'''
| From: "Rivest-Shamir-Adleman Standard algorithm".
| Published in: 1978
| Security Assumption: RSA factoring

* type:           public-key encryption
* setting:        Integer

:Authors: J Ayo Akinyele, Gary Belvin
:Date:            07/2011
'''

from charm.core.math.integer import integer,isPrime,gcd,random,randomPrime,toInt
from charm.toolbox.PKEnc import PKEnc
from charm.toolbox.PKSig import PKSig
from charm.toolbox.paddingschemes import OAEPEncryptionPadding,PSSPadding
from charm.toolbox.conversion import Conversion
from math import ceil

debug = False
class RSA():
    def __init__(self):
        pass
    # generate p,q and n
    def paramgen(self, secparam):
        while True:
            p, q = randomPrime(secparam), randomPrime(secparam)
            if isPrime(p) and isPrime(q) and p != q:
                N = p * q
                phi_N = (p - 1) * (q - 1)
                break
        return (p, q, N, phi_N)
    
    def keygen(self, secparam=1024, params=None):
        if params: 
            (N, e, d, p, q) = self.convert(params)
            phi_N = (p - 1) * (q - 1)
            pk = { 'N':N, 'e':e }
            sk = { 'phi_N':phi_N, 'd':d , 'N':N}
            return (pk, sk)

        (p, q, N, phi_N) = self.paramgen(secparam)
        
        while True:
            e = random(phi_N)
            if not gcd(e, phi_N) == 1:
                continue
            d = e ** -1
            break
        pk = { 'N':N, 'e':toInt(e) } # strip off \phi
        sk = { 'phi_N':phi_N, 'd':d , 'N':N}

        return (pk, sk)
    
    def convert(self, N, e, d, p, q):
        return (integer(N), integer(e), integer(d), 
                integer(p), integer(q))
    
class RSA_Enc(RSA,PKEnc):
    """
    >>> rsa = RSA_Enc()
    >>> (public_key, secret_key) = rsa.keygen(1024)
    >>> msg = b'This is a test'
    >>> cipher_text = rsa.encrypt(public_key, msg)
    >>> decrypted_msg = rsa.decrypt(public_key, secret_key, cipher_text)
    >>> decrypted_msg == msg
    True
    """
    def __init__(self, padding=OAEPEncryptionPadding(), params=None):
        RSA.__init__(self)
        PKEnc.__init__(self)
        self.paddingscheme = padding 
    # m : Bytes
    def encrypt(self, pk, m, salt=None):
        octetlen = int(ceil(int(pk['N']).bit_length() / 8.0))
        EM = self.paddingscheme.encode(m, octetlen, "", salt)
        if debug: print("EM == >", EM)
        i = Conversion.OS2IP(EM)
        ip = integer(i) % pk['N']  #Convert to modular integer
        return (ip ** pk['e']) % pk['N']
    
    def decrypt(self, pk, sk, c):
        octetlen = int(ceil(int(pk['N']).bit_length() / 8.0))
        M = (c ** (sk['d'] % sk['phi_N'])) % pk['N']
        os = Conversion.IP2OS(int(M), octetlen)
        if debug: print("OS  =>", os)
        return self.paddingscheme.decode(os)
    
class RSA_Sig(RSA, PKSig):
    """
    >>> msg = b'This is a test message.'
    >>> rsa = RSA_Sig()
    >>> (public_key, secret_key) = rsa.keygen(1024)
    >>> signature = rsa.sign(secret_key, msg)
    >>> rsa.verify(public_key, msg, signature)
    True
    """
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
        
    
    
