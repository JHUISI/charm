'''
Generates a Blum-Williams integer, which is the product of two distinct primes
each congruent to 3 mod 4
'''

from charm.core.math.integer import integer,isPrime,randomPrime

class BlumWilliamsInteger:
    def __init__(self):
        pass

    def generatePrimes(self, n):
        while True:
            p = randomPrime(n)
            if(isPrime(p) and (((p-3)%4) == 0)):
                break

        while True:
            q = randomPrime(n)
            if(isPrime(q) and (((q-3)%4) == 0) and not(q == p)):
                break

        return (p, q)

    def generateBlumWilliamsInteger(self, n, p=0, q=0):
        if((p == 0) or (q == 0)):
            (p,q) = self.generatePrimes(n)
            N = p * q
            return (p, q, N)
        else:
            N = p * q
            return N
