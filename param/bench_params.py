from toolbox.pairinggroup import *
import sys

paramList = ['a.param', 'd224.param']
trials = 1
curve = {}

def getGroupConst(groupStr):
    if (groupStr == 'G1'):
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
    result = GetBenchmark(bID1, RealTime) / trials
    return result

def exp_in_grp(group, grpChoice):
    bID2 = InitBenchmark()
    a, b = group.random(getGroupConst(grpChoice)), group.random(ZR)

    StartBenchmark(bID2, [RealTime])
    for i in range(0, trials):
        c = a ** b

    EndBenchmark(bID2)
    result = GetBenchmark(bID2, RealTime) / trials
    return result

def bench(param):
    group = PairingGroup(param)

    bID = InitBenchmark()
    a, b = group.random(G1), group.random(G2)

    StartBenchmark(bID, [RealTime])
    for i in range(0, trials):
        c = pair(a, b)
    EndBenchmark(bID)

    curve[param]['pair'] = GetBenchmark(bID, RealTime) / trials
    
    for i in ['G1', 'G2', 'GT']:
        curve[param]['mul'][i] = mul_in_grp(group, i)        
        curve[param]['exp'][i] = exp_in_grp(group, i)

def generateOutput(outputFile):
    file = open(outputFile, 'w')

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
                outputString += "\t\tpair:  " + str(curve[param]['pair']) + "\n"
            else:
                outputString += "\t\t" + benchmark + ":" + "\n"
                for i in ['G1', 'G2', 'GT']:
                    outputString += "\t\t\t" + i + ":  " + str(curve[param][benchmark][i]) + "\n"
        outputString += "\n"

    outputString += "Done.\n"

    print(outputString)
    file.write(outputString)
    file.close()

if __name__ == "__main__":
    if ( (len(sys.argv) != 3) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        sys.exit("Usage:  python bench_params_dir.py [number of trials] [output file]")

    trials = int(sys.argv[1])
    outputFile = sys.argv[2]

    for paramEntry in paramList:
        curve[paramEntry] = {'pair':0.0, 'mul':{'G1':0.0, 'G2':0.0, 'GT':0.0}, 'exp':{'G1':0.0, 'G2':0.0, 'GT':0.0} }

    for key in curve:
        bench(key)

    generateOutput(outputFile)
