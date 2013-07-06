from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.ecgroup import ECGroup,ZR,G
from charm.toolbox.eccurve import prime192v2
from charm.core.math.integer import * 

import unittest, sys

debug = False

def isSaneBenchmark(dct):
    isSane=True
    for val in dct.values():
        if(type(val)==list):
            for v in val:
                isSane&=v>=0
        else:
            isSane&=val>=0
    return isSane

@unittest.skipIf(sys.platform == 'darwin', "expected issues on Mac OS X.")
class BenchmarkTest1(unittest.TestCase):
    def testPairing(self):    
        trials = 10
        trials2 = trials * 3 
        group = PairingGroup("SS512")
        g = group.random(G1)
        h = group.random(G1)
        i = group.random(G2)

        self.assertTrue(group.InitBenchmark())
        group.StartBenchmark(["RealTime", "Exp", "Pair"])
        for a in range(trials):
            j = g * h 
            k = i ** group.random(ZR)
            t = (j ** group.random(ZR)) / h 
            n = pair(h, i)
        group.EndBenchmark()
       
        msmtDict = group.GetGeneralBenchmarks()
        self.assertTrue(isSaneBenchmark(msmtDict))        

        self.assertTrue(group.InitBenchmark())
        
        group.StartBenchmark(["CpuTime", "Mul", "Pair"])
        for a in range(trials2):
            j = g * h 
            k = i ** group.random(ZR)
            n = pair(h, i)
        group.EndBenchmark()
        
        msmtDict = group.GetGeneralBenchmarks()
        del group
        self.assertTrue(isSaneBenchmark(msmtDict))        

@unittest.skipIf(sys.platform == 'darwin', "expected issues on Mac OS X.")
class BenchmarkTest2(unittest.TestCase):
    def testECGroup(self):
        trials = 10
        group = ECGroup(prime192v2)
        g = group.random(G)
        h = group.random(G)
        i = group.random(G)
        
        self.assertTrue(group.InitBenchmark())
        group.StartBenchmark(["RealTime", "Mul", "Div", "Exp", "Granular"])
        for a in range(trials):
            j = g * h 
            k = h ** group.random(ZR)
            t = (j ** group.random(ZR)) / k 
        group.EndBenchmark()
        
        msmtDict = group.GetGeneralBenchmarks()
        self.assertTrue(isSaneBenchmark(msmtDict))        
        
        granDict = group.GetGranularBenchmarks()
        self.assertTrue(isSaneBenchmark(granDict))        
        
        self.assertTrue(group.InitBenchmark())
        group.StartBenchmark(["RealTime", "Mul", "Div", "Exp", "Granular"])
        for a in range(trials*2):
            j = g * h 
            k = h ** group.random(ZR)
            t = (j ** group.random(ZR)) / k 
        group.EndBenchmark()
        
        msmtDict = group.GetGeneralBenchmarks()
        granDict = group.GetGranularBenchmarks()
        del group
        self.assertTrue(isSaneBenchmark(msmtDict))        
        self.assertTrue(isSaneBenchmark(granDict))

@unittest.skipIf(sys.platform == 'darwin', "expected issues on Mac OS X.")
class BenchmarkTest3(unittest.TestCase):
    def testInterleave(self):
        trials = 10
        trials2 = trials * 3 
        group1 = PairingGroup("MNT224")
        group2 = PairingGroup("MNT224")
        
        g = group1.random(G1)
        h = group1.random(G1)
        i = group1.random(G2)
        
        self.assertTrue(group1.InitBenchmark())
        self.assertTrue(group2.InitBenchmark())
        group1.StartBenchmark(["RealTime", "Exp", "Pair", "Div", "Mul"])
        for a in range(trials):
            j = g * h 
            k = i ** group1.random(ZR)
            t = (j ** group1.random(ZR)) / h 
            n = pair(h, i)
        group1.EndBenchmark()
        msmtDict = group1.GetGeneralBenchmarks()
        del group1, group2
        self.assertTrue(isSaneBenchmark(msmtDict))

@unittest.skipIf(sys.platform == 'darwin', "expected issues on Mac OS X.")
class BenchmarkTest4(unittest.TestCase):
    def testInteger(self):
        count = 5
        time_in_ms = 1000
        
        a = integer(10)
        
        self.assertTrue(InitBenchmark())
        StartBenchmark(["RealTime", "Exp", "Mul"])
        for k in range(count):
            r = randomPrime(256)
            s = r * (r ** a)
            j = r * (r ** a)
        EndBenchmark()
        msmtDict = GetGeneralBenchmarks()
        self.assertTrue(isSaneBenchmark(msmtDict))        
        
        self.assertTrue(InitBenchmark())
        StartBenchmark(["RealTime", "Exp", "Mul", "Add", "Sub"])
        for k in range(count):
            r = randomPrime(256)
            s = r * (r ** a)
            j = r * (r ** a)
            u = s + j - j 
        EndBenchmark()
        msmtDict = GetGeneralBenchmarks()
        self.assertTrue(isSaneBenchmark(msmtDict)) 


if __name__ == "__main__":
    unittest.main()
