from charm.core.math.elliptic_curve import *

class ECGroup():
    def __init__(self, builtin_cv):
        self.group = ecc(nid=builtin_cv)
        self.param = builtin_cv
        self._verbose = True

    def order(self):
        return order(self.group)

    def bitsize(self):
        return bitsize(self.group)
    
    def paramgen(self, secparam):
        return None

    def groupSetting(self):
        return 'ecc'

    def groupType(self): 
        return self.param

    def init(self, type=ZR):
        return init(self.group, type)
    
    def random(self, type=ZR):
        if type == ZR or type == G:
            return random(self.group, type)
        return None
    
    def encode(self, message):
        return encode(self.group, message)
    
    def decode(self, msg_bytes):
        return decode(self.group, msg_bytes)
    
    def serialize(self, object):
        return serialize(object)
    
    def deserialize(self, bytes_object):
        return deserialize(self.group, bytes_object)
    
    # needs work to iterate over tuple
    def hash(self, args, _type=ZR):
        if isinstance(args, tuple):
            s = bytes()
            for i in args:
                if type(i) == ecc:
                    s += serialize(i)
                elif type(i) == str:
                    s += str(i)
                # consider other types    
            #print("s => %s" % s)
            return hash(self.group, str(s), _type)
        elif type(args) == ecc:
            msg = str(serialize(args))
            return hash(self.group, msg, _type)
        elif type(args) == str:
            return hash(self.group, args, _type)
        return None
    
    def zr(self, point):
        if type(point) == ecc:
            return getXY(self.group, point, False)
        return None

    def coordinates(self, point):
        if type(point) == ecc:
            return getXY(self.group, point, True)
        
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

