'''
Naor's generic IBE-to-Signature transform (generic composition)
 
| From: "B. Franklin, M. Franklin: Identity-based encryption from the Weil pairing"
| Published in: Eurocrypt 2009
| Available from: http://eprint.iacr.org/2009/028.pdf
 
Notes:	This transform was first described by Boneh and Franklin but credited to Moni Naor.  It
   converts any fully-secure IBE sheme into a signature by repurposing the identity key extraction
   as a signing algorithm.  To verify, encrypt a random value under the message/identity,
   and attempt to decrypt it using the signature/key.  It may be necessary to repeat this process,
   depending on the size of the IBE's plaintext space.  Some IBE schemes support a more efficient
   algorithm for verifying the structure of an identity key --- we will use it if it's available. 
   *Warning*: this transform is not secure for selectively-secure schemes!

* type:			signature (public key)
* setting:		n/a (any fully-secure IBE scheme)
* assumption:	n/a (dependent on the IBE scheme)

:Authors:	J. Ayo Akinyele
:Date:		05/2011
'''

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.IBEnc import *
from charm.toolbox.PKSig import *

debug = False
class Sig_Generic_ibetosig_Naor01(PKSig):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup,ZR
    >>> from charm.schemes.ibenc.ibenc_bb03 import IBE_BB04
    >>> from charm.adapters.ibenc_adapt_identityhash import HashIDAdapter
    >>> group = PairingGroup('MNT224')
    >>> ibe = IBE_BB04(group)
    >>> hashID = HashIDAdapter(ibe, group)    
    >>> ibsig = Sig_Generic_ibetosig_Naor01(hashID, group)
    >>> (master_public_key, master_secret_key) = ibsig.keygen()
    >>> msg = b"hello world!!!"
    >>> signature = ibsig.sign(master_secret_key, msg)
    >>> ibsig.verify(master_public_key, msg, signature) 
    True
    """
    def __init__(self, ibe_scheme, groupObj):
        PKSig.__init__(self)
        global ibe, group
        # validate that we have the appropriate object
        criteria = [('secDef', IND_ID_CPA), ('scheme', 'IBEnc'), ('messageSpace', GT)]
        if PKSig.checkProperty(self, ibe_scheme, criteria):
            # change our property as well
            PKSig.updateProperty(self, ibe_scheme, secDef=EU_CMA, id=str, secModel=ROM)
            ibe = ibe_scheme
            #PKSig.printProperties(self)
        else:
            assert False, "Input scheme does not satisfy adapter properties: %s" % criteria        
        group = groupObj
				
    def keygen(self):
        (mpk, msk) = ibe.setup()
        if debug: print("Keygen...")
        group.debug(mpk)
        group.debug(msk)
        return (mpk, msk)

    def sign(self, sk, m):
        assert type(m) in [str, bytes], "invalid message type!"
        return ibe.extract(sk, m)
		
    def verify(self, pk, m, sig):
        # Some IBE scheme support a native method for validating IBE keys.  Use this if it exists.
        if hasattr(ibe, 'verify'):
            result = ibe.verify(pk, m, sig)
            if result == False: return False
		
        assert m == sig['IDstr'], "message not thesame as ID in signature"
        # Encrypt a random message in the IBE's message space and try to decrypt it
        new_m = group.random(GT)
        if debug: print("\nRandom message =>", new_m)

        C = ibe.encrypt(pk, sig['IDstr'], new_m)
         
        if (ibe.decrypt(pk, sig, C) == new_m):
            return True
        else:
            return False


