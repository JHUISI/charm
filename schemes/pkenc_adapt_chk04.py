'''
Canetti-Halevi-Katz Public Key Encryption, IBE-to-PKE transform (generic composition of IBE+signature -> PKE)
 
| From: "R. Canneti, S. Halevi, J. Katz: Chosen-Ciphertext Security from Identity-Based Encryption"
| Published in: CRYPTO 2004
| Available from: http://eprint.iacr.org/2003/182
| Notes: 

* type:         encryption (public key)
* setting:      n/a --- requires a selective-ID secure IBE scheme an EU-CMA one-time signature (OTS) scheme
* assumption:   n/a --- dependent on the underlying primitives

:Authors:  Matthew Green
:Date:         1/2011
'''
from ibenc_bb03 import IBE_BB04
from pksig_bls04 import IBSig
from schemes.ibenc_adapt_identityhash import HashIDAdapter
from toolbox.PKEnc import PKEnc
from toolbox.pairinggroup import PairingGroup,GT

debug = False
class CHK04(PKEnc):
    def __init__(self, ibe_scheme, ots_scheme, groupObj):
        global ibe, ots, group
        ibe = ibe_scheme
        ots = ots_scheme
        group = groupObj
		
    def keygen(self, secparam):
        # Run the IBE Setup routine to generate (mpk, msk)
        (mpk, msk) = ibe.setup()
        
        pk = { 'mpk' : mpk, 'secparam':secparam }
        return (pk, msk)

    def encrypt(self, pk, message):
        # Generate a random keypair for the OTS
        (svk, ssk) = ots.keygen(pk['secparam'])		

        # get identity (element of ZR)
        _id = group.hash(svk['identity'])
        # print("pub identity enc =>", _id)

        # Encrypt message with the IBE scheme under 'identity' vk
        C = ibe.encrypt(pk['mpk'], _id, message)
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

def main():
    groupObj = PairingGroup('../param/a.param')
    # instantiate an Identity-Based Encryption scheme
    ibe = IBE_BB04(groupObj)
    hash_ibe = HashIDAdapter(ibe, groupObj)
   
    # instantiate an one-time signature scheme such as BLS04
    ots = IBSig(groupObj)
    
    pkenc = CHK04(hash_ibe, ots, groupObj)
    
    # not sure how to enforce secparam yet
    (pk, sk) = pkenc.keygen(0)
    
    msg = groupObj.random(GT)
    ciphertext = pkenc.encrypt(pk, msg)
    
    rec_msg = pkenc.decrypt(pk, sk, ciphertext)
    assert rec_msg == msg, "FAILED Decryption!!!"
    if debug: print("Successful Decryption!")       
        
if __name__ == "__main__":
    debug = True
    main()
     
    
