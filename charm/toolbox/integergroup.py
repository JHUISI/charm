try:
  #from charm.core.math.integer import integer,randomBits,random,randomPrime,isPrime,encode,decode,hashInt,bitsize,legendre,gcd,lcm,serialize,deserialize,int2Bytes,toInt
  from charm.core.math.integer import * #InitBenchmark,StartBenchmark,EndBenchmark,GetBenchmark,GetGeneralBenchmarks,ClearBenchmark
except Exception as err:
  print(err)
  exit(-1)
    
class IntegerGroup:
    def __init__(self, start=0):
        pass

    def setparam(self, p, q): 
        if p == (2 * q) + 1 and isPrime(p) and isPrime(q):
            self.p = integer(p)
            self.q = integer(q)
            return True
        else:
            print("p and q are not safe primes!")
        return False
    
    def __str__(self):
        outStr = ""
        outStr += "p = " + str(self.p) + "\n"
        outStr += "q = " + str(self.q) + "\n"
        return outStr
        
    def paramgen(self, bits, r=2):
        # determine which group
        while True:
            self.p = randomPrime(bits, 1)
            self.q = (self.p - 1) / 2
            if (isPrime(self.p) and isPrime(self.q)):
                break
        self.r = r
        return None    
    
    def randomGen(self):
        while True:
            h = random(self.p)
            g = (h ** self.r) % self.p
            if not g == 1:
                break
        return g

    def groupSetting(self):
        return 'integer'
        
    def groupType(self): 
        return 'SchnorrGroup mod p'     
          
    def groupOrder(self):
        return bitsize(self.q)    
    
    def bitsize(self):    
        return bitsize(self.q) / 8 
    
    def isMember(self, x):
        return x.isCongruent()
       
    def random(self, max=0):
        if max == 0:
            return random(self.p)        
        else:
            return random(max)
    
    def encode(self, M):
        return encode(M, self.p, self.q)
     
    def decode(self, element):
        return decode(element, self.p, self.q)

    def serialize(self, object):
        assert type(object) == integer, "cannot serialize non-integer types"
        return serialize(object)
    
    def deserialize(self, bytes_object):
        assert type(bytes_object) == bytes, "cannot deserialize object"
        return deserialize(bytes_object)
    
    def hash(self, *args):
        if isinstance(args, tuple):
            #print "Hashing => '%s'" % args
            return hashInt(args, self.p, self.q, False)
        return None

    def InitBenchmark(self):
        """initiates the benchmark state"""
        return InitBenchmark()
    
    def StartBenchmark(self, options):
        """starts the benchmark with any of these options: 
        RealTime, CpuTime, Mul, Div, Add, Sub, Exp"""
        return StartBenchmark(options)
    
    def EndBenchmark(self):
        """ends an ongoing benchmark"""
        return EndBenchmark()
        
    def GetGeneralBenchmarks(self):
        """retrieves benchmark count for all group operations"""
        return GetGeneralBenchmarks()
        
    def GetBenchmark(self, option):
        """retrieves benchmark results for any of these options: 
        RealTime, CpuTime, Mul, Div, Add, Sub, Exp"""
        return GetBenchmark(option)

class IntegerGroupQ:
    def __init__(self, start=0):
        pass

    def __str__(self):
        outStr = ""
        outStr += "p = " + str(self.p) + "\n"
        outStr += "q = " + str(self.q) + "\n"
        return outStr

    def setparam(self, p, q): 
        if p == (2 * q) + 1 and isPrime(p) and isPrime(q):
            self.p = integer(p)
            self.q = integer(q)
            return True
        else:
            print("p and q are not safe primes!")
        return False
        
    def paramgen(self, bits, r=2):
        # determine which group
        while True:
            self.p = randomPrime(bits, 1)
            self.q = (self.p - 1) / 2
            if (isPrime(self.p) and isPrime(self.q)):
                break
        self.r = r
        return None    
    
    def randomG(self):
        return self.randomGen()
        
    def randomGen(self):
        while True:
            h = random(self.p)
            g = (h ** self.r) % self.p
            if not g == 1:
                #print "g => %s" % g 
                break
        return g

    def groupSetting(self):
        return 'integer'
        
    def groupType(self): 
        return 'SchnorrGroup mod q'     
          
    def groupOrder(self):
        return bitsize(self.q)    
    
    def messageSize(self):    
        return bitsize(self.q) / 8 
    
    def isMember(self, x):
        return x.isCongruent()
       
    def random(self, max=0):
        if max == 0:
            return random(self.q)
        else:
            return random(max)
    
    def encode(self, M):
        return encode(M, self.p, self.q)
     
    def decode(self, element):
        return decode(element, self.p, self.q)
    
    def hash(self, *args):
        if isinstance(args, tuple):
            return hashInt(args, self.p, self.q, True)
        List = []
        for i in args:
            List.append(i)
        return hashInt(tuple(List), self.p, self.q, True)

    def serialize(self, object):
        assert type(object) == integer, "cannot serialize non-integer types"
        return serialize(object)
    
    def deserialize(self, bytes_object):
        assert type(bytes_object) == bytes, "cannot deserialize object"
        return deserialize(bytes_object)

    def InitBenchmark(self):
        """initiates the benchmark state"""
        return InitBenchmark()
    
    def StartBenchmark(self, options):
        """starts the benchmark with any of these options: 
        RealTime, CpuTime, Mul, Div, Add, Sub, Exp"""
        return StartBenchmark(options)
    
    def EndBenchmark(self):
        """ends an ongoing benchmark"""
        return EndBenchmark()
        
    def GetGeneralBenchmarks(self):
        """retrieves benchmark count for all group operations"""
        return GetGeneralBenchmarks()
        
    def GetBenchmark(self, option):
        """retrieves benchmark results for any of these options: 
        RealTime, CpuTime, Mul, Div, Add, Sub, Exp"""
        return GetBenchmark(option)

    
class RSAGroup:
    def __init__(self):
        self.p = self.q = self.n = 0

    def __str__(self):
        outStr = ""
        outStr += "p = " + str(self.p) + "\n"
        outStr += "q = " + str(self.q) + "\n"
        outStr += "N = " + str(self.n) + "\n"
        return outStr
    
    def paramgen(self, secparam):
        while True:
           p, q = randomPrime(secparam), randomPrime(secparam)
           if isPrime(p) and isPrime(q) and gcd(p * q, (p - 1) * (q - 1)) == 1:
              break
        n = p * q
        self.p = p
        self.q = q
        self.n = n
        return (p, q, n)

    def setparam(self, p, q): 
        if isPrime(p) and isPrime(q) and p != q:
            self.p = integer(p)
            self.q = integer(q)
            self.n = self.p * self.q
            return True
        else:
            print("p and q are not primes!")
        return False

    def serialize(self, object):
        assert type(object) == integer, "cannot serialize non-integer types"
        return serialize(object)
    
    def deserialize(self, bytes_object):
        assert type(bytes_object) == bytes, "cannot deserialize object"
        return deserialize(bytes_object)

    def random(self, max=0):
        if max == 0:
            return random(self.n)        
        else:
            return random(max)

    def groupSetting(self):
        return 'integer'

    def groupType(self): 
        return 'RSAGroup mod p'     
          
    def groupOrder(self):
        return bitsize(self.n)    
        
    def encode(self, value):
        pass

    def decode(self, value):
        pass

    def InitBenchmark(self):
        """initiates the benchmark state"""
        return InitBenchmark()
    
    def StartBenchmark(self, options):
        """starts the benchmark with any of these options: 
        RealTime, CpuTime, Mul, Div, Add, Sub, Exp"""
        return StartBenchmark(options)
    
    def EndBenchmark(self):
        """ends an ongoing benchmark"""
        return EndBenchmark()
        
    def GetGeneralBenchmarks(self):
        """retrieves benchmark count for all group operations"""
        return GetGeneralBenchmarks()
        
    def GetBenchmark(self, option):
        """retrieves benchmark results for any of these options: 
        RealTime, CpuTime, Mul, Div, Add, Sub, Exp"""
        return GetBenchmark(option)
