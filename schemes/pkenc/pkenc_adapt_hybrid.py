'''Takes an public-key encryption scheme and builds a hybrid encryption scheme.'''

import random, string
# Works for ElGamal and CS98 schemes
#from ec_cs98_enc import *
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.toolbox.eccurve import prime192v1
from charm.schemes.pkenc.pkenc_elgamal85 import *
from charm.toolbox.PKEnc import PKEnc
from charm.core.crypto.cryptobase import *
from math import ceil
from os import urandom
import base64
debug = False
# Adapter class for Hybrid Encryption Schemes
class HybridEnc(PKEnc):
    def __init__(self, pkenc, key_len=16, mode=AES): 
        PKEnc.__init__(self)
        # check that pkenc satisfies properties of a pkenc scheme
        if hasattr(pkenc, 'keygen') and hasattr(pkenc, 'encrypt') and hasattr(pkenc, 'decrypt'):
            self.pkenc = pkenc
            self.key_len = key_len # 128-bit session key by default
            self.alg = mode
            if debug: print("PKEnc satisfied.")
    
    def keygen(self, secparam=None):
        if secparam == None:
           # ec module group
           return self.pkenc.keygen()
        # integer group
        return self.pkenc.keygen(secparam)
    
    def encrypt(self, pk, M):
        # generate a short session key, K and encrypt using pkenc
        key = urandom(self.key_len)
        # encrypt session key using PKEnc
        c1 = self.pkenc.encrypt(pk, key)
        # use symmetric key encryption to enc actual message
        cipher = AuthenticatedCryptoAbstraction(key)
        c2 = cipher.encrypt(M)
        if debug: print("Ciphertext 2...")
        if debug: print(c2)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, pk, sk, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = self.pkenc.decrypt(pk, sk, c1)[:self.key_len]
        if debug: print("Rec key =>", key,", len =", len(key))
        cipher = AuthenticatedCryptoAbstraction(key)
        msg = cipher.decrypt(c2)
        if debug: print("Rec msg =>", msg)
        return msg
    
def main():
    #    pkenc = EC_CS98(prime192v1)
    pkenc = ElGamal(ecc, prime192v1)
    hyenc = HybridEnc(pkenc)
   
    (pk, sk) = hyenc.keygen()
   
    m = 'this is a new message'
    cipher = hyenc.encrypt(pk, m)
    orig_m = hyenc.decrypt(pk, sk, cipher)
    assert m == orig_m, "Failed Decryption"
    if debug: print("Successful Decryption!!")

if __name__ == "__main__":
    debug = True
    main()
