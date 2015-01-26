'''
Goldwasser-Micali Public Key Encryption Scheme (Quadratic Residuosity problem)


| From: "S. Goldwasser, S. Micali: Probabilistic encryption and how to play
|        mental poker keeping secret all partial information"
| Published in: 14th Symposium on Theory of Computing (1982)
| Available from: http://groups.csail.mit.edu/cis/pubs/shafi/1982-stoc.pdf
| Notes:

* type:          encryption (public key)
* setting:       Integer
* assumption:    Quadratic Residuosity

:Authors: Guillermo Ramos
:Date: 01/2015
'''

from charm.core.math.integer import legendre, gcd
from charm.toolbox.integergroup import RSAGroup, integer
from charm.toolbox.PKEnc import PKEnc

# Upper bound to the number of rounds the keygen is able to make
# to search for a quadratic non-residue
maxtimes = 30

# Is x a quadratic residue of N = p1*p2?
def isResidue(x, p1, p2):
    return legendre(x, p1) == 1 or legendre(x, p2) == 1

# Goldwasser-Micali cryptosystem
class GM82(PKEnc):
    """
    >>> gm82 = GM82()
    >>> (pk, sk) = gm82.keygen(512)
    >>> zero = gm82.encrypt(pk, 0)
    >>> one = gm82.encrypt(pk, 1)
    >>> gm82.decrypt(sk, zero)
    0
    >>> gm82.decrypt(sk, one)
    1
    >>> gm82.decrypt(sk, gm82.xor(pk, zero, zero))
    0
    >>> gm82.decrypt(sk, gm82.xor(pk, zero, one))
    1
    >>> gm82.decrypt(sk, gm82.xor(pk, one, zero))
    1
    >>> gm82.decrypt(sk, gm82.xor(pk, one, one))
    0
    """
    def __init__(self):
        PKEnc.__init__(self)
        self.group = RSAGroup()

    def keygen(self, secparam):
        self.group.paramgen(secparam)

        # Find a random quadratic non-residue in the group
        x = self.group.random()
        times = 1
        while times < maxtimes and isResidue(x, self.group.p, self.group.q):
            x = self.group.random()
            times += 1

        # If we are not able to find a quadratic non-residue after 'maxtimes'
        # trials, abort and output error
        if times == maxtimes:
            print("ERROR: non-residue not found after {} trials.".format(times))
            return None

        pk = (self.group.n, x)
        sk = (self.group.p, self.group.q)
        return (pk, sk)

    def encrypt(self, pk, m):
        (n, x) = pk

        y = self.group.random()
        while gcd(n, y) != 1:
            y = self.group.random()

        if m == 0:
            return y**2 % n
        else:
            return y**2 * x % n

    def decrypt(self, sk, c):
        (p, q) = sk
        return 0 if isResidue(c, p, q) else 1

    # Homomorphic XOR over ciphertexts
    def xor(self, pk, c1, c2):
        (n, _) = pk
        return (c1 * c2) % n
