from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits
import math

group = None

N = 2

secparam = 80

def ceillog(base, value):
    return group.init(ZR, math.ceil(math.log(value, base)))

def setup():
    g1 = group.random(G1)
    g2 = group.random(G2)
    u = group.random(G1)
    v = group.random(G1)
    d = group.random(G1)
    w = group.random(ZR)
    z = group.random(ZR)
    h = group.random(ZR)    
    w1 = (g1 ** w)
    w2 = (g2 ** w)
    z1 = (g1 ** z)
    z2 = (g2 ** z)
    h1 = (g1 ** h)
    h2 = (g2 ** h)    
    mpk = [g1, g2, w1, w2, z1, z2, h1, h2, u, v, d]
    output = mpk
    return output

def keygen(g2, u, v, d):
    a = group.random(ZR)
    A = (g2 ** a)
    U = pair(u, A)
    V = pair(v, A)
    D = pair(d, A)
    i = 0
    pk = [U, V, D]
    sk = a
    output = (i, pk, sk)
    return output

def sign(mpk, pk, sk, i, m):
    g1, g2, w1, w2, z1, z2, h1, h2, u, v, d = mpk
    U, V, D = pk
    i = (i + 1)
    M = group.hash(m, ZR)
    r = group.random(ZR)
    t = group.random(ZR)
    n = ceillog(2, i)
    sig1 = ((((u ** M) * ((v ** r) * d)) ** sk) * (((w1 ** n) * ((z1 ** i) * h1)) ** t))
    sig2 = (g1 ** t)
    output = (sig1, sig2, r, i)
    return output

def verify(U, V, D, g2, w2, z2, h2, m, sig1, sig2, r, i):
    M = group.hash(m, ZR)
    n = ceillog(2, i)
    if ( ( (pair(sig1, g2)) == (((U ** M) * ((V ** r) * (D * pair(sig2, ((w2 ** n) * ((z2 ** i) * h2))))))) ) ):
        output = True
    else:
        output = False
        return output
    return output

def membership(Dlist, Ulist, Vlist, g2, h2, rlist, sig1list, sig2list, w2, z2):
    if ( ( (group.ismember(Dlist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(Ulist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(Vlist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(h2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(rlist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(sig1list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(sig2list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(w2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(z2)) == (False) ) ):
        output = False
        return output
    output = True
    return output

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, g2, w2, z2, h2):
    dotALoopVal = 1
    dotBLoopVal = 1
    dotCLoopVal = 1
    dotDLoopVal = 1
    dotELoopVal = 1
    dotFLoopVal = 1
    dotGLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotALoopVal = (dotALoopVal * dotACache[z])
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
        dotCLoopVal = (dotCLoopVal * dotCCache[z])
        dotDLoopVal = (dotDLoopVal * dotDCache[z])
        dotELoopVal = (dotELoopVal * dotECache[z])
        dotFLoopVal = (dotFLoopVal * dotFCache[z])
        dotGLoopVal = (dotGLoopVal * dotGCache[z])
    if ( ( (pair(dotALoopVal, g2)) == ((dotBLoopVal * (dotCLoopVal * (dotDLoopVal * (pair(dotELoopVal, w2) * (pair(dotFLoopVal, z2) * pair(dotGLoopVal, h2))))))) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, startSigNum, midSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, g2, w2, z2, h2)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, g2, w2, z2, h2)
    output = None

def batchverify(Dlist, Ulist, Vlist, g2, h2, ilist, mlist, rlist, sig1list, sig2list, w2, z2, incorrectIndices):
    dotGCache = {}
    dotCCache = {}
    dotFCache = {}
    dotECache = {}
    dotDCache = {}
    delta = {}
    dotBCache = {}
    dotACache = {}

    for z in range(0, N):
        delta[z] = SmallExp(secparam)
    if ( ( (membership(Dlist, Ulist, Vlist, g2, h2, rlist, sig1list, sig2list, w2, z2)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        M = group.hash(mlist[z], ZR)
        n = ceillog(2, ilist[z])
        dotACache[z] = (sig1list[z] ** delta[z])
        dotBCache[z] = (Ulist[z] ** (M * delta[z]))
        dotCCache[z] = (Vlist[z] ** (rlist[z] * delta[z]))
        dotDCache[z] = (Dlist[z] ** delta[z])
        dotECache[z] = (sig2list[z] ** (delta[z] * n))
        dotFCache[z] = (sig2list[z] ** (delta[z] * ilist[z]))
        dotGCache[z] = (sig2list[z] ** delta[z])
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, g2, w2, z2, h2)
    output = incorrectIndices
    return output

def indivverify(Dlist, Ulist, Vlist, g2, h2, ilist, mlist, rlist, sig1list, sig2list, w2, z2, incorrectIndices):
    if ( ( (membership(Dlist, Ulist, Vlist, g2, h2, rlist, sig1list, sig2list, w2, z2)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        if verify(Ulist[z], Vlist[z], Dlist[z], g2, w2, z2, h2, mlist[z], sig1list[z], sig2list[z], rlist[z], ilist[z]) == False:
            incorrectIndices.append(z)
    return incorrectIndices

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('BN256')
    mpk = setup()
    g1, g2, w1, w2, z1, z2, h1, h2, u, v, d = mpk
    (i0, pk0, sk0) = keygen(g2, u, v, d)
    (i1, pk1, sk1) = keygen(g2, u, v, d)
    Ulist = {}
    Vlist = {}
    Dlist = {}
    Ulist[0], Vlist[0], Dlist[0] = pk0
    Ulist[1], Vlist[1], Dlist[1] = pk1
    
    sig1list = {}
    sig2list = {}
    ilist = {}
    rlist = {}
        
    m0 = "message0"
    m1 = "message1"
    (sig1list[0], sig2list[0], rlist[0], ilist[0]) = sign(mpk, pk0, sk0, i0, m0)
    (sig1list[1], sig2list[1], rlist[1], ilist[1]) = sign(mpk, pk1, sk1, i1, m1)
    
    assert verify(Ulist[0], Vlist[0], Dlist[0], g2, w2, z2, h2, m0, sig1list[0], sig2list[0], rlist[0], ilist[0]), "failed verification!!"
    assert verify(Ulist[1], Vlist[1], Dlist[1], g2, w2, z2, h2, m1, sig1list[1], sig2list[1], rlist[1], ilist[1]), "failed verification!!"
    print("Successful Verification!!")

    Mlist = [m0, m1]
    incorrectIndices = batchverify(Dlist, Ulist, Vlist, g2, h2, ilist, Mlist, rlist, sig1list, sig2list, w2, z2, [])
    print("Incorrect indicies: ", incorrectIndices)    

if __name__ == '__main__':
    main()

