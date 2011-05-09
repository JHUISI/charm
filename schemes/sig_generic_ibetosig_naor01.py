# Naor's generic IBE-to-Signature transform (generic composition)
# 
# From: "B. Franklin, M. Franklin: Identity-based encryption from the Weil pairing"
# Published in: Eurocrypt 2009
# Available from: http://eprint.iacr.org/2009/028.pdf
# Notes:	This transform was first described by Boneh and Franklin but credited to Moni Naor.  It
#			converts any fully-secure IBE sheme into a signature by repurposing the identity key extraction
#			as a signing algorithm.  To verify, encrypt a random value under the message/identity,
#			and attempt to decrypt it using the signature/key.  It may be necessary to repeat this process,
#			depending on the size of the IBE's plaintext space.  Some IBE schemes support a more efficient
#			algorithm for verifying the structure of an identity key --- we will use it if it's available. 
#			Warning: this transform is not secure for selectively-secure schemes!
#
# type:			signature (public key)
# setting:		n/a (any fully-secure IBE scheme)
# assumption:	n/a (dependent on the IBE scheme)
#
# Implementer:	Matthew Green
# Date:			05/2011

from pairinggroup import *
from enc_bm_ibe_bb03 import *
from PKSig import *

class Sig_Generic_ibetosig_Naor01(PKSig):
    def __init__(self, ibe_scheme, groupObj):
        global ibe, group
        ibe = ibe_scheme
        group = groupObj
				
    def keygen(self, secparam=None):
        (mpk, msk) = ibe.setup(secparam)
#        pk = { 'mpk' : mpk, 'secparam':secparam }
        print("Keygen...")
        group.debug(mpk)
        group.debug(msk)
        return (mpk, msk)

    def sign(self, sk, message):
        return ibe.extract(sk, message)
		
    def verify(self, pk, m, sig):
        # Some IBE scheme support a native method for validating IBE keys.  Use this if it exists.
        if hasattr(ibe, 'verify'):
            result = ibe.verify(pk, sig)
            if result == False: return False
		
        # TODO: get the plaintext space, find its entropy, and repeat the following test
        # enough times to reduce the probability of coincidence to 1/securityparam
		
        # Encrypt a random message in the IBE's message space and try to decrypt it
        message = group.random(GT)
        print("\nRandom message =>", message)
        # pk = pub params, sig['id'] == m == identity, and message (GT)
        C = ibe.encrypt(pk, sig['id'], message) 
        # treat 'sig' as the key to decrypt the random message
        # if successful then, the message has a valid signature, sigma
        if (ibe.decrypt(sig, C) == message):
            return True
        else:
            return False

if __name__ == "__main__":
    groupObj = PairingGroup('library/d224.param')
    
    ibe = IBE(groupObj)
    
    ibsig = Sig_Generic_ibetosig_Naor01(ibe, groupObj)

    (mpk, msk) = ibsig.keygen()
    
    M = "I want a signature on this message!"
    
    sigma = ibsig.sign(msk, M)
    print("\nMessage =>", M)
    print("Sigma =>", sigma)
    
    result = ibsig.verify(mpk, M, sigma)
    if result:
        print("Successful Verification!!!")
    else:
        print("FAILED Verification!")
    
    