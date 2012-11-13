from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80

a = {}

def setup():
    g2 = group.random(G2)
    alpha = group.random(ZR)
    P = (g2 ** alpha)
    output = (g2, alpha, P)
    return output

def keygen(alpha, ID):
    sk = (group.hash(ID, G1) ** alpha)
    pk = group.hash(ID, G1)
    output = (pk, sk)
    return output

def sign(pk, sk, M, g2):
    h = group.random(G1)
    s = group.random(ZR)
    S1 = (pair(h, g2) ** s)
    a = group.hash((M, S1), ZR)
    S2 = ((sk ** a) * (h ** s))
    output = (S1, S2)
    return output

def verify(P, g2, pk, M, S1, S2):
    a = group.hash((M, S1), ZR)
    if ( ( (pair(S2, g2)) == (((pair(pk, P) ** a) * S1)) ) ):
        output = True
    else:
        output = False
        return output
    return output

def membership(g2, pklist, P, S1list, S2list):
    if ( ( (group.ismember(g2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(pklist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(P)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(S1list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(S2list)) == (False) ) ):
        output = False
        return output
    output = True
    return output

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, pklist, Mlist, P, S1list, S2list):
    dotALoopVal = 1
    dotBLoopVal = 1
    dotCLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotALoopVal = (dotALoopVal * dotACache[z])
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
        dotCLoopVal = (dotCLoopVal * dotCCache[z])
    if ( ( (pair(dotALoopVal, g2)) == ((pair(dotBLoopVal, P) * dotCLoopVal)) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotACache, dotBCache, dotCCache, g2, pklist, Mlist, P, S1list, S2list)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, pklist, Mlist, P, S1list, S2list)
    output = None

def batchverify(g2, pklist, Mlist, P, S1list, S2list, incorrectIndices):
    dotCCache = {}
    delta = {}
    dotBCache = {}
    dotACache = {}

    for z in range(0, N):
        delta[z] = SmallExp(secparam)
    if ( ( (membership(g2, pklist, P, S1list, S2list)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        a = group.hash((Mlist[z], S1list[z]), ZR)
        dotACache[z] = (S2list[z] ** delta[z])
        dotBCache[z] = (pklist[z] ** (a * delta[z]))
        dotCCache[z] = (S1list[z] ** delta[z])
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, g2, pklist, Mlist, P, S1list, S2list)
    output = incorrectIndices
    return output

def indivverify(g2, pklist, Mlist, P, S1list, S2list, incorrectIndices):
    if ( ( (membership(g2, pklist, P, S1list, S2list)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        if verify(P, g2, pklist[z], Mlist[z], S1list[z], S2list[z]) == False:
            incorrectIndices.append(z)
    return incorrectIndices

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('BN256')
    (g2, alpha, P) = setup()
    (pk1, sk1) = keygen(alpha, "test1")
    (pk2, sk2) = keygen(alpha, "test2")
    (S1_1, S2_1) = sign(pk1, sk1, "mess1", g2)
    (S1_2, S2_2) = sign(pk2, sk2, "mess2", g2)
    print(verify(P, g2, pk1, "mess1", S1_1, S2_1))
    pklist = [pk1, pk2]
    Mlist = ["mess1", "mess2"]
    S1list = [S1_1, S1_2]
    S2list = [S2_1, S2_2]
    incorrectIndices = []
    batchverify(g2, pklist, Mlist, P, S1list, S2list, incorrectIndices)
    print(incorrectIndices)


if __name__ == '__main__':
    main()

