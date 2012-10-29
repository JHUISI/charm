from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits
import math

group = None

N = 2

secparam = 80

"""
h1 = {}
w1 = {}
z1 = {}
d = {}
a = {}
n = {}
u = {}
v = {}
"""

def setup():

    input = None
    g1 = group.random(G1)
    g2 = group.random(G2)
    output = (g1, g2)
    return output

def keygen(g1, g2):
    """
    global h1
    global w1
    global z1
    global d
    global a
    global u
    global v
    """
    input = [g1, g2]
    a = group.random(ZR)
    A = (g2 ** a)
    u = group.random(G1)
    v = group.random(G1)
    d = group.random(G1)
    U = pair(u, A)
    V = pair(v, A)
    D = pair(d, A)
    w = group.random(ZR)
    z = group.random(ZR)
    h = group.random(ZR)
    w1 = (g1 ** w)
    w2 = (g2 ** w)
    z1 = (g1 ** z)
    z2 = (g2 ** z)
    h1 = (g1 ** h)
    h2 = (g2 ** h)
    i = 0
    pk = [U, V, D, g1, g2, w1, w2, z1, z2, h1, h2, u, v, d, i]
    sk = a
    output = (pk, sk)
    return output

def sign(pk, sk, i, m):
    """
    global n
    """
    input = [pk, sk, i, m]
    U, V, D, g1, g2, w1, w2, z1, z2, h1, h2, u, v, d, i = pk
    a = sk
    i = (i + 1)
    M = group.hash(m, ZR)
    r = group.random(ZR)
    t = group.random(ZR)
    n = ceillog(2, i)

    sig1 = ((((u ** M) * ((v ** r) * d)) ** a) * (((w1 ** n) * ((z1 ** i) * h1)) ** t))
    sig2 = (g1 ** t)
    output = (sig1, sig2, r, i)
    return output

def verify(U, V, D, g2, w2, z2, h2, m, sig1, sig2, r, i):
    """global n"""

    input = [U, V, D, g2, w2, z2, h2, m, sig1, sig2, r, i]
    M = group.hash(m, ZR)
    n = ceillog(2, i)
    if ( ( (pair(sig1, g2)) == (((U ** M) * ((V ** r) * (D * pair(sig2, ((w2 ** n) * ((z2 ** i) * h2))))))) ) ):
        output = True
    else:
        output = False
        return output
    return output

def membership(D, Mlist, U, V, g2, h2, ilist, rlist, sig1list, sig2list, w2, z2):

    input = [D, Mlist, U, V, g2, h2, ilist, rlist, sig1list, sig2list, w2, z2]
    if ( ( (group.ismember(D)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(Mlist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(U)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(V)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(h2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(ilist)) == (False) ) ):
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

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotECache, dotFCache, dotGCache, sumBCache, sumCCache, sumDCache, g2, U, V, D, w2, z2, h2):

    input = [delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotECache, dotFCache, dotGCache, sumBCache, sumCCache, sumDCache, g2, U, V, D, w2, z2, h2]
    dotALoopVal = 1
    dotELoopVal = 1
    dotFLoopVal = 1
    dotGLoopVal = 1
    sumBLoopVal = 0
    sumCLoopVal = 0
    sumDLoopVal = 0
    for z in range(startSigNum, endSigNum):
        dotALoopVal = (dotALoopVal * dotACache[z])
        dotELoopVal = (dotELoopVal * dotECache[z])
        dotFLoopVal = (dotFLoopVal * dotFCache[z])
        dotGLoopVal = (dotGLoopVal * dotGCache[z])
        sumBLoopVal = (sumBLoopVal + sumBCache[z])
        sumCLoopVal = (sumCLoopVal + sumCCache[z])
        sumDLoopVal = (sumDLoopVal + sumDCache[z])
    if ( ( (pair(dotALoopVal, g2)) == (((U ** sumBLoopVal) * ((V ** sumCLoopVal) * ((D ** sumDLoopVal) * (pair(dotELoopVal, w2) * (pair(dotFLoopVal, z2) * pair(dotGLoopVal, h2))))))) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotACache, dotECache, dotFCache, dotGCache, sumBCache, sumCCache, sumDCache, g2, U, V, D, w2, z2, h2)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotECache, dotFCache, dotGCache, sumBCache, sumCCache, sumDCache, g2, U, V, D, w2, z2, h2)
    output = None

def batchverify(D, mlist, U, V, g2, h2, ilist, rlist, sig1list, sig2list, w2, z2, incorrectIndices):
    """global n"""

    dotGCache = {}
    dotFCache = {}
    dotECache = {}
    delta = {}
    sumDCache = {}
    sumCCache = {}
    sumBCache = {}
    dotACache = {}

    input = [D, mlist, U, V, g2, h2, ilist, rlist, sig1list, sig2list, w2, z2, incorrectIndices]
    for z in range(0, N):
        delta[z] = SmallExp(secparam)
    if ( ( (membership(D, mlist, U, V, g2, h2, ilist, rlist, sig1list, sig2list, w2, z2)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        n = ceillog(2, ilist[z])
        M = group.hash(mlist[z], ZR)
        dotACache[z] = (sig1list[z] ** delta[z])
        dotECache[z] = (sig2list[z] ** (delta[z] * n))
        dotFCache[z] = (sig2list[z] ** (delta[z] * ilist[z]))
        dotGCache[z] = (sig2list[z] ** delta[z])
        sumBCache[z] = (M * delta[z])
        sumCCache[z] = (rlist[z] * delta[z])
        sumDCache[z] = delta[z]
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotECache, dotFCache, dotGCache, sumBCache, sumCCache, sumDCache, g2, U, V, D, w2, z2, h2)
    output = incorrectIndices
    return output

def ceillog(base, value):
    return group.init(ZR, math.ceil(math.log(value, base)))

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))


def main():
    global group
    group = PairingGroup(secparam)

    # note that this is a same signer test    
    (g1, g2) = setup()
    
    (pk, sk) = keygen(g1, g2)
    U, V, D, g1, g2, w1, w2, z1, z2, h1, h2, u, v, d, i = pk
    
    sig1list = {}
    sig2list = {}
    ilist = {}
    rlist = {}
        
    m0 = "message0"
    m1 = "message1"
    (sig1list[0], sig2list[0], rlist[0], ilist[0]) = sign(pk, sk, i, m0)
    (sig1list[1], sig2list[1], rlist[1], ilist[1]) = sign(pk, sk, ilist[0], m1)
    
    assert verify(U, V, D, g2, w2, z2, h2, m0, sig1list[0], sig2list[0], rlist[0], ilist[0]), "failed verification!!"
    assert verify(U, V, D, g2, w2, z2, h2, m1, sig1list[1], sig2list[1], rlist[1], ilist[1]), "failed verification!!"    
    print("Successful Verification!!")

    Mlist = [m0, m1]    
    incorrectIndices = []
    batchverify(D, Mlist, U, V, g2, h2, ilist, rlist, sig1list, sig2list, w2, z2, incorrectIndices)
    print("Incorrect indicies: ", incorrectIndices)

if __name__ == '__main__':
    main()

