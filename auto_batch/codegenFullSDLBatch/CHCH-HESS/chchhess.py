from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits
import hess, chch

group = None

N = 2

secparam = 80

ac = {}
ah = {}

def verify(S1h, S2h, S1c, S2c, pk, P, g2, M):
    ah = group.hash((M, S1h), ZR)
    ac = group.hash((M, S1c), ZR)
    if ( ( (( (pair(S2h, g2)) == ((pair((pk ** ah), P) * S1h)) )) and (( (pair(S2c, g2)) == (pair((S1c * (pk ** ac)), P)) )) ) ):
        output = True
    else:
        output = False
        return output
    return output

def membership(g2, P, S1clist, pklist, S2clist, S2hlist, S1hlist):
    assert group.ismember(g2), "failed membership test"
    assert group.ismember(P), "failed membership test"
    for z in range(0, N):
        assert group.ismember(pklist[z]), "failed membership test"
        assert group.ismember(S1clist[z]), "failed membership test"
        assert group.ismember(S2clist[z]), "failed membership test"
        assert group.ismember(S1hlist[z]), "failed membership test"
        assert group.ismember(S2hlist[z]), "failed membership test"
    return True
#    if ( ( (group.ismember(g2)) == (False) ) ):
#        output = False
#        return output
#    if ( ( (group.ismember(P)) == (False) ) ):
#        output = False
#        return output
#    if ( ( (group.ismember(S1clist)) == (False) ) ):
#        output = False
#        return output
#    if ( ( (group.ismember(pklist)) == (False) ) ):
#        output = False
#        return output
#    if ( ( (group.ismember(S2clist)) == (False) ) ):
#        output = False
#        return output
#    if ( ( (group.ismember(S2hlist)) == (False) ) ):
#        output = False
#        return output
#    if ( ( (group.ismember(S1hlist)) == (False) ) ):
#        output = False
#        return output
#    output = True
#    return output

def dividenconquer(delta1, delta2, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, P, g2):
    dotALoopVal = 1
    dotBLoopVal = 1
    dotCLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotALoopVal = (dotALoopVal * dotACache[z])
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
        dotCLoopVal = (dotCLoopVal * dotCCache[z])
    if ( ( ((pair(dotALoopVal, P) * (dotBLoopVal * pair(dotCLoopVal, g2)))) == group.init(GT, 1) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta1, delta2, startSigNum, midSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, P, g2)
        dividenconquer(delta1, delta2, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, P, g2)
    output = None

def batchverify(g2, P, S1clist, pklist, Mlist, S2clist, S2hlist, S1hlist, incorrectIndices):
    delta1 = {}
    delta2 = {}
    dotCCache = {}
    dotBCache = {}
    dotACache = {}

    if ( ( (membership(g2, P, S1clist, pklist, S2clist, S2hlist, S1hlist)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        delta1[z] = SmallExp(secparam)
        delta2[z] = SmallExp(secparam)
        ac = group.hash((Mlist[z], S1clist[z]), ZR)
        ah = group.hash((Mlist[z], S1hlist[z]), ZR)
        dotACache[z] = ((pklist[z] ** (ah * delta1[z])) * ((S1clist[z] ** -delta2[z]) * (pklist[z] ** (-ac * delta2[z]))))
        dotBCache[z] = (S1hlist[z] ** delta1[z])
        dotCCache[z] = ((S2hlist[z] ** -delta1[z]) * (S2clist[z] ** delta2[z]))
    dividenconquer(delta1, delta2, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, P, g2)
    output = incorrectIndices
    return output

def indivverify(g2, P, S1clist, pklist, Mlist, S2clist, S2hlist, S1hlist, incorrectIndices):
    for z in range(0, N):
        assert group.ismember(g2), "failed membership test"
        assert group.ismember(P), "failed membership test"
        assert group.ismember(pklist[z]), "failed membership test"
        assert group.ismember(S1clist[z]), "failed membership test"
        assert group.ismember(S2clist[z]), "failed membership test"
        assert group.ismember(S1hlist[z]), "failed membership test"
        assert group.ismember(S2hlist[z]), "failed membership test"
        if verify(S1hlist[z], S2hlist[z], S1clist[z], S2clist[z], pklist[z], P, g2, Mlist[z]) == False:
            incorrectIndices.append(z)
    return incorrectIndices

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('BN256')

    chch.group = group
    hess.group = group
    (g2, alpha, P) = chch.setup()
    
    pklist = {}
    sklist = {}
    for z in range(0, N):
        (pklist[z], sklist[z]) = chch.keygen(alpha, "test" + str(z))

    Mlist = ["test" + str(z) for z in range(0, N)]
    
    S1clist = {}
    S2clist = {}
    for z in range(0, N):
        (S1clist[z], S2clist[z]) = chch.sign(pklist[z], sklist[z], Mlist[z])
        assert chch.verify(P, g2, pklist[z], Mlist[z], S1clist[z], S2clist[z]), "invalid signature generated"
        print("sign & verify for chch: ", z)

    S1hlist = {}
    S2hlist = {}
    for z in range(0, N):
        (S1hlist[z], S2hlist[z]) = hess.sign(pklist[z], sklist[z], Mlist[z], g2)
        assert hess.verify(P, g2, pklist[z], Mlist[z], S1hlist[z], S2hlist[z]), "invalid signature generated"
        print("sign & verify for hess: ", z)


    assert verify(S1hlist[0], S2hlist[0], S1clist[0], S2clist[0], pklist[0], P, g2, Mlist[0]), "indiv. verification failed for chch-hess combo"
    print("Successful combo verification!!!")

    incorrectIndices = batchverify(g2, P, S1clist, pklist, Mlist, S2clist, S2hlist, S1hlist, [])
    print("incorrectIndices: ", incorrectIndices)
    
if __name__ == '__main__':
    main()

