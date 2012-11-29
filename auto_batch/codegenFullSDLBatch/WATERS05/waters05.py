from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits
from builtinFuncs import stringToInt

group = None

N = 2

l = 5
zz = 32
secparam = 80
"""
zz = {}
u2t = {}
k2 = {}
k1 = {}
g1 = {}
k = {}
m = {}
l = {}
u1t = {}
"""
def setup():
    y0 = {}
    u = {}
    ub = {}

    alpha = group.random(ZR)
    h = group.random(G1)
    g1 = group.random(G1)
    g2 = group.random(G2)
    A = (pair(h, g2) ** alpha)
    for i in range(0, l):
        y0[i] = group.random(ZR)
        u[i] = (g1 ** y0[i])
        ub[i] = (g2 ** y0[i])
    y1t = group.random(ZR)
    y2t = group.random(ZR)
    u1t = (g1 ** y1t)
    u2t = (g1 ** y2t)
    u1b = (g2 ** y1t)
    u2b = (g2 ** y2t)
    msk = (h ** alpha)
    mpk = [g1, g2, A, u1t, u2t, u1b, u2b]
    output = (mpk, u, ub, msk)
    return output

def keygen(mpk, u, msk, ID):
    g1, g2, A, u1t, u2t, u1b, u2b = mpk
    k = stringToInt(group, ID, l, zz)
    dotProd = 1
    for i in range(0, l):
        dotProd = (dotProd * (u[i] ** k[i]))
    r = group.random(ZR)
    k1 = (msk * ((u1t * dotProd) ** r))
    k2 = (g1 ** -r)
    sk = [k1, k2]
    output = sk
    return output

def sign(mpk, u, sk, M):
    g1, g2, A, u1t, u2t, u1b, u2b = mpk
    m = stringToInt(group, M, l, zz)
    k1, k2 = sk
    s = group.random(ZR)
    dotProd1 = 1
    for i in range(0, l):
        dotProd1 = (dotProd1 * (u[i] ** m[i]))
    S1 = (k1 * ((u2t * dotProd1) ** s))
    S2 = k2
    S3 = (g1 ** -s)
    output = (S1, S2, S3)
    return output

def verify(A, g2, ub, u1b, u2b, ID, M, S1, S2, S3):
    kver = stringToInt(group, ID, l, zz)
    mver = stringToInt(group, M, l, zz)
    dotProd2 = 1
    dotProd3 = 1
    for i in range(0, l):
        dotProd2 = (dotProd2 * (ub[i] ** kver[i]))
        dotProd3 = (dotProd3 * (ub[i] ** mver[i]))
    if ( ( ((pair(S1, g2) * (pair(S2, (u1b * dotProd2)) * pair(S3, (u2b * dotProd3))))) == (A) ) ):
        output = True
    else:
        output = False
        return output
    return output

def membership(A, S1list, S2list, S3list, g2, u1b, u2b, ub):
    if ( ( (group.ismember(A)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismemberList(S1list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismemberList(S2list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismemberList(S3list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(u1b)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(u2b)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismemberList(ub)) == (False) ) ):
        output = False
        return output
    output = True
    return output

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotBCache, dotACache, sumECache, dotDCache, A, IDlist, Mlist, S1list, S2list, S3list, g2, u1b, u2b, ub):
    dotBLoopVal = 1
    dotALoopVal = 1
    sumELoopVal = 0
    dotDLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
        dotALoopVal = (dotALoopVal * dotACache[z])
        sumELoopVal = (sumELoopVal + sumECache[z])
        dotDLoopVal = (dotDLoopVal * dotDCache[z])
    dotFLoopVal = 1
    for y in range(0, l):
        dotCLoopVal = 1
        for z in range(startSigNum, endSigNum):
            k = stringToInt(group, IDlist[z], l, zz)
            m = stringToInt(group, Mlist[z], l, zz)
            dotCLoopVal = (dotCLoopVal * ((S2list[z] ** (delta[z] * k[y])) * (S3list[z] ** (delta[z] * m[y]))))
        dotFLoopVal = (dotFLoopVal * pair(dotCLoopVal, ub[y]))
    if ( ( ((pair(dotALoopVal, g2) * ((pair(dotBLoopVal, u1b) * dotFLoopVal) * pair(dotDLoopVal, u2b)))) == ((A ** sumELoopVal)) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, startSigNum, midSigNum, incorrectIndices, dotBCache, dotACache, sumECache, dotDCache, A, IDlist, Mlist, S1list, S2list, S3list, g2, u1b, u2b, ub)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotBCache, dotACache, sumECache, dotDCache, A, IDlist, Mlist, S1list, S2list, S3list, g2, u1b, u2b, ub)
    output = None

def batchverify(A, IDlist, Mlist, S1list, S2list, S3list, g2, u1b, u2b, ub, incorrectIndices):
    dotDCache = {}
    delta = {}
    sumECache = {}
    dotBCache = {}
    dotACache = {}

    for z in range(0, N):
        delta[z] = SmallExp(secparam)
    if ( ( (membership(A, S1list, S2list, S3list, g2, u1b, u2b, ub)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        dotBCache[z] = (S2list[z] ** delta[z])
        dotACache[z] = (S1list[z] ** delta[z])
        sumECache[z] = delta[z]
        dotDCache[z] = (S3list[z] ** delta[z])
    dividenconquer(delta, 0, N, incorrectIndices, dotBCache, dotACache, sumECache, dotDCache, A, IDlist, Mlist, S1list, S2list, S3list, g2, u1b, u2b, ub)
    output = incorrectIndices
    return output

def indivverify(A, IDlist, Mlist, S1list, S2list, S3list, g2, u1b, u2b, ub, incorrectIndices):
    if ( ( (membership(A, S1list, S2list, S3list, g2, u1b, u2b, ub)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        if verify(A, g2, ub, u1b, u2b, IDlist[z], Mlist[z], S1list[z], S2list[z], S3list[z]) == False:
            incorrectIndices.append(z)
    return incorrectIndices

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('BN256')
    (mpk, u, ub, msk) = setup()

    IDlist = {}
    S1list = {}
    S2list = {}
    S3list = {}

    IDlist[0] = "janedoe@gmail.com"
    IDlist[1] = "gijoe@email.com"
    sk0 = keygen(mpk, u, msk, IDlist[0])
    sk1 = keygen(mpk, u, msk, IDlist[1])

    M0 = "my message 0."
    M1 = "my message 1."
    Mlist = [M0, M1]
    S1list[0], S2list[0], S3list[0] = sign(mpk, u, sk0, M0) # mpk, u, sk, M
    S1list[1], S2list[1], S3list[1] = sign(mpk, u, sk1, M1)

    g1, g2, A, u1t, u2t, u1b, u2b = mpk
    assert verify(A, g2, ub, u1b, u2b, IDlist[0], M0, S1list[0], S2list[0], S3list[0]), "failed verification!"
    assert verify(A, g2, ub, u1b, u2b, IDlist[1], M1, S1list[1], S2list[1], S3list[1]), "failed verification!"
    print("Successful Verification!")

    incorrectIndices = []
    batchverify(A, IDlist, Mlist, S1list, S2list, S3list, g2, u1b, u2b, ub, incorrectIndices)
    print("Incorrect indices: ", incorrectIndices)

if __name__ == '__main__':
    main()

