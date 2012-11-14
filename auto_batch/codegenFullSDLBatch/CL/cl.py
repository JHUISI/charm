from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80

m = {}

def setup():
    g = group.random(G1)
    output = g
    return output

def keygen(g):
    x = group.random(ZR)
    y = group.random(ZR)
    X = (g ** x)
    Y = (g ** y)
    output = (X, Y, x, y)
    return output

def sign(x, y, M):
    a = group.random(G2)
    m = group.hash(M, ZR)
    b = (a ** y)
    c = (a ** (x + (m * (x * y))))
    sig = [a, b, c]
    output = sig
    return output

def verify(X, Y, g, M, a, b, c):
    m = group.hash(M, ZR)
    if ( ( (( (pair(Y, a)) == (pair(g, b)) )) and (( ((pair(X, a) * (pair(X, b) ** m))) == (pair(g, c)) )) ) ):
        output = True
    else:
        output = False
        return output
    return output

def membership(g, alist, clist, blist, Y, X):
    if ( ( (group.ismember(g)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(alist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(clist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(blist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(Y)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(X)) == (False) ) ):
        output = False
        return output
    output = True
    return output

def dividenconquer(delta1, delta2, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g, Y, X):
    dotALoopVal = 1
    dotBLoopVal = 1
    dotCLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotALoopVal = (dotALoopVal * dotACache[z])
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
        dotCLoopVal = (dotCLoopVal * dotCCache[z])
    if ( ( ((pair(g, dotALoopVal) * pair(Y, dotBLoopVal))) == (pair(X, dotCLoopVal)) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta1, delta2, startSigNum, midSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g, Y, X)
        dividenconquer(delta1, delta2, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g, Y, X)
    output = None

def batchverify(g, alist, Mlist, clist, blist, Y, X, incorrectIndices):
    delta1 = {}
    delta2 = {}
    dotCCache = {}
    dotBCache = {}
    dotACache = {}

    for z in range(0, N):
        delta1[z] = SmallExp(secparam)
        delta2[z] = SmallExp(secparam)
    if ( ( (membership(g, alist, clist, blist, Y, X)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        m = group.hash(Mlist[z], ZR)
        dotACache[z] = ((blist[z] ** delta1[z]) * (clist[z] ** delta2[z]))
        dotBCache[z] = (alist[z] ** -delta1[z])
        dotCCache[z] = ((alist[z] ** delta2[z]) * (blist[z] ** (m * delta2[z])))
    dividenconquer(delta1, delta2, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, g, Y, X)
    output = incorrectIndices
    return output

def indivverify(g, alist, Mlist, clist, blist, Y, X, incorrectIndices):
    if ( ( (membership(g, alist, clist, blist, Y, X)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        if verify(X, Y, g, Mlist[z], alist[z], blist[z], clist[z]) == False:
            incorrectIndices.append(z)
    return incorrectIndices

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('BN256')
    g = setup()
    (X, Y, x, y) = keygen(g)
    Mlist = ["mess1", "mess2"]
    sig0 = sign(x, y, Mlist[0])
    sig1 = sign(x, y, Mlist[1])
    print(verify(X, Y, g, Mlist[0], sig0[0], sig0[1], sig0[2]))
    alist = [sig0[0], sig1[0]]
    blist = [sig0[1], sig1[1]]
    clist = [sig0[2], sig1[2]]
    incorrectIndices = []
    batchverify(g, alist, Mlist, clist, blist, Y, X, incorrectIndices)
    print(incorrectIndices)
    

if __name__ == '__main__':
    main()

