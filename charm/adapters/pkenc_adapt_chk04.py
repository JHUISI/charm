'''
Canetti-Halevi-Katz Public Key Encryption, IBE-to-PKE transform (generic composition of IBE+signature -> PKE)
 
| From: "R. Canneti, S. Halevi, J. Katz: Chosen-Ciphertext Security from Identity-Based Encryption"
| Published in: CRYPTO 2004
| Available from: http://eprint.iacr.org/2003/182
| Notes: 

* type:         encryption (public key)
* setting:      n/a --- requires a selective-ID secure IBE scheme an EU-CMA one-time signature (OTS) scheme
* assumption:   n/a --- dependent on the underlying primitives

:Authors:  J. Ayo Akinyele
:Date:         1/2011
'''
from charm.toolbox.PKEnc import *
from charm.toolbox.IBSig import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair

debug = False
class CHK04(PKEnc):
    """
    >>> from charm.adapters.ibenc_adapt_identityhash import HashIDAdapter
    >>> from charm.schemes.ibenc.ibenc_bb03 import IBE_BB04
    >>> from charm.schemes.pksig.pksig_bls04 import BLS01
    >>> group = PairingGroup('SS512')
    >>> ibe = IBE_BB04(group)
    >>> hash_ibe = HashIDAdapter(ibe, group)
    >>> ots = BLS01(group)
    >>> pkenc = CHK04(hash_ibe, ots, group)
    >>> (public_key, secret_key) = pkenc.keygen(0)
    >>> msg = group.random(GT)
    >>> cipher_text = pkenc.encrypt(public_key, msg)
    >>> decrypted_msg = pkenc.decrypt(public_key, secret_key, cipher_text)
    >>> decrypted_msg == msg
    True
    """
    def __init__(self, ibe_scheme, ots_scheme, groupObj):
        PKEnc.__init__(self)
        global ibe, ots, group
        criteria1 = [('secDef', 'IND_ID_CPA'), ('scheme', 'IBEnc'), ('id', str)]
        criteria2 = [('secDef', 'EU_CMA'), ('scheme', 'IBSig')] 
        if PKEnc.checkProperty(self, ibe_scheme, criteria1): # and PKEnc.checkProperty(self, ots_scheme, criteria2):
            PKEnc.updateProperty(self, ibe_scheme, secDef=IND_CCA, secModel=SM)
            ibe = ibe_scheme
            ots = ots_scheme
            #PKEnc.printProperties(self)
        else:
            assert False, "Input scheme does not satisfy adapter properties: %s" % criteria

        group = groupObj
		
    def keygen(self, secparam):
        # Run the IBE Setup routine to generate (mpk, msk)
        (mpk, msk) = ibe.setup()
        
        pk = { 'mpk' : mpk, 'secparam':secparam }
        return (pk, msk)

    def encrypt(self, pk, message):
        # Generate a random keypair for the OTS
        (svk, ssk) = ots.keygen(pk['secparam'])		

        # print("pub identity enc =>", _id)

        # Encrypt message with the IBE scheme under 'identity' vk
        C = ibe.encrypt(pk['mpk'],svk['identity'] , message)
        # Sign the resulting ciphertext with sk
        sigma = ots.sign(ssk['x'], C)
        return { 'vk' : svk, 'C' : C, 'sigma' : sigma }
		
    # NOTE: need to transform c['vk'] into a string to use as key        
    def decrypt(self, pk, sk, c):
        # Given a ciphertext (vk, C, sigma), verify that sigma is a signature on C under public key vk
        if not ots.verify(c['vk'], c['sigma'], c['C']):
            return False

        identity = c['vk']['identity']
        # print("identity in dec =>", identity)
        # Otherwise, extract an IBE key for identity 'vk' under the master secret params
        dk = ibe.extract(sk, identity)
        # Return the decryption of the ciphertext element "C" under key dk
        return ibe.decrypt(pk, dk, c['C'])

