from toolbox.pairinggroup import *
from charm.integer import randomBits
import sys

paramList = ['a.param', 'd224.param']
trials = 1
curve = {}
time_in_ms = 1000
Bits = 80 # security level for PRNG

def getGroupConst(groupStr):
    if(groupStr == 'ZR'):
        return ZR
    elif (groupStr == 'G1'):
        return G1
    elif (groupStr == 'G2'):
        return G2
    elif (groupStr == 'GT'):
        return GT
    else:
        return NULL

def mul_in_grp(group, grpChoice):
    bID1 = InitBenchmark()
    a, b = group.random(getGroupConst(grpChoice)), group.random(getGroupConst(grpChoice))

    StartBenchmark(bID1, [RealTime])
    for i in range(0, trials):
        c = a * b

    EndBenchmark(bID1)
    result = (GetBenchmark(bID1, RealTime) / trials) * time_in_ms
    return result

def exp_in_grp(group, grpChoice):
    bID2 = InitBenchmark()
    a, b = group.random(getGroupConst(grpChoice)), group.random(ZR)

    StartBenchmark(bID2, [RealTime])
    for i in range(0, trials):
        c = a ** b

    EndBenchmark(bID2)
    result = (GetBenchmark(bID2, RealTime) / trials) * time_in_ms
    return result

def hash_in_grp(group, grpChoice):
    bID3 = InitBenchmark()
    _hash = group.Pairing.H
    _grp = getGroupConst(grpChoice)
    m = "this is some message of a good length!!!" # 40 bytes
    StartBenchmark(bID3, [RealTime])
    for i in range(trials):
        res = _hash(m, _grp)
    EndBenchmark(bID3)
    result = (GetBenchmark(bID3, RealTime) / trials) * time_in_ms
    return result

def prng_bits(group, bits=80):
    bID4 = InitBenchmark()
    StartBenchmark(bID4, [RealTime])
    for i in range(trials):
        a = randomBits(bits)
    EndBenchmark(bID4)
    result = (GetBenchmark(bID4, RealTime) / trials) * time_in_ms
    return result

def bench(param):
    group = PairingGroup(param)

    bID = InitBenchmark()
    a, b = group.random(G1), group.random(G2)

    StartBenchmark(bID, [RealTime])
    for i in range(0, trials):
        c = pair(a, b)
    EndBenchmark(bID)

    curve[param]['pair'] = (GetBenchmark(bID, RealTime) / trials) * time_in_ms
    
    for i in ['G1', 'G2', 'GT']:
        curve[param]['mul'][i] = mul_in_grp(group, i)        
        curve[param]['exp'][i] = exp_in_grp(group, i)
    
    curve[param]['hash']['ZR'] = hash_in_grp(group, 'ZR')
    curve[param]['hash']['G1'] = hash_in_grp(group, 'G1')
    curve[param]['hash']['G2'] = curve[param]['hash']['GT'] = 0
    # how long it takes to generate integers of a certain number of bits
    curve[param]['prng'] = prng_bits(group)

def generateOutput(outputFile):
    file = open(outputFile, 'w')
    data = open(outputFile + ".py", 'w')
    
    dataStr = ""
    dataStr += "benchmarks = " + str(curve)
    data.write(dataStr)
    data.close()
    
    outputString = ""

    outputString += "\n<= Benchmark Results =>\n\n"
    outputString += "Raw Output:\n"
    outputString += str(curve)
    outputString += "\n\n"
    outputString += "Formatted Output:\n\n"

    for param in curve:
        outputString += "\t" + param + "\n"
        for benchmark in curve[param]:
            if (benchmark == "pair"):
                outputString += "\t\tpair:  " + str(curve[param]['pair']) + " ms\n"
            elif (benchmark == "prng"):
                outputString += "\t\tprng of "+ str(Bits) + " bits:  " + str(curve[param]['prng']) + " ms\n"
            elif (benchmark == "hash"):
                outputString += "\t\t" + benchmark + ":\n"
                for i in ['ZR', 'G1']:
                    outputString += "\t\t\t" + i + ":  " + str(curve[param][benchmark][i]) + " ms\n"
            else:
                outputString += "\t\t" + benchmark + ":\n"
                for i in ['G1', 'G2', 'GT']:
                    outputString += "\t\t\t" + i + ":  " + str(curve[param][benchmark][i]) + " ms\n"
        outputString += "\n"

    outputString += "Done.\n"

    print(outputString)
    file.write(outputString)
    file.close()

if __name__ == "__main__":
    if ( (len(sys.argv) != 3) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        sys.exit("Usage:  python %s [number of trials] [output file]" % sys.argv[0])

    trials = int(sys.argv[1])
    outputFile = sys.argv[2]

    for paramEntry in paramList:
        grps = {'ZR':0.0, 'G1':0.0, 'G2':0.0, 'GT':0.0}
        curve[paramEntry] = {'pair':0.0, 'mul':grps.copy(), 
                             'exp':grps.copy(), 'hash':grps.copy(), 'prng':0.0 }

    for key in curve:
        bench(key)

    generateOutput(outputFile)
