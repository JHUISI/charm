# Implementing the proof of concept secret sharing 
from __future__ import print_function
from toolbox.pairinggroup import PairingGroup,ZR

class SecretShare:
    def __init__(self, element, verbose_status=False):
        self.elem = element
        self.verbose = verbose_status
        
    def P(self, coeff, x):
        share = self.elem.init(ZR, 0)
        # evaluate polynomial
        for i in range(0, len(coeff)):
            i2 = self.elem.init(ZR, long(i))
            share += (coeff[i] * (x ** i2))
        return share

    def genShares(self, secret, k, n, q=None, x_points=None):
        if(k <= n):
            if q == None: 
                q = [self.elem.random(ZR) for i in range(0, k)]
                q[0] = secret

            if x_points == None: # just go from 0 to n
                shares = [self.P(q, i) for i in range(0, n+1)] # evaluating poly. q at i for all i
            else:
                shares = {}
                for i in range(len(x_points)):
                    shares[i] = (x_points[i], self.P(q, x_points[i]))
#                     = [self.P(q, i) for i in x_points] # x_points should be a list

        # debug
        if self.verbose:
            print('Secret: %s' % secret)
            for i in range(1, k):
                print("a %s: %s" % (i, q[i]))
            print('')
            if x_points == None:
                for i in range(1,n+1):
                    print('Share %s: %s' % (i, shares[i]))
            else:
                for i in range(len(x_points)):
                    print('Share %s: %s' % (i, shares[i]))
            
        return shares
    
    # shares is a dictionary
    def recoverCoefficients(self, list):
        coeff = {}
        for i in list:
            result = self.elem.init(ZR, long(1))
            for j in list:
                if not (i == j):
                    # lagrange basis poly
                    result *= (0 - j) / (i - j)
            if self.verbose: print("coeff '%d' => '%s'" % (i, result))
            coeff[i] = result
        return coeff
        
    def recoverSecret(self, shares):
        list = shares.keys()
        if self.verbose: print(list)
        coeff = self.recoverCoefficients(list)
        if self.verbose: print("coefficients: ", coeff)
        secret = self.elem.init(ZR, 0)
        for i in list:
            secret += (coeff[i] * shares[i])

        return secret

if __name__ == "__main__":

# Testing Secret sharing python API
  k = 3
  n = 4
  p = PairingGroup('../param/a.param')

  s = SecretShare(p, True)
  sec = p.random(ZR)
  shares = s.genShares(sec, k, n)

  K = shares[0]
  print('\nOriginal secret: %s' % K)
  y = {1:shares[1], 2:shares[2], 3:shares[3]}

  secret = s.recoverSecret(y)

  if(K == secret):
    print('\nRecovered secret: %s' % secret)
  else:
    print('\nCould not recover the secret!')


