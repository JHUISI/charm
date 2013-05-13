# code adapted from active state code recipes for enumeration
def Enum(*names):
      class EnumClass(object):
         __slots__ = names
         def __iter__(self):        return iter(constants)
         def __len__(self):         return len(constants)
         def __getitem__(self, i):  
             if type(i) == int: return constants[i]
             elif type(i) == str: 
                 index = lookup.get(i) 
                 if index != None: return constants[index]
                 else: return None
             else: assert False, "Invalid input type."
         def __repr__(self):        return 'Enum' + str(names)
         def __str__(self):         return 'enum ' + str(constants)
         def getList(self):         return list(names)

      class EnumValue(object):
         #__slots__ = ('__value')
         def __init__(self, value): self.__value = value
         Value = property(lambda self: self.__value)
         EnumType = property(lambda self: EnumType)
         def __hash__(self):        return hash(self.__value)
         def __lt__(self, other): 
             return (self.__value < other.__value)
         def __gt__(self, other): 
             return (self.__value > other.__value)
         def __le__(self, other): 
             return (self.__value <= other.__value)
         def __ge__(self, other): 
             return (self.__value >= other.__value)
         def __eq__(self, other): 
             if type(self) == int: lhs = self
             else: lhs = self.__value
             if type(other) == int: rhs = other
             else: rhs = other.__value
             return (lhs == rhs)
         def __ne__(self, other): 
             if type(self) == int: lhs = self
             else: lhs = self.__value
             if type(other) == int: rhs = other
             else: rhs = other.__value
             return (lhs != rhs)
         def __invert__(self):      return constants[maximum - self.__value]
         def __nonzero__(self):     return bool(self.__value)
         def __repr__(self):        return str(names[self.__value])

      maximum = len(names) - 1
      constants = [None] * len(names)
      lookup = {}
      for i, each in enumerate(names):
          val = EnumValue(i)
          setattr(EnumClass, each, val)
          # create list of int => 'str'
          constants[i] = val
          # create reverse lookup 
          lookup[str(val)] = i
      constants = tuple(constants)
      EnumType = EnumClass()
      return EnumType
