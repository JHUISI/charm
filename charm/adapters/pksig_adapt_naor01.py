'''
**Naor's IBE-to-Signature Transform (Naor01)**

*Description:* Transforms a fully-secure Identity-Based Encryption scheme into a
digital signature scheme using Naor's construction.

| **Based on:** Identity-Based Encryption from the Weil Pairing
| **Published in:** CRYPTO 2001
| **Available from:** https://eprint.iacr.org/2001/090.pdf
| **Notes:** First described by Boneh and Franklin, credited to Moni Naor.
| Uses IBE key extraction as signing; verification via encrypt-then-decrypt.
| **Warning:** Not secure for selectively-secure IBE schemes!

.. rubric:: Adapter Properties

* **Type:** IBE-to-signature transform
* **Underlying Scheme:** any fully-secure IBE scheme
* **Purpose:** constructs digital signatures from Identity-Based Encryption

.. rubric:: Implementation

:Authors: J. Ayo Akinyele
:Date: 05/2011
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


