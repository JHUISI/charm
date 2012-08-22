from charm.toolbox.PKSig import PKSig
from charm.core.math.integer import integer,isPrime,random,randomPrime,randomBits
import hashlib

def SHA1(bytes1):
    s1 = hashlib.new('sha1')
    s1.update(bytes1)
    return s1.digest()

def randomQR(n):
    return random(n) ** 2

debug=False
class Sig_CL03(PKSig):
    """
    >>> pksig = Sig_CL03() 
    >>> p = integer(21281327767482252741932894893985715222965623124768085901716557791820905647984944443933101657552322341359898014680608292582311911954091137905079983298534519)
    >>> q = integer(25806791860198780216123533220157510131833627659100364815258741328806284055493647951841418122944864389129382151632630375439181728665686745203837140362092027)
    >>> (public_key, secret_key) = pksig.keygen(1024, p, q)
    >>> msg = integer(SHA1(b'This is the message I want to hash.'))
    >>> signature = pksig.sign(public_key, secret_key, msg)
    >>> pksig.verify(public_key, msg, signature)
    True
    """
    def __init__(self, lmin=160, lin=160, secparam=512):
        global ln, lm, le, l
        ln = 2 * secparam
        lm = lmin
        le = lm + 2
        l = lin
        
    def keygen(self, secparam=512, p=0, q=0):
        if(p == 0):
            pprime = randomPrime(secparam)
            while(not isPrime(2*pprime + 1)):
                pprime = randomPrime(secparam)
            p = 2 * pprime + 1
            print(p)

        if(q == 0):
            qprime = randomPrime(secparam)
            while(not isPrime(2*qprime + 1)):
                qprime = randomPrime(secparam)
            q = 2 * qprime + 1
            print(q)

        N = p * q

        a = randomQR(N)
        b = randomQR(N)
        c = randomQR(N)

        pk = { 'N':N, 'a':a, 'b':b, 'c':c }
        sk = { 'p':p, 'q':q }

        return (pk, sk)
    
    def sign(self, pk, sk, m):
        e = randomPrime(le)

        ls = ln + lm + l
        s = integer(randomBits(ls))

        phi_N = (sk['p']-1)*(sk['q']-1)
        e2 = e % phi_N
    
        v = (((pk['a'] ** m)*(pk['b'] ** s)*pk['c']) ** (e2 ** -1)) % pk['N']

        sig = { 'e':e, 's':s, 'v':v }

        return sig

    def signCommit(self, pk, sk, Cx):
        e = randomPrime(le)

        ls = ln + lm + l
        rprime = integer(randomBits(ls))

        phi_N = (sk['p']-1)*(sk['q']-1)
        e2 = e % phi_N
    
        v = (((Cx)*(pk['b'] ** rprime)*pk['c']) ** (e2 ** -1)) % pk['N']

        sig = { 'e':e, 'rprime':rprime, 'v':v }

        return sig

    def verify(self, pk, m, sig):
        if debug: print("\nVERIFY\n\n")

        lhs = (sig['v'] ** sig['e']) % pk['N']
        rhs = ((pk['a'] ** m)*(pk['b'] ** sig['s'])*pk['c']) % pk['N']

        #do size check on e

        if(lhs == rhs):
            return True

        return False



