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
         # Use _value (single underscore) to avoid Python 3.13+ name-mangling
         # issues with double-underscore attributes in nested classes.
         __slots__ = ('_value',)
         def __init__(self, value): self._value = value
         Value = property(lambda self: self._value)
         EnumType = property(lambda self: EnumType)
         def __hash__(self):        return hash(self._value)
         def __lt__(self, other):
             if not isinstance(other, EnumValue): return NotImplemented
             return (self._value < other._value)
         def __gt__(self, other):
             if not isinstance(other, EnumValue): return NotImplemented
             return (self._value > other._value)
         def __le__(self, other):
             if not isinstance(other, EnumValue): return NotImplemented
             return (self._value <= other._value)
         def __ge__(self, other):
             if not isinstance(other, EnumValue): return NotImplemented
             return (self._value >= other._value)
         def __eq__(self, other):
             if isinstance(other, int):
                 return self._value == other
             if isinstance(other, EnumValue):
                 return self._value == other._value
             return NotImplemented
         def __ne__(self, other):
             if isinstance(other, int):
                 return self._value != other
             if isinstance(other, EnumValue):
                 return self._value != other._value
             return NotImplemented
         def __invert__(self):      return constants[maximum - self._value]
         def __nonzero__(self):     return bool(self._value)
         def __bool__(self):        return bool(self._value)
         def __repr__(self):        return str(names[self._value])

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
