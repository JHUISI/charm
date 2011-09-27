'''Takes an public-key encryption scheme and builds a hybrid encryption scheme.'''

import random, string
# Works for ElGamal and CS98 schemes
#from ec_cs98_enc import *
from schemes.pkenc_elgamal85 import *
from toolbox.PKEnc import *
from charm.cryptobase import *
from math import ceil

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
        key = self.randomBits()
        # encrypt session key using PKEnc
        c1 = self.pkenc.encrypt(pk, key)
        # use symmetric key encryption to enc actual message
        iv  = '6543210987654321' # static IV (for testing)    
        prp = selectPRP(self.alg, (key, MODE_CBC, iv))
        c2 = prp.encrypt(self.pad(M))
        if debug: print("Ciphertext 2...")
        if debug: print(c2)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, pk, sk, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = self.pkenc.decrypt(pk, sk, c1)[:self.key_len]
        if debug: print("Rec key =>", key,", len =", len(key))
        iv  = '6543210987654321' # static IV (for testing)    
        prp = selectPRP(self.alg, (key, MODE_CBC, iv))
        msg = prp.decrypt(c2)
        if debug: print("Rec msg =>", msg)
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
        bits = random.sample(string.printable, self.key_len)
        rand = ""
        for i in bits:
            rand += i
        return rand

def main():
    #    pkenc = EC_CS98(409)
    pkenc = ElGamal(ecc, 409)
    hyenc = HybridEnc(pkenc)
   
    (pk, sk) = hyenc.keygen()
   
    m = 'this is a new message'
    cipher = hyenc.encrypt(pk, m)
    orig_m = hyenc.decrypt(pk, sk, cipher)
   
    assert m == orig_m
    if debug: print("Successful Decryption!!")

if __name__ == "__main__":
    debug = True
    main()
