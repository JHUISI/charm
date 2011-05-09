# From: "Rivest-Shamir-Adleman Standard algorithm".
# Published in: 1978
# Security Assumption: RSA factoring

# type:           public-key encryption
# setting:        Integer
#
# Implementer:    J Ayo Akinyele
# Date:            05/2011

from charm.integer import *
from PKEnc import *

class RSA(PKEnc):
    def __init__(self):
        self.rand = init()
        global encode, decode
        encode, decode = self.encode, self.decode
                
    # generate p,q and n
    def paramgen(self, secparam):
        while True:
           p, q = self.rand.randomPrime(secparam), self.rand.randomPrime(secparam)
           if isPrime(p) and isPrime(q):
              N = p * q
              phi_N = (p - 1) * (q - 1)
              break
        return (p, q, N, phi_N)
        
    def keygen(self, secparam=1024):
        (p, q, N, phi_N) = self.paramgen(secparam)
        
        while True:
            e = self.rand.random(phi_N) # or use 65537 for testing
            if not gcd(e, phi_N) == 1:
                continue
            d = e ** -1
            break
        pk = { 'N':N, 'e':e }
        sk = { 'phi_N':phi_N, 'd':d }
        return (pk, sk)
    
    def encrypt(self, pk, m):
        M = encode(m, pk['N'])
        return (m ** pk['e']) % pk['N']
    
    def decrypt(self, pk, sk, c):
        M = (c ** (sk['d'] % sk['phi_N'])) % pk['N']
        return decode(M, pk['N'])
    
    def encode(self, m, n):
        # apply padding scheme to encode message s.t. (0 < m < N).
        # add padding routine here to encode message as integer
        return m % n
    
    def decode(self, m, n):
        # add padding routine here to recover message
        return m % n
        
if __name__ == "__main__":
    rsa = RSA()
    
    (pk, sk) = rsa.keygen(1024)
    
    m = integer(34567890981234556498) % pk['N']
    c = rsa.encrypt(pk, m)
    
    orig_m = rsa.decrypt(pk, sk, c)
    print("recovered m =>", orig_m)

    if m == orig_m:
        print("Successful Decryption!!!")
    else:
        print("FAILED Decryption!")
