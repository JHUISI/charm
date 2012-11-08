from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

l = 3

secparam = 80

dotProd = {}
h = {}
l = {}

def setup():

    input = None
    g = group.random(G2)
    alpha = group.random(ZR)
    P = (g ** alpha)
    output = (P, g, alpha)
    return output

def concat(ID_List):
    global l

    input = ID_List
    L = ""
    l = len(ID_List)
    for y in range(0, l):
        L = (L + ID_List[y])
    output = L
    return output

def keygen(alpha, ID):

    input = [alpha, ID]
    sk = (group.hash(ID, G1) ** alpha)
    pk = group.hash(ID, G1)
    output = (pk, sk)
    return output

def sign(ID, pk, sk, L, M):
    global dotProd
    global h

    h = {}
    u = {}
    pklist = {}

    input = [ID, pk, sk, L, M]
    Lt = concat(L)
    for i in range(0, l):
        if ( ( (ID) != (L[i]) ) ):
            u[i] = group.random(G1)
            h[i] = group.hash((M, Lt, u[i]), ZR)
        else:
            s = i
    r = group.random(ZR)
    for y in range(0, l):
        pklist[y] = group.hash(L[y], G1)
    dotProd = 1
    for i in range(0, l):
        if ( ( (ID) != (L[i]) ) ):
            dotProd = (dotProd * (u[i] * (pklist[i] ** h[i])))
    u[s] = ((pk ** r) * (dotProd ** -1))
    h[s] = group.hash((M, Lt, u[s]), ZR)
    S = (sk ** (h[s] + r))
    output = (Lt, pklist, u, S)
    return output

def verify(Lt, pklist, P, g, M, u, S):
    global dotProd
    global h

    input = [Lt, pklist, P, g, M, u, S]
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

    input = [P, Slist, g, pklist, ulist]
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

    input = [delta, startSigNum, endSigNum, incorrectIndices, dotBCache, dotCCache, P, g]
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
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotBCache, dotCCache, P, g)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotBCache, dotCCache, P, g)
    output = None

def batchverify(Lt, Mlist, P, Slist, g, pklist, ulist, incorrectIndices):
    global h

    dotCCache = {}
    delta = {}
    dotBCache = {}

    input = [Lt, Mlist, P, Slist, g, pklist, ulist, incorrectIndices]
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

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    (P, g, alpha) = setup()
    (pk, sk) = keygen(alpha, "alice")
    L = ["alice", "bob"]
    (Lt, pklist, u1, S1) = sign("alice", pk, sk, L, "message")
    (Lt, pklist, u2, S2) = sign("alice", pk, sk, L, "message2")
    Mlist = ["message", "message2"]
    Slist = [S1, S2]
    ulist = [u1, u2]
    incorrectIndices = []
    batchverify(Lt, Mlist, P, Slist, g, pklist, ulist, incorrectIndices)
    print(incorrectIndices)

if __name__ == '__main__':
    main()

