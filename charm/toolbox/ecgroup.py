try:
   from charm.core.math.elliptic_curve import elliptic_curve,ec_element,ZR,G,init,random,order,getGenerator,bitsize,serialize,deserialize,hashEC,encode,decode,getXY
   import charm.core.math.elliptic_curve as ecc
except Exception as err:
   print(err)
   exit(-1)

class ECGroup():
    def __init__(self, builtin_cv):
        self.ec_group = elliptic_curve(nid=builtin_cv)
        self.param = builtin_cv
        self._verbose = True

    def __str__(self):
        return str(self.ec_group)

    def order(self):
        """returns the order of the group"""
        return order(self.ec_group)

    def bitsize(self):
        """returns the bitsize for encoding messages in the group"""
        return bitsize(self.ec_group)
    
    def paramgen(self, secparam):
        return None

    def groupSetting(self):
        return 'elliptic_curve'

    def groupType(self): 
        return self.param

    def init(self, _type=ZR):
        """initializes an object with a specified type and value"""        
        return init(self.ec_group, _type)
    
    def random(self, _type=ZR):
        """selects a random element in ZR or G"""        
        if _type == ZR or _type == G:
            return random(self.ec_group, _type)
        return None
    
    def encode(self, message):
        """encode arbitrary string as a group element. Max size is dependent on the EC group order"""
        return encode(self.ec_group, message)
    
    def decode(self, msg_bytes):
        """decode a group element into a string"""
        return decode(self.ec_group, msg_bytes)
    
    def serialize(self, object):
        """serializes a pairing object into bytes"""        
        return serialize(object)
    
    def deserialize(self, bytes_object):
        """deserializes into a pairing object"""        
        return deserialize(self.ec_group, bytes_object)
    
    # needs work to iterate over tuple
    def hash(self, args, target_type=ZR):
        """hashes objects into ZR or G"""        
        if isinstance(args, tuple):
            s = bytes()
            for i in args:
                if type(i) == ec_element:
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
        elif type(args) == ec_element:
            msg = str(serialize(args))
            return hashEC(self.ec_group, msg, target_type)
        elif type(args) in [str, bytes]:
            return hashEC(self.ec_group, args, target_type)
        raise Exception("ECGroup - invalid input for hash")
    
    def zr(self, point):
        """get the X coordinate only"""
        if type(point) == ec_element:
            return getXY(self.ec_group, point, False)
        return None

    def coordinates(self, point):
        """get the X and Y coordinates of an EC point"""
        if type(point) == ec_element:
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

    def InitBenchmark(self):
        """initiates the benchmark state"""        
        return ecc.InitBenchmark(self.ec_group)
    
    def StartBenchmark(self, options):
        """starts the benchmark with any of these options: 
        RealTime, CpuTime, Mul, Div, Add, Sub, Exp, Granular"""        
        return ecc.StartBenchmark(self.ec_group, options)
    
    def EndBenchmark(self):
        """ends an ongoing benchmark"""        
        return ecc.EndBenchmark(self.ec_group)
        
    def GetGeneralBenchmarks(self):
        """retrieves benchmark count for all group operations"""
        return ecc.GetGeneralBenchmarks(self.ec_group)
    
    def GetGranularBenchmarks(self):
        """retrieves group operation count per type: ZR and G"""        
        return ecc.GetGranularBenchmarks(self.ec_group)
    
    def GetBenchmark(self, option):
        """retrieves benchmark results for any of these options: 
        RealTime, CpuTime, Mul, Div, Add, Sub, Exp, Granular"""        
        return ecc.GetBenchmark(self.ec_group, option)