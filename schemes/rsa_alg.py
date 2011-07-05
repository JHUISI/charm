# From: "Rivest-Shamir-Adleman Standard algorithm".
# Published in: 1978
# Security Assumption: RSA factoring

# type:           public-key encryption
# setting:        Integer
#
# Implementer:    J Ayo Akinyele
# Date:            05/2011

from charm.integer import *
from toolbox.PKEnc import *
from toolbox.paddingschemes import *
from toolbox.conversion import Conversion

debug = False
class RSA_Enc(PKEnc):
    def __init__(self, padding=OAEPEncryptionPadding()):
        self.rand = init()
        self.paddingscheme = padding 
                
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
    
    def encrypt(self, pk, m:Bytes):
        octetlen = math.ceil(int(pk['N']).bit_length() / 8)
        EM = self.paddingscheme.encode(m, octetlen)
        if debug: print("EM == >", EM)
        i = Conversion.OS2IP(EM)
        ip = integer(i) % pk['N']  #Convert to modular integer
        return (ip ** pk['e']) % pk['N']
    
    def decrypt(self, pk, sk, c):
        octetlen = math.ceil(int(pk['N']).bit_length() / 8)
        M = (c ** (sk['d'] % sk['phi_N'])) % pk['N']
        os = Conversion.IP2OS(int(M), octetlen)
        if debug: print("OS  =>", os)
        return self.paddingscheme.decode(os)
    
class RSA_Sig():
    pass

def main():
    rsa = RSA_Enc()
    
    (pk, sk) = rsa.keygen(1024)
    
    #m = integer(34567890981234556498) % pk['N']
    m = b'This is a test'
    c = rsa.encrypt(pk, m)
    
    orig_m = rsa.decrypt(pk, sk, c)
    if debug: print("recovered m =>", orig_m)

    assert m == orig_m
    if debug: print("Successful Decryption!!!")
        
if __name__ == "__main__":
    debug = True
    main()
