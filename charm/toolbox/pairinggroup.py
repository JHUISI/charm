try:
  from charm.toolbox.pairingcurves import params as param_info
  from charm.core.math.pairing import pairing,pc_element,ZR,G1,G2,GT,init,pair,hashPair,H,random,serialize,deserialize,ismember,order
  import charm.core.math.pairing as pg
  from charm.config import libs,pairing_lib
except Exception as err:
  print(err)
  exit(-1)

class PairingGroup():
    def __init__(self, param_id, param_file=False, secparam=512, verbose=False):
        #legacy handler to handle calls that still pass in a file path
        if param_file:
          self.Pairing = pairing(file=param_id)
        elif type(param_id) == str:
          pairID = param_info.get(param_id)
          assert pairID != None, "'%s' not recognized! See 'pairingcurves.py' in toolbox." % param_id
          if pairing_lib == libs.pbc:
             self.Pairing = pairing(string=pairID)
             self.param = param_id
          elif pairing_lib in [libs.miracl, libs.relic]:
             self.Pairing = pairing(pairID)
             self.param = pairID
        elif type(param_id) == int:
          self.Pairing = pairing(param_id)
          self.param   = param_id
 
        self.secparam = secparam # number of bits
        self._verbose = verbose
    
    def __str__(self):
        return str(self.Pairing)

    def order(self):
        """returns the order of the group"""
        return order(self.Pairing)
    
    def paramgen(self, qbits, rbits):
        return None

    def ismember(self, obj):
        """membership test for a pairing object"""
        return ismember(self.Pairing, obj)

    def ismemberList(self, obj):
        """membership test for a list of pairing objects"""        
        for i in range(len(obj)):
            if ismember(self.Pairing, obj[i]) == False: return False
        return True

    def ismemberDict(self, obj):
        """membership test for a dict of pairing objects"""                
        for i in obj.keys():
            if ismember(self.Pairing, obj[i]) == False: return False
        return True

    def groupSetting(self):
        return 'pairing'

    def groupType(self): 
        return self.param
        
    def messageSize(self):
        return self.secparam / 8        

    def init(self, type, value=None):
        """initializes an object with a specified type and value""" 
        if value != None:
            return init(self.Pairing, type, value)
        return init(self.Pairing, type)
            
    def random(self, _type=ZR, count=1, seed=None):
        """selects a random element in ZR, G1, G2 and GT"""
        if _type == GT: return self.__randomGT()
        elif _type in [ZR, G1, G2]:
            if seed != None and count == 1:
                return random(self.Pairing, _type, seed)
            elif count > 1:
                return tuple([random(self.Pairing, _type) for i in range(count)])                
            return random(self.Pairing, _type)
        return None

        
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
        """hashes objects into ZR, G1 or G2 depending on the pairing curve"""
        return H(self.Pairing, args, type)
    
    def serialize(self, obj, compression=True):
        """Serialize a pairing object into bytes.

           :param compression: serialize the compressed representation of the
                curve element, taking about half the space but potentially
                incurring in non-negligible computation costs when
                deserializing. Default is True for compatibility with previous
                versions of charm.
            
            >>> p = PairingGroup('SS512')
            >>> v1 = p.random(G1)
            >>> b1 = p.serialize(v1)
            >>> b1 == p.serialize(v1, compression=True)
            True
            >>> v1 == p.deserialize(b1)
            True
            >>> b1 = p.serialize(v1, compression=False)
            >>> v1 == p.deserialize(b1, compression=False)
            True
        """
        return serialize(obj, compression)
    
    def deserialize(self, obj, compression=True):
        """Deserialize a bytes serialized element into a pairing object. 

           :param compression: must be used for objects serialized with the
                compression parameter set to True. Default is True for
                compatibility with previous versions of charm.
        """
        return deserialize(self.Pairing, obj, compression)
    
    def debug(self, data, prefix=None):
        if not self._verbose:
            return
        if type(data) == dict:
            for k,v in data.items():
               print(k,v)
        elif type(data) == list:
            for i in range(0, len(data)):
               print(prefix, (i+1),':',data[i])
            print('')
        elif type(data) == str:
            print(data)
        else:
            print(type(data), ':', data)
        return
    
    def pair_prod(self, lhs, rhs):
        """takes two lists of G1 & G2 and computes a pairing product"""
        return pair(lhs, rhs, self.Pairing)

    def InitBenchmark(self):
        """initiates the benchmark state"""
        return pg.InitBenchmark(self.Pairing)
    
    def StartBenchmark(self, options):
        """starts the benchmark with any of these options: 
        RealTime, CpuTime, Mul, Div, Add, Sub, Exp, Pair, Granular"""
        return pg.StartBenchmark(self.Pairing, options)
    
    def EndBenchmark(self):
        """ends an ongoing benchmark"""
        return pg.EndBenchmark(self.Pairing)
        
    def GetGeneralBenchmarks(self):
        """retrieves benchmark count for all group operations"""
        return pg.GetGeneralBenchmarks(self.Pairing)
    
    def GetGranularBenchmarks(self):
        """retrieves group operation count per type: ZR, G1, G2, and GT"""
        return pg.GetGranularBenchmarks(self.Pairing)
    
    def GetBenchmark(self, option):
        """retrieves benchmark results for any of these options: 
        RealTime, CpuTime, Mul, Div, Add, Sub, Exp, Pair, Granular"""
        return pg.GetBenchmark(self.Pairing, option)


def extract_key(g):
    """
    Given a group element, extract a symmetric key
    :param g:
    :return:
    """
    g_in_hex = hashPair(g).decode('utf-8')
    return bytes(bytearray.fromhex(g_in_hex))
