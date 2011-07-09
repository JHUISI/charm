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
from toolbox.PKSig import *
from toolbox.paddingschemes import *
from toolbox.conversion import Conversion

debug = True
class RSA():
    def __init__(self):
        self.rand = init()
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
        print("D:", d)
        pk = { 'N':N, 'e':e }
        sk = { 'phi_N':phi_N, 'd':d , 'N':N}
        return (pk, sk)

class RSA_Enc(RSA,PKEnc):
    def __init__(self, padding=OAEPEncryptionPadding()):
        RSA.__init__(self)
        PKEnc.__init__(self)
        self.paddingscheme = padding 
    
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
    
class RSA_Sig(RSA, PKSig):
    '''RSASSA-PSS'''
    def __init__(self, padding=PSSPadding()):
        RSA.__init__(self)
        PKSig.__init__(self)
        self.paddingscheme = padding 

    def sign(self,sk, M, salt=None):
        #apply encoding
        k = math.ceil(int(sk['N']).bit_length() / 8)
        emLen = math.ceil((int(sk['N']).bit_length() -1) / 8)
        print("emLen =>", emLen)
        em = self.paddingscheme.encode(M, emLen, salt)
        m = Conversion.OS2IP(em)
        m = integer(m) % sk['N']  #ERRROR m is larger than N
        s =  (m ** sk['d']) % sk['N']
        S = Conversion.IP2OS(s, k)
        if debug:
            print("Signing")
            print("k     =>", k)
            print("emLen =>", emLen) 
            print("m     =>", m)
            print("em    =>", em)
            print("s     =>", s)
            print("S     =>", S)
        return S
    
    def verify(self, pk, M, S):
        k = math.ceil(int(pk['N']).bit_length() / 8)
        emLen = math.ceil((int(pk['N']).bit_length() -1) / 8)
        if len(S) != k:
            if debug: print("Sig is %s octets long, not %" %(len(S), k))
            return False
        s = Conversion.OS2IP(S)
        s = integer(s) % pk['N']  #Convert to modular integer
        m = (s ** pk['e']) % pk['N']
        EM = Conversion.IP2OS(m, emLen)
        if debug:
            print("Verifying")
            print("k     =>", k)
            print("emLen =>", emLen)
            print("s     =>", s)
            print("m       =>", m)
            print("em      =>", EM)
#            print("bin_em  =>", bin(EM))
            print("S     =>", S)
        return self.paddingscheme.verify(M, EM)
        
    
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
    
def main2(): # NEEDS DEBUGGING
    M = b'This is a test message.'
    rsa = RSA_Sig()
    (pk, sk) = rsa.keygen(1024)
    S = rsa.sign(sk, M)
    assert rsa.verify(pk, M, S)
        
if __name__ == "__main__":
    debug = True
    main2()
