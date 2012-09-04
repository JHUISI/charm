try:
   from charm.core.math.elliptic_curve import elliptic_curve,ZR,G,init,random,order,getGenerator,bitsize,serialize,deserialize,hashEC,encode,decode,getXY
   #from charm.core.math.elliptic_curve import InitBenchmark,StartBenchmark,EndBenchmark,GetBenchmark,GetGeneralBenchmarks,ClearBenchmark
except Exception as err:
   print(err)
   exit(-1)

class ECGroup():
    def __init__(self, builtin_cv):
        self.group = elliptic_curve(nid=builtin_cv)
        self.param = builtin_cv
        self._verbose = True

    def order(self):
        return order(self.group)

    def bitsize(self):
        return bitsize(self.group)
    
    def paramgen(self, secparam):
        return None

    def groupSetting(self):
        return 'elliptic_curve'

    def groupType(self): 
        return self.param

    def init(self, _type=ZR):
        return init(self.group, _type)
    
    def random(self, _type=ZR):
        if _type == ZR or _type == G:
            return random(self.group, _type)
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
                if type(i) == elliptic_curve:
                    s += serialize(i)
                elif type(i) == str:
                    s += str(i)
                # consider other types    
            #print("s => %s" % s)
            return hashEC(self.group, str(s), _type)
        elif type(args) == elliptic_curve:
            msg = str(serialize(args))
            return hashEC(self.group, msg, _type)
        elif type(args) == str:
            return hashEC(self.group, args, _type)
        return None
    
    def zr(self, point):
        if type(point) == elliptic_curve:
            return getXY(self.group, point, False)
        return None

    def coordinates(self, point):
        if type(point) == elliptic_curve:
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

