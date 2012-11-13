from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80

b = {}

def setup():
    g2 = group.random(G2)
    output = g2
    return output

def keygen(g2):
    alpha = group.random(ZR)
    sk = alpha
    pk = (g2 ** alpha)
    output = (pk, sk)
    return output

def sign(pk, sk, M, t1, t2, t3):
    a = group.hash(t1, G1)
    h = group.hash(t2, G1)
    b = group.hash((M, t3), ZR)
    sig = ((a ** sk) * (h ** (sk * b)))
    output = sig
    return output

def verify(pk, g2, sig, M, t1, t2, t3):
    a = group.hash(t1, G1)
    h = group.hash(t2, G1)
    b = group.hash((M, t3), ZR)
    if ( ( (pair(sig, g2)) == ((pair(a, pk) * (pair(h, pk) ** b))) ) ):
        output = True
    else:
        output = False
        return output
    return output

def membership(g2, pklist, siglist):
    if ( ( (group.ismember(g2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(pklist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(siglist)) == (False) ) ):
        output = False
        return output
    output = True
    return output

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, a, h):
    dotALoopVal = 1
    dotBLoopVal = 1
    dotCLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotALoopVal = (dotALoopVal * dotACache[z])
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
        dotCLoopVal = (dotCLoopVal * dotCCache[z])
    if ( ( (pair(dotALoopVal, g2)) == ((pair(a, dotBLoopVal) * pair(h, dotCLoopVal))) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, startSigNum, midSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, a, h)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, a, h)
    output = None

def batchverify(g2, pklist, t2, t3, t1, Mlist, siglist, incorrectIndices):
    delta = {}
    dotCCache = {}
    dotBCache = {}
    dotACache = {}

    for z in range(0, N):
        delta[z] = SmallExp(secparam)
    if ( ( (membership(g2, pklist, siglist)) == (False) ) ):
        output = False
        return output
    a = group.hash(t1, G1)
    h = group.hash(t2, G1)
    for z in range(0, N):
        b = group.hash((Mlist[z], t3), ZR)
        dotACache[z] = (siglist[z] ** delta[z])
        dotBCache[z] = (pklist[z] ** delta[z])
        dotCCache[z] = (pklist[z] ** (b * delta[z]))
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, g2, a, h)
    output = incorrectIndices
    return output

def indivverify(g2, pklist, t2, t3, t1, Mlist, siglist, incorrectIndices):
    if ( ( (membership(g2, pklist, siglist)) == False ) ):
        output = False
        return output
    for z in range(0, N):
        if verify(pklist[z], g2, siglist[z], Mlist[z], t1, t2, t3) == False:
            incorrectIndices.append(z)
    return incorrectIndices

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('BN256')

    g2 = setup()
    (pk0, sk0) = keygen(g2)
    (pk1, sk1) = keygen(g2)
    t1_0 = "1"
    t2_0 = "2"
    t3_0 = "3"
    t1_1 = "1"
    t2_1 = "2"
    t3_1 = "3"
    t1list = [t1_0, t1_1]
    t2list = [t2_0, t2_1]
    t3list = [t3_0, t3_1]
    Mlist = ["mess1", "mess2"]
    sig0 = sign(pk0, sk0, Mlist[0], t1list[0], t2list[0], t3list[0])
    sig1 = sign(pk1, sk1, Mlist[1], t1list[1], t2list[1], t3list[1])
    print(verify(pk0, g2, sig0, Mlist[0], t1list[0], t2list[0], t3list[0]))
    print(verify(pk1, g2, sig1, Mlist[1], t1list[1], t2list[1], t3list[1]))
    pklist = [pk0, pk1]
    siglist = [sig0, sig1]
    incorrectIndices = []
    batchverify(g2, pklist, t2_0, t3_0, t1_0, Mlist, siglist, incorrectIndices)
    print(incorrectIndices)


if __name__ == '__main__':
    main()

