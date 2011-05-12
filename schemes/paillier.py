# Pascal Paillier (Public-Key)
# 
# From: "Public-Key Cryptosystems Based on Composite Degree Residuosity Classes" 
# Published in: EUROCRYPT 1999
# Available from: http://eprint.iacr.org/2009/309.pdf
# Notes: 

# type:           public-key encryption (public key)
# setting:        Integer
#
# Implementer:    J Ayo Akinyele
# Date:            4/2011
from charm.integer import *
from toolbox.PKEnc import *

class Pai99(PKEnc):
    def __init__(self):
        PKEnc.__init__(self)
        self.rand = init()
    
    def paramgen(self, secparam):
        while True:
           p, q = self.rand.randomPrime(secparam), self.rand.randomPrime(secparam)
           if isPrime(p) and isPrime(q) and gcd(p * q, (p - 1) * (q - 1)) == 1:
              break
        return (p, q)    

    def L(self, u, n):
        return integer(int(u - 1)) / n
                
    def keygen(self, secparam=1024):
        (p, q) = self.paramgen(secparam)
        n = p * q
        g = n + 1
        lam = lcm(p - 1, q - 1)
        n2 = n ** 2
        u = (self.L(((g % n2) ** lam), n) % n) ** -1
        pk, sk = {'n':n, 'g':g, 'n2':n2}, {'lamda':lam, 'u':u}
        return (pk, sk)

    def encrypt(self, pk, m):
        g, n, n2 = pk['g'], pk['n'], pk['n2']
        r = self.rand.random(pk['n'])
        return ((g % n2) ** m) * ((r % n2) ** n)
    
    def decrypt(self, pk, sk, c):
        n, n2 = pk['n'], pk['n2']
        return ((self.L(c ** sk['lamda'], n) % n) * sk['u']) % n
    
    def encode(self, modulus, message):
        # takes a string and represents as a bytes object
        elem = integer(message)
        return elem % modulus
        
    def decode(self, pk, element):
        pass
    
if __name__ == "__main__":
    pai = Pai99()
    
    (pk, sk) = pai.keygen()
    
    m = pai.encode(pk['n'], 12345678987654321)
    cipher = pai.encrypt(pk, m)
    
    orig_m = pai.decrypt(pk, sk, cipher)
    
    if m == orig_m:
       print("Successful Decryption!")
    else:
       print("FAILED Decryption!!!")
    
