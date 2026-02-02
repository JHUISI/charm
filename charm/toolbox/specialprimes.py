'''
Generates a Blum-Williams integer, which is the product of two distinct primes
each congruent to 3 mod 4
'''

from charm.core.math.integer import integer,isPrime,randomPrime

class BlumWilliamsInteger:
    def __init__(self):
        pass

    def generatePrimes(self, n):
        # Add safety limit to prevent infinite loops on Python 3.12+
        # Blum-Williams primes (p ≡ 3 mod 4) are approximately 50% of all primes
        # so we should find one within a reasonable number of attempts
        max_attempts = 10000

        for attempt in range(max_attempts):
            p = randomPrime(n)
            if(isPrime(p) and (((p-3)%4) == 0)):
                break
        else:
            raise RuntimeError(
                f"Could not generate Blum-Williams prime p after {max_attempts} attempts"
            )

        for attempt in range(max_attempts):
            q = randomPrime(n)
            if(isPrime(q) and (((q-3)%4) == 0) and not(q == p)):
                break
        else:
            raise RuntimeError(
                f"Could not generate Blum-Williams prime q after {max_attempts} attempts"
            )

        return (p, q)

    def generateBlumWilliamsInteger(self, n, p=0, q=0):
        if((p == 0) or (q == 0)):
            (p,q) = self.generatePrimes(n)
            N = p * q
            return (p, q, N)
        else:
            N = p * q
            return N
