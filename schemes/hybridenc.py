# Takes an public-key encryption scheme and builds a hybrid encryption scheme.

import random
# Works for ElGamal and CS98 schemes
from ec_cs98_enc import *
from elgamal import *
from toolbox.PKEnc import *
from charm.cryptobase import *
from math import ceil
from string import *

# Adapter class for Hybrid Encryption Schemes
class HybridEnc(PKEnc):
    def __init__(self, pkenc, key_len=16, mode=AES): 
        PKEnc.__init__(self)
        # check that pkenc satisfies properties of a pkenc scheme
        if hasattr(pkenc, 'keygen') and hasattr(pkenc, 'encrypt') and hasattr(pkenc, 'decrypt'):
            self.pkenc = pkenc
            self.key_len = key_len # 128-bit session key by default
            self.alg = mode
            print("PKEnc satisfied.")
    
    def keygen(self, secparam=None):
        if secparam == None:
           # ec module group
           return self.pkenc.keygen()
        # integer group
        return self.pkenc.keygen(secparam)
    
    def encrypt(self, pk, M):
        # generate a short session key, K and encrypt using pkenc
        key = self.randomBits()
        # encrypt session key using PKEnc
        c1 = self.pkenc.encrypt(pk, key)
        # use symmetric key encryption to enc actual message
        prp = selectPRP(self.alg, (key, MODE_ECB))
        c2 = prp.encrypt(self.pad(M))
        print("Ciphertext 2...")
        print(c2)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, pk, sk, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = pkenc.decrypt(pk, sk, c1)[:self.key_len]
        print("Rec key =>", key,", len =", len(key))
        prp = selectPRP(self.alg, (key, MODE_ECB))
        msg = prp.decrypt(c2)
        print("Rec msg =>", msg)
        return msg.decode('utf8').strip('\x00')
    
    def pad(self, message):
        # calculate the ceiling of
        msg_len = ceil(len(message) / self.key_len) * self.key_len 
        extra = msg_len - len(message)
        # append 'extra' bytes to message
        for i in range(0, extra):
            message += '\x00'
        return message
    
    def randomBits(self):
        bits = random.sample(printable, self.key_len)
        rand = ""
        for i in bits:
            rand += i
        return rand

if __name__ == "__main__":
    pkenc = EC_CS98(409)
#    pkenc = ElGamal('ecc', 409)
    hyenc = HybridEnc(pkenc)
   
    (pk, sk) = hyenc.keygen()
   
    m = 'this is a new message'
    cipher = hyenc.encrypt(pk, m)
    orig_m = hyenc.decrypt(pk, sk, cipher)
   
    if m == orig_m:
        print("Successful Decryption!!")
    else:
        print("FAILED Decryption!!!")
