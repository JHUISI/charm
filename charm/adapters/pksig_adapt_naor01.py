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
from charm.toolbox.PKSig import PKSig

debug = False
class Sig_Generic_ibetosig_Naor01(PKSig):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup,ZR
    >>> from charm.schemes.ibenc.ibenc_bb03 import IBE_BB04
    >>> group = PairingGroup('MNT224')
    >>> ibe = IBE_BB04(group)
    >>> ibsig = Sig_Generic_ibetosig_Naor01(ibe, group)
    >>> (master_public_key, master_secret_key) = ibsig.keygen()
    >>> msg = group.random(ZR)
    >>> signature = ibsig.sign(master_secret_key, msg)
    >>> ibsig.verify(master_public_key, msg, signature) 
    True
    """
    #TODO msg must be in Zp
    def __init__(self, ibe_scheme, groupObj):
        global ibe, group
        ibe = ibe_scheme
        group = groupObj
				
    def keygen(self, secparam=None):
        (mpk, msk) = ibe.setup(secparam)
        if debug: print("Keygen...")
        group.debug(mpk)
        group.debug(msk)
        return (mpk, msk)

    def sign(self, sk, message):
        return ibe.extract(sk, message)
		
    #TODO: this method does NOT validate the message it is given
    def verify(self, pk, m, sig):
        # Some IBE scheme support a native method for validating IBE keys.  Use this if it exists.
        if hasattr(ibe, 'verify'):
            result = ibe.verify(pk, sig)
            if result == False: return False
		
        # Encrypt a random message in the IBE's message space and try to decrypt it
        message = group.random(GT)
        if debug: print("\nRandom message =>", message)

        C = ibe.encrypt(pk, sig['id'], message)
         
        if (ibe.decrypt(pk, sig, C) == message):
            return True
        else:
            return False


