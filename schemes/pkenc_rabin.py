'''
| From: "Digitalized Signatures and Public-Key Functions as Intractable as Factorization".
| Published in: 1979
| Security Assumption: Integer Factorization

* type:           public-key encryption
* setting:        Integer

:Authors: Christina Garman
:Date:            09/2011
'''

from charm.integer import integer,isPrime,gcd,random,randomPrime
from toolbox.PKEnc import PKEnc
from toolbox.PKSig import PKSig
from toolbox.paddingschemes import OAEPEncryptionPadding,PSSPadding
from toolbox.redundancyschemes import InMessageRedundancy
from toolbox.conversion import Conversion
from math import ceil, floor

debug = False
class Rabin():
    '''Rabin Module'''
    def __init__(self):
        pass
    # generate p,q and n
    def paramgen(self, secparam):
        while True:
            p = randomPrime(secparam)
            if isPrime(p) and (((p-3)%4) == 0):
                print("p => ",p)
                break
        while True:
            q = randomPrime(secparam)
            if isPrime(q) and (((q-3)%4) == 0) and not(q == p):
                print("q => ",q)
                break
        N = p * q
        print("N => ", N)

        yp = (p % q) ** -1
        yq = (q % p) ** -1
        print("yp => ", yp)
        print("yq => ", yq) 

        return (p, yp, q, yq, N)
    
    def keygen(self, secparam=1024, params=None):
        if params: 
            (N, p, q, yp, yq) = self.convert(params)
            pk = { 'N':N }
            sk = { 'p':p, 'q':q, 'N':N , 'yp':yp, 'yq':yq }
            return (pk, sk)

        (p, yp, q, yq, N) = self.paramgen(secparam)
        
        pk = { 'N':N }
        sk = { 'p':p, 'q':q, 'N':N , 'yp':yp, 'yq':yq }

        return (pk, sk)
    
    def convert(self, N, p, q, yp, yq):
        return (integer(N), integer(p), integer(q), integer(yp), integer(yq))
    
class Rabin_Enc(Rabin,PKEnc):
    def __init__(self, padding=OAEPEncryptionPadding(), redundancy=InMessageRedundancy(), params=None):
        Rabin.__init__(self)
        PKEnc.__init__(self)
        self.paddingscheme = padding 
        self.redundancyscheme = redundancy
    # m : Bytes
    def encrypt(self, pk, m, salt=None):
        print(m)
        print(bytes(m))
        m = self.redundancyscheme.encode(m)
        print(m)
        octetlen = int(ceil(int(pk['N']).bit_length() / 8.0))
        print(octetlen, len(m))
        EM = self.paddingscheme.encode(m, octetlen, "", salt)
        if debug: print("EM == >", EM)
        #i = Conversion.OS2IP(m)
        i = Conversion.OS2IP(EM)
        print("i => ", i, pk['N'])
        ip = integer(i) % pk['N']  #Convert to modular integer
        print((ip ** 2) % pk['N'])
        return (ip ** 2) % pk['N']
    
    def decrypt(self, pk, sk, c):
        octetlen = int(ceil(int(pk['N']).bit_length() / 8.0))

        p = sk['p']
        q = sk['q']
        yp = sk['yp']
        yq = sk['yq']

        print("p,q => ",p,q)

        print((p+1)/4,(q+1)/4)
        print("c => ", c)

        mp = (c ** ((p+1)/4)) % p
        print("mp => ", mp)
        mq = (c ** ((q+1)/4)) % q
        print("mq => ", mq)

        #can you extract just the "number" part of a modular integer???
        print("mp (int) => ", int(mp))
        print("mq (int) => ", int(mq))
        print("yp (int) => ", int(yp))
        print("yq (int) => ", int(yq))

        r1 = ((int(yp)*int(p)*int(mq)) + ((int(yq)*int(q)*int(mp)))) % int(sk['N'])
        print(type(r1))
        r2 = int(sk['N']) - int(r1)
        print("r1, r2 =>", r1, r2)

        s1 = (int(yp)*int(p)*int(mq) - int(yq)*int(q)*int(mp)) % int(sk['N'])
        s2 = int(sk['N']) - int(s1)
        print("s1, s2 =>", s1, s2)

        m1 = r1 % int(sk['N'])
        m2 = r2 % int(sk['N'])
        m3 = s1 % int(sk['N'])
        m4 = s2 % int(sk['N'])

        os1 = Conversion.IP2OS(int(m1), octetlen)
        os2 = Conversion.IP2OS(int(m2), octetlen)
        os3 = Conversion.IP2OS(int(m3), octetlen)
        os4 = Conversion.IP2OS(int(m4), octetlen)
        if debug: print("OS1  =>", os1)
        if debug: print("OS2  =>", os2)
        if debug: print("OS3  =>", os3)
        if debug: print("OS4  =>", os4)
        print("OS1 dec => ", self.paddingscheme.decode(os1))
        print("OS2 dec => ", self.paddingscheme.decode(os2))
        print("OS3 dec => ", self.paddingscheme.decode(os3))
        print("OS4 dec => ", self.paddingscheme.decode(os4))

        for i in [os1, os2, os3, os4]:
            (isMessage, message) = self.redundancyscheme.decode(self.paddingscheme.decode(i))
            if(isMessage):
               return message

        return self.paddingscheme.decode(os1)
    
class Rabin_Sig(Rabin, PKSig):
    '''RSASSA-PSS'''
    def __init__(self, padding=PSSPadding()):
        RSA.__init__(self)
        PKSig.__init__(self)
        self.paddingscheme = padding 

    def sign(self,sk, M, salt=None):
        #apply encoding
        modbits = int(sk['N']).bit_length()
        k = int(ceil(modbits / 8.0))
        emLen = int(ceil((modbits -1) / 8.0))
        
        
        em = self.paddingscheme.encode(M, modbits - 1, salt)
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
        modbits = int(pk['N']).bit_length()
        k = int(ceil(modbits / 8.0))
        emLen = int(ceil((modbits -1) / 8.0))
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
            print("S     =>", S)
        return self.paddingscheme.verify(M, EM, modbits-1)
        
    
def main():
    rabin = Rabin_Enc()
    
    (pk, sk) = rabin.keygen(1024)
    
    m = b'This is a test'
    #m = 55
    #m = b'A'
    c = rabin.encrypt(pk, m)
    if debug: print("ct =>", c)
    
    orig_m = rabin.decrypt(pk, sk, c)
    if debug: print("recovered m =>", orig_m)

    assert m == orig_m
    if debug: print("Successful Decryption!!!")
    
def main2():
    M = b'This is a test message.'
    rsa = RSA_Sig()
    (pk, sk) = rsa.keygen(1024)
    S = rsa.sign(sk, M)
    assert rsa.verify(pk, M, S)
    if debug: print("Successful Signature!")
        
if __name__ == "__main__":
    debug = True
    main()
    #main2()    
