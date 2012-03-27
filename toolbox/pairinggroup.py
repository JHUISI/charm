from __future__ import print_function
from charm.pairing import *
from toolbox.pairingcurves import params
from charm.integer import randomBits,bitsize,integer
import os.path

class PairingGroup():
    def __init__(self, param_file, secparam=512, verbose=False):        
        #legacy handler to handle calls that still pass in a file path
        if type(param_file) == str:
          pair = params.get(param_file)
          assert pair != None, "'%s' not recognized! See 'pairingcurves.py' in toolbox." % param_file
          self.Pairing = pairing(string=pair)
          self.param = param_file
        elif type(param_file) == int:
            # support for MIRACL initialization : default arg := MNT160
          self.Pairing = pairing(param_file)
          self.param   = param_file
 
        self.secparam = secparam # number of bits
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
        if type(obj) in [set, tuple, list]:
           for i in obj:
               if type(i) == pairing:
                  if ismember(self.Pairing, i) == False: return False 
           return True
        elif type(obj) == dict:
           for i in obj.keys():
               if type(i) == pairing:
                  if ismember(self.Pairing, obj[i]) == False: return False
           return True
        else:
           if type(obj) == pairing:
               return ismember(self.Pairing, obj)
           return None # ignore non-pairing types

    def groupSetting(self):
        return 'pairing'

    def groupType(self): 
        return self.param
        
    def messageSize(self):
        return self.secparam / 8        

    def init(self, type, value=None):
        if value != None:
            return init(self.Pairing, type, value)
#            return self.Pairing.init(type, long(value))
        return init(self.Pairing, type)
            
    def random(self, type=ZR, count=1, seed=None):
        if type == GT: return self.__randomGT()
        elif type == ZR or type == G1 or type == G2:
            if seed != None and count == 1:
                return random(self.Pairing, type, seed)
            elif count > 1:
                return tuple([random(self.Pairing, type) for i in range(count)])                
            return random(self.Pairing, type)
        else:
            return integer(randomBits(self.secparam))

        
    def __randomGT(self):
        if not hasattr(self, 'gt'):
            self.gt = pair(self.random(G1), self.random(G2))
        z = self.random(ZR)
        return self.gt ** z
    
    def encode(self, message):
        raise NotImplementedException
    
    def decode(self, element):
        raise NotImplementedException 
    
    def hash(self, args, type=ZR):
        return H(self.Pairing, args, type)
    
    def serialize(self, obj):
        return serialize(obj)
    
    def deserialize(self, obj):
        return deserialize(self.Pairing, obj)
    
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
    
    def pair_prod(self, lhs, rhs):
        return pair(lhs, rhs, self.Pairing)
