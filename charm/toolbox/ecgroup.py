try:
   from charm.core.math.elliptic_curve import elliptic_curve,ZR,G,init,random,order,getGenerator,bitsize,serialize,deserialize,hashEC,encode,decode,getXY
   #from charm.core.math.elliptic_curve import InitBenchmark,StartBenchmark,EndBenchmark,GetBenchmark,GetGeneralBenchmarks,ClearBenchmark
except Exception as err:
   print(err)
   exit(-1)

ec_element = 'elliptic_curve.Element'

class ECGroup():
    def __init__(self, builtin_cv):
        self.ec_group = elliptic_curve(nid=builtin_cv)
        self.param = builtin_cv
        self._verbose = True

    def __str__(self):
        return str(self.ec_group)

    def order(self):
        return order(self.ec_group)

    def bitsize(self):
        return bitsize(self.ec_group)
    
    def paramgen(self, secparam):
        return None

    def groupSetting(self):
        return 'elliptic_curve'

    def groupType(self): 
        return self.param

    def init(self, _type=ZR):
        return init(self.ec_group, _type)
    
    def random(self, _type=ZR):
        if _type == ZR or _type == G:
            return random(self.ec_group, _type)
        return None
    
    def encode(self, message):
        return encode(self.ec_group, message)
    
    def decode(self, msg_bytes):
        return decode(self.ec_group, msg_bytes)
    
    def serialize(self, object):
        return serialize(object)
    
    def deserialize(self, bytes_object):
        return deserialize(self.ec_group, bytes_object)
    
    # needs work to iterate over tuple
    def hash(self, args, target_type=ZR):
        if isinstance(args, tuple):
            s = bytes()
            for i in args:
                if ec_element in str(i.__class__):
                    s += serialize(i)
                elif type(i) == str:
                    s += bytes(str(i), 'utf8')
                elif type(i) == bytes:
                    s += i
                else:
                    print("unexpected type: ", type(i))
                # consider other types    
            #print("s => %s" % s)
            assert len(s) != 0, "hash input is empty."
            return hashEC(self.ec_group, str(s), target_type)
        elif ec_element in str(args.__class__): # type(args) == elliptic_curve:
            msg = str(serialize(args))
            return hashEC(self.ec_group, msg, target_type)
        elif type(args) in [str, bytes]:
            return hashEC(self.ec_group, args, target_type)
        raise Exception("ECGroup - invalid input for hash")
    
    def zr(self, point):
        if ec_element in str(point.__class__): # type(point) == elliptic_curve:
            return getXY(self.ec_group, point, False)
        return None

    def coordinates(self, point):
        if ec_element in str(point.__class__): # type(point) == elliptic_curve:
            return getXY(self.ec_group, point, True)
        
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

