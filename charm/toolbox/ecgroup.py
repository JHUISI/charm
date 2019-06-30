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

    def init(self, _type=ZR, value=None):
        """initializes an object with a specified type and value"""
        if value is not None:
            return init(self.ec_group, _type, value)
        return init(self.ec_group, _type)
    
    def random(self, _type=ZR):
        """selects a random element in ZR or G"""        
        if _type == ZR or _type == G:
            return random(self.ec_group, _type)
        return None
    
    def encode(self, message, include_ctr=False):
        """encode arbitrary string as a group element. Max size is dependent on the EC group order"""
        return encode(self.ec_group, message, include_ctr)
    
    def decode(self, msg_bytes, include_ctr=False):
        """decode a group element into a string"""
        return decode(self.ec_group, msg_bytes, include_ctr)
    
    def serialize(self, object):
        """serializes a pairing object into bytes"""        
        return serialize(object)
    
    def deserialize(self, bytes_object):
        """deserializes into a pairing object"""        
        return deserialize(self.ec_group, bytes_object)

    def hash(self, args, target_type=ZR):
        """hashes objects into ZR or G

        Different object types may hash to the same element, e.g., the ASCII
        string 'str' and the byte string b'str' map to the same element."""
        def hash_encode(arg):
            """encode a data type to bytes"""
            if type(arg) is bytes:
                s = arg
            elif type(arg) is ec_element:
                s = serialize(arg)
            elif type(arg) is str:
                s = arg.encode('utf-8')
            elif type(arg) is int:
                s = arg.to_bytes((arg.bit_length() + 7) // 8, 'little')
            elif isinstance(args, tuple):
                # based on TupleHash (see NIST SP 800-185)
                def left_encode(x):
                    # This implictly checks for validity conditions:
                    # An exception is raised if n > 255, i.e., if len(x) > 2**2040
                    n = (x.bit_length() + 7 ) // 8
                    return n.to_bytes(1, 'little') + x.to_bytes(n, 'little')

                s = b''
                for arg in args:
                    z = hash_encode(arg)
                    # concat with encode_string(z)
                    s += left_encode(len(z)) + z
            else:
                raise ValueError("unexpected type to hash: {}".format(type(arg)))

            return s

        return hashEC(self.ec_group, hash_encode(args), target_type)

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
