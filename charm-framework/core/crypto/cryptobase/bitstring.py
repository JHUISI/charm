import math
bitstring = __import__("bitstring")

class PyBitStringAdapter:
  def __init__(self, parentClass, objClass, bitstring):
    self.parentClass = parentClass
    self.objClass = objClass
    self.bitstring = bitstring
    
  def __lshift__(self, n):
    if n == 0: return self.bistring
    copyObjBinConstructor = self.bitstring.bin.replace('0b','0b' + ('0'*n))
    resultObj = self.objClass(copyObjBinConstructor)
    return self.parentClass.__ishift__(resultObj, n)
  
  def __rshift__(self, n):
    if n == 0: return self.bistring
    resultObj = self.parentClass.__rshift__(self.bitstring, n)
    return resultObj[n:]
    
  def __ilshift__(self, n):
    if n == 0: return bitstring
    self.bitstring.prepend('0b' + ('0'*n))
    self.parentClass.__ilshift__(self.bitstring, n)
    return self.bitstring
  
  def __irshift__(self, n):
    if n == 0: return self.bitstring
    self.parentClass.__irshift__(self.bitstring, n)
    del self.bitstring[0:n]
    return self.bitstring

class BitString(bitstring.BitArray):
  def __init__(self, *args, **kargs):
    if kargs.get("length", None) == None and kargs.has_key("uint"):
      kargs["length"] = int(math.ceil(math.log(kargs["uint"]+1, 2)))
    bitstring.BitArray.__init__ (self, *args, **kargs)
    self.__adapter = PyBitStringAdapter(bitstring.BitArray, BitString, self)
    
  def __lshift__(self, n):
    return self.__adapter << n
    
  def __ilshift__(self, n):
    self.__adapter <<= n
    return self
    
  def __rshift__(self, n):
    return self.__adapter >> n
    
  def __irshift__(self, n):
    self.__adapter >>= n
    return self
  
    
class ConstBitString(bitstring.ConstBitArray):
  def __init__(self, *args, **kargs):
    if kargs.get("length", None) == None and kargs.has_key("uint"):
      kargs["length"] = int(math.ceil(math.log(kargs["uint"]+1, 2)))
    bitstring.ConstBitArray.__init__ (self, *args, **kargs)
    self.__adapter = PyBitStringAdapter(bitstring.ConstBitArray, ConstBitString, self)
    
  def __lshift__(self, n):
    return self.__adapter << n
  
  def __rshift__(self, n):
    return self.__adapter >> n