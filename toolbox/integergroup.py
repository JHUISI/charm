from charm.integer import *

class IntegerGroup:
    def __init__(self, start=0):
        if start != 0:   
            fixed = start 
            self.randObj = init(fixed)
        self.randObj = init()
        
    def paramgen(self, bits, r=2):
        # determine which group
        while True:
            self.q = self.randObj.randomPrime(bits)
            self.p = r*self.q + 1
            if (isPrime(self.p) and isPrime(self.q)):
                break
        self.r = r
        return None    
    
    def randomGen(self):
        while True:
            h = self.randObj.random(self.p)
            g = (h ** self.r) % self.p
            if not g == 1:
                break
        return g
        
    def groupType(self): 
        return 'SchnorrGroup mod p'     
          
    def groupOrder(self):
        return bitsize(self.q)    
    
    def messageSize(self):    
        return bitsize(self.q) / 8 
    
    def isMember(self, x):
        return x.isCongruent()
       
    def random(self):
        return self.randObj.random(self.p)        

    def randomPrime(self, bits):
        return self.randObj.randomPrime(bits)
    
    def encode(self, M):
        return encode(M, self.p, self.q)
     
    def decode(self, element):
        return decode(element, self.p, self.q)
    
    def hash(self, *args):
        if isinstance(args, tuple):
            #print "Hashing => '%s'" % args
            return hash(args, self.p, self.q, False)
        return None

class IntegerGroupQ:
    def __init__(self, start=0):
        if start != 0:   
            fixed = start 
            self.randObj = init(fixed)
        self.randObj = init()
        
    def paramgen(self, bits, r=2):
        # determine which group
        while True:
            self.q = self.randObj.randomPrime(bits)
            self.p = r*self.q + 1
            if (isPrime(self.p) and isPrime(self.q)):
                break
        self.r = r
        return None    
    
    def randomGen(self):
        while True:
            h = self.randObj.random(self.p)
            g = (h ** self.r) % self.p
            if not g == 1:
                #print "g => %s" % g 
                break
        return g
        
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
            return self.randObj.random(self.q)
        else:
            return self.randObj.random(max)

    def randomPrime(self, bits):
        return self.randObj.randomPrime(bits)
    
    def encode(self, M):
        return encode(M, self.p, self.q)
     
    def decode(self, element):
        return decode(element, self.p, self.q)
    
    def hash(self, *args):
        if isinstance(args, tuple):
            return hash(args, self.p, self.q, True)
        List = []
        for i in args:
            List.append(i)
        return hash(tuple(List), self.p, self.q, True)
    
