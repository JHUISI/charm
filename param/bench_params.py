from toolbox.pairinggroup import *
import sys

trials = 200
time_per_curve = {'pair':0.0, 'mul':{G1:0.0, G2:0.0, GT:0.0}, 'exp':{G1:0.0, G2:0.0, GT:0.0} }
curve = {'a.param':time_per_curve.copy(), 'd224.param': time_per_curve.copy() }

def mul_in_grp(group, grpChoice):
    # test 2: mul in 'G1'
    bID1 = InitBenchmark()
    a, b = group.random(grpChoice), group.random(grpChoice)
    #start
    StartBenchmark(bID1, [RealTime])
    for i in range(0, trials):
        c = a * b
    #stop
    EndBenchmark(bID1)
    result = GetBenchmark(bID1, RealTime) / trials
    return result

def exp_in_grp(group, grpChoice):
    bID2 = InitBenchmark()
    a, b = group.random(grpChoice), group.random(ZR)
    #start
    StartBenchmark(bID2, [RealTime])
    for i in range(0, trials):
        c = a ** b
    #stop
    EndBenchmark(bID2)
    result = GetBenchmark(bID2, RealTime) / trials
    return result


def bench(file):
    group = PairingGroup(file)
    
    # test 1: pair time
    bID = InitBenchmark()
    a, b = group.random(G1), group.random(G2)
    # start
    StartBenchmark(bID, [RealTime])
    for i in range(0, trials):
        c = pair(a, b)
    EndBenchmark(bID)
    curve[file]['pair'] = GetBenchmark(bID, RealTime) / trials
    
    for i in [G1, G2, GT]:
        curve[file]['mul'][i] = mul_in_grp(group, i)    
        curve[file]['exp'][i] = exp_in_grp(group, i)

    print("<= Benchmark Results => ")
    print(curve[file])
    
if __name__ == "__main__":
    file = sys.argv[1]
    
    bench(file)
    print("Done.")