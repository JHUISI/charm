from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80

h = {}

def keygen():

    input = None
    g = group.random(G2)
    x = group.random(ZR)
    pk = (g ** x)
    sk = x
    output = (pk, sk, g)
    return output

def sign(sk, M):

    input = [sk, M]
    sig = (group.hash(M, G1) ** sk)
    output = sig
    return output

def verify(pk, M, sig, g):
    global h

    #input = [pk, M, sig, g]
    h = group.hash(M, G1)
    if ( ( (pair(h, pk)) == (pair(sig, g)) ) ):
        output = True
    else:
        output = False
        return output
    return output

def membership(pk, siglist, g):

    #input = [pk, siglist, g]
    if ( ( (group.ismember(pk)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(siglist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g)) == (False) ) ):
        output = False
        return output
    output = True
    return output

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, pk, g):

    #input = [delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, pk, g]
    dotALoopVal = 1
    dotBLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotALoopVal = (dotALoopVal * dotACache[z])
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
    if ( ( (pair(dotALoopVal, pk)) == (pair(dotBLoopVal, g)) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotACache, dotBCache, pk, g)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, pk, g)
    output = None

def batchverify(Mlist, pk, siglist, g, incorrectIndices):
    #global h

    delta = {}
    dotBCache = {}
    dotACache = {}

    #input = [Mlist, pk, siglist, g, incorrectIndices]
    for z in range(0, N):
        delta[z] = SmallExp(group, secparam)
    if ( ( (membership(pk, siglist, g)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        h = group.hash(Mlist[z], G1)
        dotACache[z] = (h ** delta[z])
        dotBCache[z] = (siglist[z] ** delta[z])
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, pk, g)
    output = incorrectIndices
    return output

def indivverify(Mlist, pk, siglist, g, incorrectIndices):
    if ( ( (membership(pk, siglist, g)) == (False) ) ):
        output = False
        return output
    
    for z in range(0, N):
        if verify(pk, Mlist[z], siglist[z], g) == False:
            incorrectIndices.append(z)
    
    return incorrectIndices

def SmallExp(group, bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('BN256')
    (pk, sk, g) = keygen()
    M1 = "test1"
    M2 = "test2"
    sig1 = sign(sk, M1)
    sig2 = sign(sk, M2)

    assert verify(pk, M1, sig1, g), "failed verification 1"
    assert verify(pk, M2, sig2, g), "failed verification 2"
    print("Successful Verification")

    Mlist = [M1, M2]
    siglist = [sig1, sig2]
    incorrectIndices = batchverify(Mlist, pk, siglist, g, [])
    print(incorrectIndices)

if __name__ == '__main__':
    main()

