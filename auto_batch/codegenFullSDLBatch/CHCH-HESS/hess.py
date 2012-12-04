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
    assert group.ismember(P), "failed membership test"
    assert group.ismember(g2), "failed membership test"
    assert group.ismemberList(pklist), "failed membership test"
    assert group.ismemberList(S1list), "failed membership test"
    assert group.ismemberList(S2list), "failed membership test"
    return True

#    if ( ( (group.ismember(g2)) == (False) ) ):
#        output = False
#        return output
#    if ( ( (group.ismember(pklist)) == (False) ) ):
#        output = False
#        return output
#    if ( ( (group.ismember(P)) == (False) ) ):
#        output = False
#        return output
#    if ( ( (group.ismember(S1list)) == (False) ) ):
#        output = False
#        return output
#    if ( ( (group.ismember(S2list)) == (False) ) ):
#        output = False
#        return output
#    output = True
#    return output

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
        dividenconquer(delta, startSigNum, midSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, pklist, Mlist, P, S1list, S2list)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, pklist, Mlist, P, S1list, S2list)
    output = None

def batchverify(g2, pklist, Mlist, P, S1list, S2list, incorrectIndices):
    dotCCache = {}
    delta = {}
    dotBCache = {}
    dotACache = {}

    if ( ( (membership(g2, pklist, P, S1list, S2list)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        delta[z] = SmallExp(secparam)
        a = group.hash((Mlist[z], S1list[z]), ZR)
        dotACache[z] = (S2list[z] ** delta[z])
        dotBCache[z] = (pklist[z] ** (a * delta[z]))
        dotCCache[z] = (S1list[z] ** delta[z])
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, g2, pklist, Mlist, P, S1list, S2list)
    output = incorrectIndices
    return output

def indivverify(g2, pklist, Mlist, P, S1list, S2list, incorrectIndices):
    for z in range(0, N):
        assert group.ismember(P), "failed membership test"
        assert group.ismember(g2), "failed membership test"
        assert group.ismember(pklist[z]), "failed membership test"
        assert group.ismember(S1list[z]), "failed membership test"
        assert group.ismember(S2list[z]), "failed membership test"
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
        (S1list[z], S2list[z]) = sign(pklist[z], sklist[z], Mlist[z], g2)
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
    incorrectIndices = batchverify(g2, pklist, Mlist, P, S1list, S2list, [])
    print("incorrectIndices: ", incorrectIndices)


if __name__ == '__main__':
    main()

