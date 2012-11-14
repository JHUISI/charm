from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits
import random

group = None

N = 10

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

def sign(pk, sk, M):
    s = group.random(ZR)
    S1 = (pk ** s)
    a = group.hash((M, S1), ZR)
    S2 = (sk ** (s + a))
    output = (S1, S2)
    return output

def verify(P, g2, pk, M, S1, S2):
    a = group.hash((M, S1), ZR)

    if ( ( (pair(S2, g2)) == (pair((S1 * (pk ** a)), P)) ) ):
        output = True
    else:
        output = False
        return output
    return output

def membership(P, S1list, S2list, g2, pklist):
    if ( ( (group.ismember(P)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(S1list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(S2list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(pklist)) == (False) ) ):
        output = False
        return output
    output = True
    return output

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, g2, P):
    dotALoopVal = group.init(G1)
    dotBLoopVal = group.init(G1)
    for z in range(startSigNum, endSigNum):
        dotALoopVal = (dotALoopVal * dotACache[z])
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
    
    if ( ( (pair(dotALoopVal, g2)) == (pair(dotBLoopVal, P)) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, startSigNum, midSigNum, incorrectIndices, dotACache, dotBCache, g2, P)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, g2, P)
    output = None

def batchverify(Mlist, P, S1list, S2list, g2, pklist, incorrectIndices):
    delta = {}
    dotBCache = {}
    dotACache = {}

    for z in range(0, N):
        delta[z] = SmallExp(secparam)
    if ( ( (membership(P, S1list, S2list, g2, pklist)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        a = group.hash((Mlist[z], S1list[z]), ZR)
        dotACache[z] = (S2list[z] ** delta[z])
        dotBCache[z] = ((S1list[z] ** delta[z]) * (pklist[z] ** (a * delta[z])))
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, g2, P)
    output = incorrectIndices
    return output

def indivverify(Mlist, P, S1list, S2list, g2, pklist, incorrectIndices):
    if ( ( (membership(P, S1list, S2list, g2, pklist)) == (False) ) ):
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
    pklist = {}
    sklist = {}
    for z in range(0, N):
        (pklist[z], sklist[z]) = keygen(alpha, "test" + str(z))

    Mlist = ["test" + str(z) for z in range(0, N)]

    S1list = {}
    S2list = {}
    for z in range(0, N):
        (S1list[z], S2list[z]) = sign(pklist[z], sklist[z], Mlist[z])
        assert verify(P, g2, pklist[z], Mlist[z], S1list[z], S2list[z]), "invalid signature generated"
    
    badList = []
    for i in range(0, int(N/2)):
        randomIndex = random.randint(0, N-1)
        if randomIndex not in badList:
            badList.append(randomIndex)
    
    badList.sort()
    for i in badList:
        Mlist[i] = "foo"
    print("badList         : ", badList)
    incorrectIndices = batchverify(Mlist, P, S1list, S2list, g2, pklist, [])
    print("incorrectIndices: ", incorrectIndices)


if __name__ == '__main__':
    main()

