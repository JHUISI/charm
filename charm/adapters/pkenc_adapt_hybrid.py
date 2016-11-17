'''Takes an public-key encryption scheme and builds a hybrid encryption scheme.'''

# Works for ElGamal and CS98 schemes
from charm.toolbox.PKEnc import PKEnc
from charm.toolbox.securerandom import OpenSSLRand
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.toolbox.ecgroup import ECGroup
from charm.toolbox.eccurve import prime192v1
from charm.schemes.pkenc.pkenc_cs98 import CS98
from charm.core.crypto.cryptobase import AES
debug = False

# Adapter class for Hybrid Encryption Schemes
class HybridEnc(PKEnc):
    """
    >>> groupObj = ECGroup(prime192v1)
    >>> pkenc = CS98(groupObj)
    >>> hyenc = HybridEnc(pkenc, msg_len=groupObj.bitsize())
    >>> (public_key, secret_key) = hyenc.keygen()
    >>> msg = b'this is a new message'
    >>> cipher_text = hyenc.encrypt(public_key, msg)
    >>> decrypted_msg = hyenc.decrypt(public_key, secret_key, cipher_text)
    >>> decrypted_msg == msg
    True
    """
    def __init__(self, pkenc, msg_len=16, key_len=16, mode=AES):
        PKEnc.__init__(self)
        # check that pkenc satisfies properties of a pkenc scheme
        if hasattr(pkenc, 'keygen') and hasattr(pkenc, 'encrypt') and hasattr(pkenc, 'decrypt'):
            self.pkenc = pkenc
            self.key_len = key_len # 128-bit session key by default
            self.msg_len = msg_len
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
        key = OpenSSLRand().getRandomBytes(self.msg_len)
        # encrypt session key using PKEnc
        c1 = self.pkenc.encrypt(pk, key)
        # use symmetric key encryption to enc actual message
        c2 = AuthenticatedCryptoAbstraction(key).encrypt(M)
        if debug: print("Ciphertext...")
        if debug: print(c2)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, pk, sk, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = self.pkenc.decrypt(pk, sk, c1)[:self.key_len]
        if debug: print("Rec key =>", key, ", len =", len(key))
        msg = AuthenticatedCryptoAbstraction(key).decrypt(c2)
        if debug: print("Rec msg =>", msg)
        return msg
    
def main():
    groupObj = ECGroup(prime192v1)
    pkenc = CS98(groupObj)
    hyenc = HybridEnc(pkenc)
       
    (pk, sk) = hyenc.keygen()
       
    m = b'this is a new message'

    cipher = hyenc.encrypt(pk, m)
    orig_m = hyenc.decrypt(pk, sk, cipher)
    assert m == orig_m, "Failed Decryption"
    if debug: print("Successful Decryption!!")

if __name__ == "__main__":
   debug = True
   main()
