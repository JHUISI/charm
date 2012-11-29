from charm.toolbox.pairinggroup import * #PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits
import random

group = None

N = 2

l = 8

secparam = 80


def setup(n):
    u = {}
    U = {}

    g1 = group.random(G1)
    g2 = group.random(G2)
    hExp = group.random(ZR)
    ub = group.random(ZR)
    h = (g2 ** hExp)
    Ub = (g2 ** ub)
    for i in range(0, n+1):
        u[i] = group.random(ZR)
    U0 = (g2 ** u[0])
    U1 = (g1 ** u[1])
    for i in range(1, n+1):
        U[i] = (g2 ** u[i])
    pk = [Ub, g1, g2, h]
    sk = [ub, g1, h]
    output = (pk, U0, U1, U, sk, u)
    return output

def polyF(sk, u, x):
    ut, g1, h = sk
    dotProd = 1
    for i in range(1, l+1):
        dotProd = (dotProd * (u[i] ** x[i]))
    result0 = pair((g1 ** ((ut * u[0]) * dotProd)), h)
    output = result0
    return output

def prove(sk, u, x):
    pi = {}

    ut, g1, h = sk
    for i in range(1, l+1):
        dotProd0 = 1
        for j in range(1, i+1):
            dotProd0 = (dotProd0 * (u[j] ** x[j]))
        pi[i] = (g1 ** (ut * dotProd0))
    dotProd1 = 1
    for i in range(1, l+1):
        dotProd1 = (dotProd1 * (u[i] ** x[i]))
    pi[0] = (g1 ** (ut * (u[0] * dotProd1)))
    y0 = polyF(sk, u, x)
    output = (y0, pi)
    return output

def verify(U0, U1, U, Ub, g1, g2, h, y0, pi, x):
    proof0 = pair(pi[1], g2)
    if ( ( (( (x[1]) == (0) )) and (( (proof0) != (pair(g1, Ub)) )) ) ):
        output = False
        return output
    if ( ( (( (x[1]) == (1) )) and (( (proof0) != (pair(U1, Ub)) )) ) ):
        output = False
        return output
    if ( ( (( (x[1]) != (0) )) and (( (x[1]) != (1) )) ) ):
        output = False
        return output
    for i in range(2, l+1):
        proof1 = pair(pi[i], g2)
        if ( ( (( (x[i]) == (0) )) and (( (proof1) != (pair(pi[i-1], g2)) )) ) ):
            output = False
            return output
        if ( ( (( (x[i]) == (1) )) and (( (proof1) != (pair(pi[i-1], U[i])) )) ) ):
            output = False
            return output
        if ( ( (( (x[i]) != (0) )) and (( (x[i]) != (1) )) ) ):
            output = False
            return output
    if ( ( (pair(pi[0], g2)) != (pair(pi[l], U0)) ) ):
        output = False
        return output
    if ( ( (pair(pi[0], h)) != (y0) ) ):
        output = False
        return output
    output = True
    return output

def membership(U, U0, U1, Ub, g1, g2, h, pilist, y0list):
    assert group.ismemberDict(U), "failed membership test"
    assert group.ismember(U0), "failed membership test"
    assert group.ismember(U1), "failed membership test"
    assert group.ismember(Ub), "failed membership test"
    assert group.ismember(g1), "failed membership test"
    assert group.ismember(g2), "failed membership test"
    assert group.ismember(h), "failed membership test"
    for z in range(len(y0list)):
        assert group.ismember(y0list[z]), "failed membership test"
    for z in range(len(pilist)):
        assert group.ismemberList(pilist[z]), "failed membership test"
    return True

def dividenconquer(delta1, delta2, delta3, delta4, delta5, delta6, delta7, delta8, delta9, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, Ub, g2, U0, h, U):
    dotALoopVal = 1
    dotBLoopVal = 1
    dotCLoopVal = 1
    dotDLoopVal = 1
    dotELoopVal = 1
    dotFLoopVal = 1
    dotGLoopVal = 1
    dotHLoopVal = 1
    dotILoopVal = 1
    dotJLoopVal = 1
    dotKLoopVal = 1
    dotLLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotALoopVal = (dotALoopVal * dotACache[z])
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
        dotCLoopVal = (dotCLoopVal * dotCCache[z])
        dotDLoopVal = (dotDLoopVal * dotDCache[z])
        dotELoopVal = (dotELoopVal * dotECache[z])
        dotFLoopVal = (dotFLoopVal * dotFCache[z])
        dotGLoopVal = (dotGLoopVal * dotGCache[z])
        dotHLoopVal = (dotHLoopVal * dotHCache[z])
        dotILoopVal = (dotILoopVal * dotICache[z])
        dotJLoopVal = (dotJLoopVal * dotJCache[z])
        dotKLoopVal = (dotKLoopVal * dotKCache[z])
        dotLLoopVal = (dotLLoopVal * dotLCache[z])
    if ( ( ((pair(dotALoopVal, Ub) * pair(dotBLoopVal, g2))) == (((pair(dotCLoopVal, U0) * (dotDLoopVal * pair(dotELoopVal, (g2 * (h ** -1))))) * ((((((pair(dotFLoopVal, U[2]) * pair(dotGLoopVal, U[3])) * pair(dotHLoopVal, U[4])) * pair(dotILoopVal, U[5])) * pair(dotJLoopVal, U[6])) * pair(dotKLoopVal, U[7])) * pair(dotLLoopVal, U[8])))) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta1, delta2, delta3, delta4, delta5, delta6, delta7, delta8, delta9, startSigNum, midSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, Ub, g2, U0, h, U)
        dividenconquer(delta1, delta2, delta3, delta4, delta5, delta6, delta7, delta8, delta9, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, Ub, g2, U0, h, U)
    output = None

def batchverify(U, U0, U1, Ub, g1, g2, h, pilist, xlist, y0list, incorrectIndices):
    dotLCache = {}
    dotKCache = {}
    dotDCache = {}
    dotJCache = {}
    dotECache = {}
    dotICache = {}
    dotBCache = {}
    delta1 = {}
    delta2 = {}
    delta3 = {}
    delta4 = {}
    delta5 = {}
    delta6 = {}
    delta7 = {}
    delta8 = {}
    delta9 = {}
    dotHCache = {}
    dotGCache = {}
    dotACache = {}
    dotFCache = {}
    dotCCache = {}

    for z in range(0, N):
        delta1[z] = SmallExp(secparam)
        delta2[z] = SmallExp(secparam)
        delta3[z] = SmallExp(secparam)
        delta4[z] = SmallExp(secparam)
        delta5[z] = SmallExp(secparam)
        delta6[z] = SmallExp(secparam)
        delta7[z] = SmallExp(secparam)
        delta8[z] = SmallExp(secparam)
        delta9[z] = SmallExp(secparam)
    if ( ( (membership(U, U0, U1, Ub, g1, g2, h, pilist, y0list)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        dotACache[z] = ((g1 ** ((1 - xlist[z][1]) * delta1[z])) * (U1 ** (xlist[z][1] * delta1[z])))
        dotBCache[z] = ((pilist[z][1] ** -delta1[z]) * ((((((((pilist[z][2] ** delta3[z]) * (pilist[z][1] ** ((1 - xlist[z][2]) * -delta3[z]))) * ((pilist[z][3] ** -delta4[z]) * (pilist[z][2] ** (((1 - xlist[z][3]) * -delta4[z]) * -1)))) * ((pilist[z][4] ** -delta5[z]) * (pilist[z][3] ** (((1 - xlist[z][4]) * -delta5[z]) * -1)))) * ((pilist[z][5] ** -delta6[z]) * (pilist[z][4] ** (((1 - xlist[z][5]) * -delta6[z]) * -1)))) * ((pilist[z][6] ** -delta7[z]) * (pilist[z][5] ** (((1 - xlist[z][6]) * -delta7[z]) * -1)))) * ((pilist[z][7] ** -delta8[z]) * (pilist[z][6] ** (((1 - xlist[z][7]) * -delta8[z]) * -1)))) * ((pilist[z][8] ** -delta9[z]) * (pilist[z][7] ** (((1 - xlist[z][8]) * -delta9[z]) * -1)))))
        dotCCache[z] = (pilist[z][l] ** delta2[z])
        dotDCache[z] = (y0list[z] ** -delta2[z])
        dotECache[z] = (pilist[z][0] ** -delta2[z])
        dotFCache[z] = (pilist[z][1] ** (xlist[z][2] * delta3[z]))
        dotGCache[z] = ((pilist[z][2] ** (xlist[z][3] * delta4[z])) ** -1)
        dotHCache[z] = ((pilist[z][3] ** (xlist[z][4] * delta5[z])) ** -1)
        dotICache[z] = ((pilist[z][4] ** (xlist[z][5] * delta6[z])) ** -1)
        dotJCache[z] = ((pilist[z][5] ** (xlist[z][6] * delta7[z])) ** -1)
        dotKCache[z] = ((pilist[z][6] ** (xlist[z][7] * delta8[z])) ** -1)
        dotLCache[z] = ((pilist[z][7] ** (xlist[z][8] * delta9[z])) ** -1)
    dividenconquer(delta1, delta2, delta3, delta4, delta5, delta6, delta7, delta8, delta9, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, Ub, g2, U0, h, U)
    output = incorrectIndices
    return output

def indivverify(U, U0, U1, Ub, g1, g2, h, pilist, xlist, y0list, incorrectIndices):
    for z in range(0, N):
        assert group.ismemberDict(U), "failed membership test"
        assert group.ismember(U0), "failed membership test"
        assert group.ismember(U1), "failed membership test"
        assert group.ismember(Ub), "failed membership test"
        assert group.ismember(g1), "failed membership test"
        assert group.ismember(g2), "failed membership test"
        assert group.ismember(h), "failed membership test"
        assert group.ismember(y0list[z]), "failed membership test"
        assert group.ismemberList(pilist[z]), "failed membership test"
        if verify(U0, U1, U, Ub, g1, g2, h, y0list[z], pilist[z], xlist[z]) == False:
           incorrectIndices.append(z)
    return incorrectIndices  
 
def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('BN256')
    (pk, U0, U1, U, sk, u) = setup(l)
    [Ub, g1, g2, h] = pk

#    print("current dir...")
#    print(dir())

    x0 = {}
    x1 = {}
    for i in range(1, l+1):
        x0[ i ] = random.randint(0, 1)
        x1[ i ] = random.randint(0, 1)

    print("x0 :=", list(x0.values()))
    print("x1 :=", list(x1.values()))
        
    (y0, pi0) = prove(sk, u, x0)
    (y1, pi1) = prove(sk, u, x1)
    assert verify(U0, U1, U, Ub, g1, g2, h, y0, pi0, x0), "VRF failed verification"
    assert verify(U0, U1, U, Ub, g1, g2, h, y1, pi1, x1), "VRF failed verification"
    print("Successful Verification!!")

    pilist = [pi0, pi1]
    y0list = [y0, y1]
    xlist =  [x0, x1]
    incorrectIndices = []
    assert batchverify(U, U0, U1, Ub, g1, g2, h, pilist, xlist, y0list, incorrectIndices) != False, "invalid batch verification"
    print("incorrectIndices: ", incorrectIndices)

if __name__ == '__main__':
    main()

