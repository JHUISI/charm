from __future__ import print_function
from charm.pairing import *
from charm.integer import randomBits,bitsize,integer

class PairingGroup():
    def __init__(self, param_file, secparam=512, verbose=False):
        self.Pairing = pairing(param_file)
        self.secparam = secparam # number of bits
#        self.rand = init()
        self._verbose = verbose

    # will be used to define curve parameters and such
    def paramgen(self, qbits, rbits):
        return None

    def validSize(self, value):
        size = bitsize(value)
        if size <= self.messageSize():
            return True
        print("ERROR: max len => %s, input len => %s" % (self.messageSize(), size))
        return False

    def ismember(self, obj):
        if type(obj) in [tuple, list]:
           for i in obj:
               if self.Pairing.ismember(i) == False: return False 
           return True
        elif type(obj) == dict:
           for i in obj.keys():
               if self.Pairing.ismember(obj[i]) == False: return False
           return True
        else:
           return self.Pairing.ismember(obj)

    def groupType(self): 
        return 'PairingGroup'     
        
    def messageSize(self):
        return self.secparam / 8        

    def init(self, type, value=None):
        if value != None:
            return self.Pairing.init(type, value)
        return self.Pairing.init(type)
            
    def random(self, type=ZR, seed=None):
        if type == GT: return self.__randomGT()
        elif type == ZR or type == G1 or type == G2:
            if seed != None:
                return self.Pairing.random(type, seed)
            return self.Pairing.random(type)
        else:
            return integer(randomBits(self.secparam))
        
    def __randomGT(self):
        if not hasattr(self, 'gt'):
            self.gt = pair(self.Pairing.random(G1), self.Pairing.random(G2))
        z = self.Pairing.random(ZR)
        return self.gt ** z
    
    def encode(self, message):
        raise NotImplementedException
    
    def decode(self, element):
        raise NotImplementedException 
    
    def hash(self, args, type1=ZR):
        if(type(args) == str):
            args = unicode(args)
        return self.Pairing.H(args, type1)
    
    def serialize(self, obj):
        return self.Pairing.serialize(obj)
    
    def deserialize(self, obj):
        return self.Pairing.deserialize(obj)
    
    def debug(self, data, prefix=None):
        if type(data) == dict and self._verbose:
           for k,v in data.items():
               if type(v) == dict and self._verbose:
                   print(k + " ", end='')
                   print("{",end='')
                   for i, (a,b) in enumerate(v.items()):
                       if i: print(", '%s': %s" % (a, b), end='')
                       else: print("'%s': %s" % (a, b), end='')
                   print("}")
               else:
                   print(k,v)
        elif type(data) == list and self._verbose:
           for i in range(0, len(data)):
               print(prefix, (i+1),':',data[i])            
           print('')
        elif type(data) == str and self._verbose:
           print(data)
        return None
    
