from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80


def precheck(g1, g2, h, u, v, w, M, T1, T2, T3, c, salpha, sbeta, sx, sgamma1, sgamma2, R3):

    input = [g1, g2, h, u, v, w, M, T1, T2, T3, c, salpha, sbeta, sx, sgamma1, sgamma2, R3]
    R1ver = ((u ** salpha) * (T1 ** -c))
    R2ver = ((v ** sbeta) * (T2 ** -c))
    R4ver = ((T1 ** sx) * (u ** -sgamma1))
    R5ver = ((T2 ** sx) * (v ** -sgamma2))
    if ( ( (c) != (group.hash((M, T1, T2, T3, R1ver, R2ver, R3, R4ver, R5ver), ZR)) ) ):
        output = False
    else:
        output = True
    return output

def keygen(n):

    A = {}
    x = {}

    input = n
    g1 = group.random(G1)
    g2 = group.random(G2)
    h = group.random(G1)
    xi1 = group.random(ZR)
    xi2 = group.random(ZR)
    u = (h ** (1 / xi1))
    v = (h ** (1 / xi2))
    gamma = group.random(ZR)
    w = (g2 ** gamma)
    gpk = [g1, g2, h, u, v, w]
    gmsk = [xi1, xi2]
    for y in range(0, n):
        x[y] = group.random(ZR)
        A[y] = (g1 ** (1 / (gamma + x[y])))
    output = (gpk, gmsk, A, x)
    return output

def sign(gpk, A_ind, x_ind, M):

    r = {}

    input = [gpk, A_ind, x_ind, M]
    g1, g2, h, u, v, w = gpk
    alpha = group.random(ZR)
    beta = group.random(ZR)
    T1 = (u ** alpha)
    T2 = (v ** beta)
    T3 = (A_ind * (h ** (alpha + beta)))
    gamma1 = (x_ind * alpha)
    gamma2 = (x_ind * beta)
    r[0] = group.random(ZR)
    r[1] = group.random(ZR)
    r[2] = group.random(ZR)
    r[3] = group.random(ZR)
    r[4] = group.random(ZR)
    r[5] = group.random(ZR)
    R1 = (u ** r[0])
    R2 = (v ** r[1])
    R3 = ((pair(T3, g2) ** r[2]) * ((pair(h, w) ** (-r[0] - r[1])) * (pair(h, g2) ** (-r[3] - r[4]))))
    R4 = ((T1 ** r[2]) * (u ** -r[3]))
    R5 = ((T2 ** r[2]) * (v ** -r[4]))
    c = group.hash((M, T1, T2, T3, R1, R2, R3, R4, R5), ZR)
    salpha = (r[0] + (c * alpha))
    sbeta = (r[1] + (c * beta))
    sx = (r[2] + (c * x_ind))
    sgamma1 = (r[3] + (c * gamma1))
    sgamma2 = (r[4] + (c * gamma2))
    sig = [T1, T2, T3, c, salpha, sbeta, sx, sgamma1, sgamma2, R3]
    output = sig
    return output

def verify(g1, g2, h, u, v, w, M, T1, T2, T3, c, salpha, sbeta, sx, sgamma1, sgamma2, R3):

    input = [g1, g2, h, u, v, w, M, T1, T2, T3, c, salpha, sbeta, sx, sgamma1, sgamma2, R3]
    if ( ( (precheck(g1, g2, h, u, v, w, M, T1, T2, T3, c, salpha, sbeta, sx, sgamma1, sgamma2, R3)) == (False) ) ):
        output = False
    if ( ( (((pair(T3, g2) ** sx) * ((pair(h, w) ** (-salpha - sbeta)) * ((pair(h, g2) ** (-sgamma1 - sgamma2)) * ((pair(T3, w) ** c) * (pair(g1, g2) ** -c)))))) == (R3) ) ):
        output = True
    else:
        output = False
    return output

def membership(R3list, T1list, T2list, T3list, clist, g1, g2, h, salphalist, sbetalist, sgamma1list, sgamma2list, sxlist, u, v, w):

    input = [R3list, T1list, T2list, T3list, clist, g1, g2, h, salphalist, sbetalist, sgamma1list, sgamma2list, sxlist, u, v, w]
    if ( ( (group.ismember(R3list)) == (False) ) ):
        output = False
    if ( ( (group.ismember(T1list)) == (False) ) ):
        output = False
    if ( ( (group.ismember(T2list)) == (False) ) ):
        output = False
    if ( ( (group.ismember(T3list)) == (False) ) ):
        output = False
    if ( ( (group.ismember(clist)) == (False) ) ):
        output = False
    if ( ( (group.ismember(g1)) == (False) ) ):
        output = False
    if ( ( (group.ismember(g2)) == (False) ) ):
        output = False
    if ( ( (group.ismember(h)) == (False) ) ):
        output = False
    if ( ( (group.ismember(salphalist)) == (False) ) ):
        output = False
    if ( ( (group.ismember(sbetalist)) == (False) ) ):
        output = False
    if ( ( (group.ismember(sgamma1list)) == (False) ) ):
        output = False
    if ( ( (group.ismember(sgamma2list)) == (False) ) ):
        output = False
    if ( ( (group.ismember(sxlist)) == (False) ) ):
        output = False
    if ( ( (group.ismember(u)) == (False) ) ):
        output = False
    if ( ( (group.ismember(v)) == (False) ) ):
        output = False
    if ( ( (group.ismember(w)) == (False) ) ):
        output = False
    output = True
    return output

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, w):

    input = [delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, w]
    dotALoopVal = 1
    dotBLoopVal = 1
    dotCLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotALoopVal = (dotALoopVal * dotACache[z])
        dotBLoopVal = (dotBLoopVal * dotBCache[z])
        dotCLoopVal = (dotCLoopVal * dotCCache[z])
    if ( ( ((pair(dotALoopVal, g2) * pair(dotBLoopVal, w))) == (dotCLoopVal) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, startSigNum, midway, incorrectIndices, dotACache, dotBCache, dotCCache, g2, w)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, g2, w)
    output = None

def batchverify(Mlist, R3list, T1list, T2list, T3list, clist, g1, g2, h, salphalist, sbetalist, sgamma1list, sgamma2list, sxlist, u, v, w, incorrectIndices):

    dotCCache = {}
    delta = {}
    dotBCache = {}
    dotACache = {}

    input = [Mlist, R3list, T1list, T2list, T3list, clist, g1, g2, h, salphalist, sbetalist, sgamma1list, sgamma2list, sxlist, u, v, w, incorrectIndices]
    for z in range(0, N):
        delta[z] = SmallExp(secparam)
    if ( ( (membership(R3list, T1list, T2list, T3list, clist, g1, g2, h, salphalist, sbetalist, sgamma1list, sgamma2list, sxlist, u, v, w)) == (False) ) ):
        output = False
    for z in range(0, N):
        if ( ( (precheck(g1, g2, h, u, v, w, Mlist[z], T1list[z], T2list[z], T3list[z], clist[z], salphalist[z], sbetalist[z], sxlist[z], sgamma1list[z], sgamma2list[z], R3list[z])) == (False) ) ):
            return False

    for z in range(0, N):
        dotACache[z] = ((T3list[z] ** (sxlist[z] * delta[z])) * ((h ** ((-sgamma1list[z] + -sgamma2list[z]) * delta[z])) * (g1 ** (-clist[z] * delta[z]))))
        dotBCache[z] = ((h ** ((-salphalist[z] + -sbetalist[z]) * delta[z])) * (T3list[z] ** (clist[z] * delta[z])))
        dotCCache[z] = (R3list[z] ** delta[z])
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, g2, w)
    output = incorrectIndices
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    (gpk, gmsk, A, x) = keygen(3)
    T1, T2, T3, c, salpha, sbeta, sx, sgamma1, sgamma2, R3 = sign(gpk, A[0], x[0], "message")
    sig0 = sign(gpk, A[0], x[0], "message0")
    sig1 = sign(gpk, A[0], x[0], "message1")
    g1 = gpk[0]
    g2 = gpk[1]
    h = gpk[2]
    u = gpk[3]
    v = gpk[4]
    w = gpk[5]
    verify(g1, g2, h, u, v, w, "message", T1, T2, T3, c, salpha, sbeta, sx, sgamma1, sgamma2, R3), "failed verification!"
    print("Successful Verification!")

    Mlist = ["message0", "message1"]
    T1list = [sig0[0], sig1[0]]
    T2list = [sig0[1], sig1[1]]
    T3list = [sig0[2], sig1[2]]
    clist = [sig0[3], sig1[3]]
    salphalist = [sig0[4], sig1[4]]
    sbetalist = [sig0[5], sig1[5]]
    sxlist = [sig0[6], sig1[6]]
    sgamma1list = [sig0[7], sig1[7]]
    sgamma2list = [sig0[8], sig1[8]]
    R3list = [sig0[9], sig1[9]]
    incorrectIndices = []
    if batchverify(Mlist, R3list, T1list, T2list, T3list, clist, g1, g2, h, salphalist, sbetalist, sgamma1list, sgamma2list, sxlist, u, v, w, incorrectIndices) == False:
       print("Failed batch verification!")
    else:
       print("incorrectIndices: ", incorrectIndices)

if __name__ == '__main__':
    main()

