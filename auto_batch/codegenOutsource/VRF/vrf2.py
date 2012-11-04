from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 1

l = 4

secparam = 80

ut = {}

def setup(n):
    #global ut

    U1 = {}
    U2 = {}
    u = {}

    input = [n]
    g1 = group.random(G1)
    g2 = group.random(G2)
    h = group.random(G2)
    ut = group.random(ZR)
    Ut = (g2 ** ut)
    for i in range(0, n+1):
        u[i] = group.random(ZR)
    for i in range(0, n):
        U1[i] = (g1 ** u[i])
        U2[i] = (g2 ** u[i])
    pk = [Ut, g1, g2, h]
    sk = [ut, g1, h]
    output = (pk, U1, U2, sk, u)
    return output

def polyF(sk, u, x):

    input = [sk, u, x]
    ut, g1, h = sk
    dotProd = 1
    for i in range(0, l):
        dotProd = (dotProd * (u[i] ** x[i]))
    result0 = pair((g1 ** ((ut * u[0]) * dotProd)), h)
    output = result0
    return output

def prove(sk, u, x):

    pi = {}

    input = [sk, u, x]
    ut, g1, h = sk
    for i in range(0, l):
        dotProd0 = 1
        for j in range(0, i+1):
            dotProd0 = (dotProd0 * (u[j] ** x[j]))
        pi[i+1] = (g1 ** (ut * dotProd0))
    dotProd1 = 1
    for i in range(0, l):
        dotProd1 = (dotProd1 * (u[i] ** x[i]))
    pi[0] = (g1 ** (ut * (u[0] * dotProd1)))
    y0 = polyF(sk, u, x)
    output = (y0, pi)
    return output

def verify(U1, U2, Ut, g1, g2, h, y0, pi, x):

    input = [U1, U2, Ut, g1, g2, h, y0, pi, x]
    proof0 = pair(pi[1], g2)
    if ( ( (( (x[0]) == (0) )) and (( (proof0) != (pair(g1, Ut)) )) ) ):
        output = False
        return output
    if ( ( (( (x[0]) == (1) )) and (( (proof0) != (pair(U1[0], Ut)) )) ) ):
        output = False
        return output
    if ( ( (( (x[0]) != (0) )) and (( (x[0]) != (1) )) ) ):
        output = False
        return output
    for i in range(2, l+1):
        proof1 = pair(pi[i], g2)
        if ( ( (( (x[i-1]) == (0) )) and (( (proof1) != (pair(pi[i-1], g2)) )) ) ):
            output = False
            return output
        if ( ( (( (x[i-1]) == (1) )) and (( (proof1) != (pair(pi[i-1], U2[i-1])) )) ) ):
            output = False
            return output
        if ( ( (( (x[i-1]) != (0) )) and (( (x[i-1]) != (1) )) ) ):
            output = False
            return output
    if ( ( (pair(pi[0], (g2 * h))) != ((pair(pi[l], U2[0]) * y0)) ) ):
        output = False
        return output
    output = True
    return output

def membership(U1, U2, Ut, g1, g2, h, pilist, xlist, y0list):

    input = [U1, U2, Ut, g1, g2, h, pilist, xlist, y0list]
    if ( ( (group.ismember(U1)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(U2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(Ut)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g1)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(h)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(pilist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(xlist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(y0list)) == (False) ) ):
        output = False
        return output
    output = True
    return output

def dividenconquer(delta, delta1, delta3, delta2, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, Ut, g2, U2, h):

    input = [delta1, delta3, delta2, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, Ut, g2, U2, h]
    dotALoopVal = 1
    dotBLoopVal = 1
    dotCLoopVal = 1
    dotDLoopVal = 1
    dotELoopVal = 1
    dotFLoopVal = 1
    dotGLoopVal = 1
    dotHLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotALoopVal = (dotALoopVal * dotACache[z])
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
        dotCLoopVal = (dotCLoopVal * dotCCache[z])
        dotDLoopVal = (dotDLoopVal * dotDCache[z])
        dotELoopVal = (dotELoopVal * dotECache[z])
        dotFLoopVal = (dotFLoopVal * dotFCache[z])
        dotGLoopVal = (dotGLoopVal * dotGCache[z])
        dotHLoopVal = (dotHLoopVal * dotHCache[z])
    if ( ( ((pair(dotALoopVal, Ut) * pair(dotBLoopVal, g2))) == (((pair(dotCLoopVal, U2[0]) * (pair(dotDLoopVal, (~g2 * h)) * dotELoopVal)) * ((pair(dotFLoopVal ** -1, U2[1])) * (pair(dotGLoopVal, U2[2]) * pair(dotHLoopVal, U2[3]))))) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, delta1, delta3, delta2, startSigNum, midway, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, Ut, g2, U2, h)
        dividenconquer(delta, delta1, delta3, delta2, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, Ut, g2, U2, h)
    output = None

def batchverify(U1, U2, Ut, g1, g2, h, pilist, xlist, y0list, incorrectIndices):
    delta = {}
    delta1 = {}
    delta2 = {}
    delta3 = {}
    dotFCache = {}
    dotECache = {}
    dotDCache = {}
    dotCCache = {}
    dotHCache = {}
    dotBCache = {}
    dotGCache = {}
    dotACache = {}

    input = [U1, U2, Ut, g1, g2, h, pilist, xlist, y0list, incorrectIndices]
    for z in range(0, N):
        delta[z] = SmallExp(secparam)        
        delta1[z] = SmallExp(secparam)
        delta3[z] = SmallExp(secparam)
        delta2[z] = SmallExp(secparam)
#    if ( ( (membership(U1, U2, Ut, g1, g2, h, pilist, xlist, y0list)) == (False) ) ):
#        output = False
#        return output
    for z in range(0, N):
        dotACache[z] = ((g1 ** ((1 - xlist[z][0]) * delta1[z])) * (U1[0] ** (xlist[z][0] * delta1[z])))
        dotBCache[z] = ((pilist[z][1] ** -delta1[z]) * ((pilist[z][2] ** -delta[z]) * ((pilist[z][1] ** (((1 - xlist[z][1]) * -delta[z]) * -1)) * ((((pilist[z][3] ** delta[z]) * (pilist[z][2] ** ((1 - xlist[z][2]) * -delta[z]))) ** -1) * (((pilist[z][4] ** delta[z]) * (pilist[z][3] ** ((1 - xlist[z][3]) * -delta[z]))) ** -1)))))
        dotCCache[z] = (pilist[z][l] ** delta2[z])
        dotDCache[z] = (pilist[z][0] ** -delta2[z])
        dotECache[z] = (y0list[z] ** -delta3[z])
        dotFCache[z] = (pilist[z][1] ** (xlist[z][1] * delta[z]))
        dotGCache[z] = (pilist[z][2] ** (xlist[z][2] * delta[z]))
        dotHCache[z] = (pilist[z][3] ** (xlist[z][3] * delta[z]))
    dividenconquer(delta, delta1, delta3, delta2, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, Ut, g2, U2, h)
    output = incorrectIndices
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup("MNT224")

    (pk, U1, U2, sk, u) = setup(l)
    Ut, g1, g2, h = pk
#    print("pk :=", pk)
    
    x = [1, 0, 1, 0]
    x1 = [1, 0, 1, 1]    
    (y0, pi) = prove(sk, u, x)
    assert verify(U1, U2, Ut, g1, g2, h, y0, pi, x), "VRF failed verification"
    print("Successful Verification!!")
    
    pilist = [pi]
    y0list = [y0]
    xlist = [x]
    incorrectIndices = []
    assert batchverify(U1, U2, Ut, g1, g2, h, pilist, xlist, y0list, incorrectIndices), "invalid batch verification"
    print("incorrectIndices: ", incorrectIndices)
if __name__ == '__main__':
    main()

