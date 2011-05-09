from charm.ecc import *

class ECGroup():
    def __init__(self, builtin_cv):
        self.elem = ecc(nid=builtin_cv)
        self._verbose = True
    
    def paramgen(self, secparam):
        return None

    def groupType(self): 
        return 'ECGroup'     

    def init(self, type=ZR):
        return self.elem.init(type)
    
    def random(self, type=ZR):
        if type == ZR or type == G:
            return self.elem.random(type)
        return None
    
    def encode(self, message):
        return self.elem.encode(message)
    
    def decode(self, msg_bytes):
        return self.elem.decode(msg_bytes)
    
    def serialize(self, object):
        return self.elem.serialize(object)
    
    def deserialize(self, bytes_object):
        return self.elem.deserialize(bytes_object)
    
    # needs work to iterate over tuple
    def hash(self, args, _type=ZR):
        if isinstance(args, tuple):
            s = bytes()
            for i in args:
                if type(i) == ecc:
                    s += self.elem.serialize(i)
                elif type(i) == str:
                    s += str(i)
                # consider other types    
            #print("s => %s" % s)
            return self.elem.hash(str(s), _type)
        elif type(args) == ecc:
            msg = str(self.elem.serialize(args))
            return self.elem.hash(msg, _type)
        elif type(args) == str:
            return self.elem.hash(args, _type)
        return None
    
    def zr(self, point):
        if type(point) == ecc:
            return self.elem.toInt(point)
        return None
        
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

