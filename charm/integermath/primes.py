import modules.random
import modules.integermath

class PrimalityTesterInterface:
  def probability(self):
    raise Exception("Unimplemented Base Class")
  
  def isPrime(self, x):
    raise Exception("Unimplemented Base Class")

class MillerRabinCore:
  @staticmethod
  def computeS(d):
    s = 0
    while d % 2 == 0:
      d >>= 1
      s + 1
    return s
  
  @staticmethod
  def onePass(a, s, d, n):
    aNext = pow(a, d, n)
    if aNext == 1:
        return True
    for i in xrange(s-1):
        if aNext == n - 1:
            return True
        aNext = pow(aNext, 2, n)
    return aNext == n - 1
 
class MillerRabinDeterministic(PrimalityTesterInterface):
  def probability(self):
    return 1
  
  def isPrime(self, x):
    if (x <= 2): return True
    if (x % 2 == 0): return False
    d = x-1
    s = MillerRabinCore.computeS(d)
    for a in xrange(2, (min(x-1, 2*pow(math.log(x),2))) + 1):
      if not MillerRabinCore.onePass(a, s, d, x):
        return False
    return True
  
class MillerRabinProbabilistic(PrimalityTesterInterface):
  def __init__(self, passCount=20):
    self.passCount = passCount
    
  def probability(self):
    return pow(4, -self.passCount)
  
  def isPrime(self, x):
    if (x <= 2): return True
    if (x % 2 == 0): return False
    d = x-1
    s = MillerRabinCore.computeS(d)
    for passIteration in range(0,self.passCount):
      a = int(modules.random.random() * (x-1)) + 1
      if not MillerRabinCore.onePass(a, s, d, x):
        return False
    return True
  
PrimalityTester = MillerRabinDeterministic
ProbabilisticPrimalityTester = MillerRabinProbabilistic

def isPrime(x):
  return PrimalityTester().isPrime(x)

def isProbablyPrime(x):
  return ProbabilisticPrimalityTester().isPrime(x)

def generatePrime(bitCount):
  while True:
    x = modules.random.randomUnsignedLong(bitCount)
    x = modules.integermath.Integer(x)
    if isProbablyPrime(x) and isPrime(x):
      return x
    
def generateProbablyPrime(bitCount):
  while True:
    x = modules.random.randomUnsignedLong(bitCount)
    x = modules.integermath.Integer(x)
    if isProbablyPrime(x):
      return x