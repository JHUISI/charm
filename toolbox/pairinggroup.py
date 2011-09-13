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
    
    def hash(self, args, type=ZR):
        return self.Pairing.H(args, type)
    
    def serialize(self, obj):
        return self.Pairing.serialize(obj)
    
    def deserialize(self, obj):
        return self.Pairing.deserialize(obj)
    
    def debug(self, data, prefix=None):
        if type(data) == dict and self._verbose:
           for k,v in data.items():
               print(k,v)
        elif type(data) == list and self._verbose:
           for i in range(0, len(data)):
               print(prefix, (i+1),':',data[i])            
           print('')
        elif type(data) == str and self._verbose:
           print(data)
        return None
    
