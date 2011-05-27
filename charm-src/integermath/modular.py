
import integer
import modules.random

def xgcd(a, b):
    x,y, u,v = 0,1, 1,0
    while a != 0:
        q,r = b/a,b%a; m,n = x-u*q,y-v*q
        b,a, x,y, u,v = a,r, u,v, m,n
    return b, x, y

def modinv(a, m):
    g, x, y = xgcd(a, m) # or egcd(a, m)
    if g != 1:
      return None
    else:
      return x % m
    
class SpecialExponent:
  def __init__(self, power):
    if self.__class__ == SpecialExponent:
      raise Exception("SpecialExponent is an abstract class.")
    self.power = power
    
  def pow(self, modularInt):
    raise Exception("method [pow] must be redefined in subclasses.")
  
  def __int__(self):
    return int(self.power)
  
  def __long__(self):
    return int(self.power)
  
  def __float__(self):
    return float(self.power)

class Integer(integer.Integer):
  #convenience method
  @staticmethod
  def Random(modulus, generator=modules.random.randomUnsignedLong):
    bitcountApprox = modulus.bit_length()
    temp = generator(bitcountApprox)
    return Integer(temp, modulus)
  
  #until integer.Integer is it's own class, we have to overwrite new
  def __new__(cls, value, modulus):
    i = integer.Integer.__new__(cls, value%modulus)
    i.__init__(value, modulus)
    return i
    
  def __init__(self, value, modulus):
    integer.Integer.__init__(self, value%modulus)
    self.value = integer.Integer(value)
    self.modulus = integer.Integer(modulus)
    self.inverse = None

  def __add__(self, num):
    if isinstance(num, Integer):
      if num.modulus != self.modulus:
        raise Exception("Can only add modular integers of the same modulus")
      v = num.value
    elif not isinstance(num, integer.Integer):
      v = integer.Integer(num)
    else:
      v = num
    return Integer((self.value + v) % self.modulus, self.modulus)
  
  def __sub__(self, num):
    if isinstance(num, Integer):
      if num.modulus != self.modulus:
        raise Exception("Can only add modular integers of the same modulus")
      v = num.value
    #elif not isinstance(num, integer.Integer):
    #  v = integer.Integer(num)
    else:
      v = num
    return Integer((self.value - v) % self.modulus, self.modulus)
  
  def __mul__(self, num):
    return Integer(self.value*num, self.modulus)
  
  def __div__(self, num):
    return Integer(self.value/num, self.modulus)
  
  def __pow__(self, num):
    if isinstance(num, SpecialExponent):
      return num.pow(self)
    elif num == -1:
      if self.inverse == None:
        self.inverse = modinv(self.value, self.modulus)
        if self.inverse == None:
          return None
        self.inverse =  Integer(self.inverse, self.modulus)
      return self.inverse
    elif num < 0:
      raise Exception("Negative Exponents (other than inverse) are not allowed")
    else:
      return Integer(pow(self.value, int(num), self.modulus), self.modulus)
    
  def __int__(self):
    return self.value % self.modulus
  
  def __long__(self):
    return self.value % self.modulus
  
#def random():
  
def randomQR(N):
  return Integer(modules.random.random() * N-1, N) ** 2
