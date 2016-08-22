'''
 A Signature Scheme with Efficient Protocols
 
| From: "J. Camenisch, A. Lysyanskaya."
| Published in: 2003
| Available from: http://cs.brown.edu/~anna/papers/camlys02b.pdf 
| Notes: Schemes 2.2 (on page 4) and 4 (on page 8). 

* type:           signature
* setting:        integer groups 

:Authors:    Christina Garman/Antonio de la Piedra
:Date:       11/2013
 '''
from charm.toolbox.PKSig import PKSig
from charm.core.math.integer import integer,isPrime,random,randomPrime,randomBits
import hashlib

def SHA1(bytes1):
    s1 = hashlib.new('sha256')
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
    >>> from charm.toolbox.conversion import Conversion
    >>> g  = {}
    >>> m = {}
    >>> j = 16
    >>> for i in range(1, j + 1): g[str(i)] = randomQR(public_key['N'])
    >>> for i in range(1, j + 1): m[str(i)] = integer(SHA1(Conversion.IP2OS(random(public_key['N']))))
    >>> Cx = 1 % public_key['N']
    >>> for i in range(1, len(m) + 1): Cx = Cx*(g[str(i)] ** m[str(i)])
    >>> pksig = Sig_CL03() 
    >>> p = integer(21281327767482252741932894893985715222965623124768085901716557791820905647984944443933101657552322341359898014680608292582311911954091137905079983298534519)
    >>> q = integer(25806791860198780216123533220157510131833627659100364815258741328806284055493647951841418122944864389129382151632630375439181728665686745203837140362092027)
    >>> (public_key, secret_key) = pksig.keygen(1024, p, q)
    >>> signature = pksig.signCommit(public_key, secret_key, Cx)
    >>> pksig.verifyCommit(public_key, signature, Cx)
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
        
        if (sig['e'] <= 2**(le - 1) or sig['e'] >= 2**(le)):
            return False

        if(lhs == rhs):
            return True

        return False

    def verifyCommit(self, pk, sig, Cx):
        if debug: print("\nVERIFY\n\n")

        lhs = (sig['v'] ** sig['e']) % pk['N']
        rhs = (Cx*(pk['b'] ** sig['rprime'])*pk['c']) % pk['N']

        if (sig['e'] <= 2**(le - 1)):
            return False

        if(lhs == rhs):
            return True

        return False
