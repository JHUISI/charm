from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

l = 2

secparam = 80

dotProd = {}
h = {}

def setup():
    g = group.random(G2)
    alpha = group.random(ZR)
    P = (g ** alpha)
    output = (P, g, alpha)
    return output

def concat(ID_list):
    L = ""
    l = len(ID_list)
    for y in range(0, l):
        L = (L + ":" + ID_list[y])
    output = L
    return output

def keygen(alpha, ID):
    sk = (group.hash(ID, G1) ** alpha)
    pk = group.hash(ID, G1)
    output = (pk, sk)
    return output

def sign(ID, ID_list, pk, sk, M):
    h = {}
    u = {}
    pklist = {}

    Lt = concat(ID_list)
    for i in range(0, l):
        if ( ( (ID) != (ID_list[i]) ) ):
            u[i] = group.random(G1)
            h[i] = group.hash((M, Lt, u[i]), ZR)
        else:
            s = i
    r = group.random(ZR)
    for y in range(0, l):
        pklist[y] = group.hash(ID_list[y], G1)
    dotProd = 1
    for i in range(0, l):
        if ( ( (ID) != (ID_list[i]) ) ):
            dotProd = (dotProd * (u[i] * (pklist[i] ** h[i])))
    u[s] = ((pk ** r) * (dotProd ** -1))
    h[s] = group.hash((M, Lt, u[s]), ZR)
    S = (sk ** (h[s] + r))
    output = (Lt, pklist, u, S)
    return output

def verify(Lt, pklist, P, g, M, u, S):
    for y in range(0, l):
        h[y] = group.hash((M, Lt, u[y]), ZR)
    dotProd = 1
    for y in range(0, l):
        dotProd = (dotProd * (u[y] * (pklist[y] ** h[y])))
    if ( ( (pair(dotProd, P)) == (pair(S, g)) ) ):
        output = True
    else:
        output = False
        return output
    return output

def membership(P, Slist, g, pklist, ulist):
    if ( ( (group.ismember(P)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(Slist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(pklist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(ulist)) == (False) ) ):
        output = False
        return output
    output = True
    return output

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotBCache, dotCCache, P, g):
    dotBLoopVal = 1
    dotCLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
        dotCLoopVal = (dotCLoopVal * dotCCache[z])
    if ( ( (pair(dotBLoopVal, P)) == (pair(dotCLoopVal, g)) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, startSigNum, midSigNum, incorrectIndices, dotBCache, dotCCache, P, g)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotBCache, dotCCache, P, g)
    output = None

def batchverify(Lt, Mlist, P, Slist, g, pklist, ulist, incorrectIndices):
    dotCCache = {}
    delta = {}
    dotBCache = {}

    for z in range(0, N):
        delta[z] = SmallExp(secparam)
    if ( ( (membership(P, Slist, g, pklist, ulist)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        dotALoopVal = 1
        for y in range(0, l):
            h = group.hash((Mlist[z], Lt, ulist[z][y]), ZR)
            dotALoopVal = (dotALoopVal * ((ulist[z][y] ** delta[z]) * (pklist[y] ** (h * delta[z]))))
        dotBCache[z] = dotALoopVal
        dotCCache[z] = (Slist[z] ** delta[z])
    dividenconquer(delta, 0, N, incorrectIndices, dotBCache, dotCCache, P, g)
    output = incorrectIndices
    return output

def indivverify(Lt, Mlist, P, Slist, g, pklist, ulist, incorrectIndices):
    if ( ( (membership(P, Slist, g, pklist, ulist)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        if verify(Lt, pklist, P, g, Mlist[z], ulist[z], Slist[z]) == False:
            incorrectIndices.append(z)
    return incorrectIndices

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('BN256')
    
    (P, g, alpha) = setup()
    (pk, sk) = keygen(alpha, "alice")
    (pk1, sk1) = keygen(alpha, "bob")
    L = ["alice", "bob"]
    (Lt, pklist, u1, S1) = sign("alice", L, pk, sk, "message1")
    (Lt, pklist, u2, S2) = sign("bob", L, pk1, sk1, "message2")
    Mlist = ["message1", "message2"]
    Slist = [S1, S2]
    ulist = [u1, u2]
    incorrectIndices = []
    batchverify(Lt, Mlist, P, Slist, g, pklist, ulist, incorrectIndices)
    print(incorrectIndices)
if __name__ == '__main__':
    main()

