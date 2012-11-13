from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80
"""
vG2 = {}
t = {}
theta = {}
v1G2 = {}
tagc = {}
s = {}
g2b = {}
v2G2 = {}
g2AlphaA1 = {}
s2 = {}
s1 = {}
M = {}
alpha = {}
"""
def keygen():
    """
    global vG2
    global v1G2
    global g2b
    global v2G2
    global g2AlphaA1
    global alpha
    """
    input = None
    g1 = group.random(G1)
    g2 = group.random(G2)
    a1 = group.random(ZR)
    a2 = group.random(ZR)
    b = group.random(ZR)
    alpha = group.random(ZR)
    wExp = group.random(ZR)
    hExp = group.random(ZR)
    vExp = group.random(ZR)
    v1Exp = group.random(ZR)
    v2Exp = group.random(ZR)
    uExp = group.random(ZR)
    vG2 = (g2 ** vExp)
    v1G2 = (g2 ** v1Exp)
    v2G2 = (g2 ** v2Exp)
    wG1 = (g1 ** wExp)
    hG1 = (g1 ** hExp)
    w = (g2 ** wExp)
    h = (g2 ** hExp)
    uG1 = (g1 ** uExp)
    u = (g2 ** uExp)
    tau1 = (vG2 * (v1G2 ** a1))
    tau2 = (vG2 * (v2G2 ** a2))
    g1b = (g1 ** b)
    g1a1 = (g1 ** a1)
    g1a2 = (g1 ** a2)
    g1ba1 = (g1 ** (b * a1))
    g1ba2 = (g1 ** (b * a2))
    tau1b = (tau1 ** b)
    tau2b = (tau2 ** b)
    A = (pair(g1, g2) ** (alpha * (a1 * b)))
    g2AlphaA1 = (g2 ** (alpha * a1))
    g2b = (g2 ** b)
    pk = [g1, g2, g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, uG1, u, wG1, hG1, w, h, A]
    sk = [g2AlphaA1, g2b, vG2, v1G2, v2G2, alpha]
    output = (pk, sk)
    return output

def sign(pk, sk, m):
    """
    global M
    """
    input = [pk, sk, m]
    g1, g2, g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, uG1, u, wG1, hG1, w, h, A = pk
    g2AlphaA1, g2b, vG2, v1G2, v2G2, alpha = sk
    r1 = group.random(ZR)
    r2 = group.random(ZR)
    z1 = group.random(ZR)
    z2 = group.random(ZR)
    tagk = group.random(ZR)
    r = (r1 + r2)
    M = group.hash(m, ZR)
    S1 = (g2AlphaA1 * (vG2 ** r))
    S2 = ((g2 ** -alpha) * ((v1G2 ** r) * (g2 ** z1)))
    S3 = (g2b ** -z1)
    S4 = ((v2G2 ** r) * (g2 ** z2))
    S5 = (g2b ** -z2)
    S6 = (g1b ** r2)
    S7 = (g1 ** r1)
    SK = (((u ** M) * (w ** tagk)) * h) ** r1
    output = (S1, S2, S3, S4, S5, S6, S7, SK, tagk)
    return output

def verify(g1, g2, g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, u, w, h, A, S1, S2, S3, S4, S5, S6, S7, SK, tagk, m):
    """
    global t
    global theta
    global tagc
    global s
    global s2
    global s1
    global M
    """
    input = [g1, g2, g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, u, w, h, A, S1, S2, S3, S4, S5, S6, S7, SK, tagk, m]
    s1 = group.random(ZR)
    s2 = group.random(ZR)
    t = group.random(ZR)
    tagc = group.random(ZR)
    s = (s1 + s2)
    M = group.hash(m, ZR)
    theta = (1 / (tagc - tagk))

    if ((pair((g1b ** s), S1) * (pair((g1ba1 ** s1), S2) * (pair((g1a1 ** s1), S3) * (pair((g1ba2 ** s2), S4) * pair((g1a2 ** s2), S5)))))) == ((pair(S6, ((tau1 ** s1) * (tau2 ** s2))) * (pair(S7, ((tau1b ** s1) * ((tau2b ** s2) * (w ** -t)))) * (((pair(S7, (((u ** (M * t)) * (w ** (tagc * t))) * (h ** t))) * pair((g1 ** -t), SK)) ** theta) * (A ** s2))))):
        output = True
    else:
        output = False
        return output
    return output

def membership(A, S1list, S2list, S3list, S4list, S5list, S6list, S7list, SKlist, g1, g1a1, g1a2, g1b, g1ba1, g1ba2, g2, h, tagklist, tau1, tau1b, tau2, tau2b, u, w):

    input = [A, S1list, S2list, S3list, S4list, S5list, S6list, S7list, SKlist, g1, g1a1, g1a2, g1b, g1ba1, g1ba2, g2, h, tagklist, tau1, tau1b, tau2, tau2b, u, w]
    if ( ( (group.ismember(A)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(S1list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(S2list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(S3list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(S4list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(S5list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(S6list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(S7list)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(SKlist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g1)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g1a1)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g1a2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g1b)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g1ba1)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g1ba2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(h)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(tagklist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(tau1)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(tau1b)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(tau2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(tau2b)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(u)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(w)) == (False) ) ):
        output = False
        return output
    output = True
    return output

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, dotMCache, sumNCache, g1b, g1ba1, g1a1, g1ba2, g1a2, tau1, tau2, tau1b, tau2b, w, u, h, g1, A):

    input = [delta, startSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, dotMCache, sumNCache, g1b, g1ba1, g1a1, g1ba2, g1a2, tau1, tau2, tau1b, tau2b, w, u, h, g1, A]
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
    dotMLoopVal = 1
    sumNLoopVal = 0
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
        dotMLoopVal = (dotMLoopVal * dotMCache[z])
        sumNLoopVal = (sumNLoopVal + sumNCache[z])
    if ( ( ((pair(g1b, dotALoopVal) * (pair(g1ba1, dotBLoopVal) * (pair(g1a1, dotCLoopVal) * (pair(g1ba2, dotDLoopVal) * pair(g1a2, dotELoopVal)))))) == ((pair(dotFLoopVal, tau1) * (pair(dotGLoopVal, tau2) * (pair(dotHLoopVal, tau1b) * (pair(dotILoopVal, tau2b) * (pair(dotJLoopVal, w) * (pair(dotKLoopVal, u) * (pair(dotLLoopVal, h) * (pair(g1, dotMLoopVal) * (A ** sumNLoopVal)))))))))) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, startSigNum, midSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, dotMCache, sumNCache, g1b, g1ba1, g1a1, g1ba2, g1a2, tau1, tau2, tau1b, tau2b, w, u, h, g1, A)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, dotMCache, sumNCache, g1b, g1ba1, g1a1, g1ba2, g1a2, tau1, tau2, tau1b, tau2b, w, u, h, g1, A)
    output = None

def batchverify(A, S1list, S2list, S3list, S4list, S5list, S6list, S7list, SKlist, g1, g1a1, g1a2, g1b, g1ba1, g1ba2, g2, h, mlist, tagklist, tau1, tau1b, tau2, tau2b, u, w, incorrectIndices):
    """
    global t
    global theta
    global tagc
    global s
    global s2
    global s1
    global M
    """
    dotLCache = {}
    dotKCache = {}
    dotDCache = {}
    delta = {}
    dotJCache = {}
    dotECache = {}
    dotICache = {}
    dotBCache = {}
    sumNCache = {}
    dotHCache = {}
    dotGCache = {}
    dotACache = {}
    dotFCache = {}
    dotCCache = {}
    dotMCache = {}

    input = [A, S1list, S2list, S3list, S4list, S5list, S6list, S7list, SKlist, g1, g1a1, g1a2, g1b, g1ba1, g1ba2, g2, h, mlist, tagklist, tau1, tau1b, tau2, tau2b, u, w, incorrectIndices]
    for z in range(0, N):
        delta[z] = SmallExp(secparam)
    if ( ( (membership(A, S1list, S2list, S3list, S4list, S5list, S6list, S7list, SKlist, g1, g1a1, g1a2, g1b, g1ba1, g1ba2, g2, h, tagklist, tau1, tau1b, tau2, tau2b, u, w)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        s2 = group.random(ZR)
        s1 = group.random(ZR)
        M = group.hash(mlist[z], ZR)
        s = (s1 + s2)
        t = group.random(ZR)
        tagc = group.random(ZR)
        theta = (1 / (tagc - tagklist[z]))

        dotACache[z] = (S1list[z] ** (s * delta[z]))
        dotBCache[z] = (S2list[z] ** (s1 * delta[z]))
        dotCCache[z] = (S3list[z] ** (s1 * delta[z]))
        dotDCache[z] = (S4list[z] ** (s2 * delta[z]))
        dotECache[z] = (S5list[z] ** (s2 * delta[z]))
        dotFCache[z] = (S6list[z] ** (delta[z] * s1))
        dotGCache[z] = (S6list[z] ** (delta[z] * s2))
        dotHCache[z] = (S7list[z] ** (delta[z] * s1))
        dotICache[z] = (S7list[z] ** (delta[z] * s2))
        dotJCache[z] = (S7list[z] ** ((delta[z] * -t) + ((theta * delta[z]) * (tagc * t))))
        dotKCache[z] = (S7list[z] ** ((theta * delta[z]) * (M * t)))
        dotLCache[z] = (S7list[z] ** ((theta * delta[z]) * t))
        dotMCache[z] = (SKlist[z] ** (-t * (theta * delta[z])))
        sumNCache[z] = (s2 * delta[z])
    dividenconquer(delta, 0, N, incorrectIndices, dotACache, dotBCache, dotCCache, dotDCache, dotECache, dotFCache, dotGCache, dotHCache, dotICache, dotJCache, dotKCache, dotLCache, dotMCache, sumNCache, g1b, g1ba1, g1a1, g1ba2, g1a2, tau1, tau2, tau1b, tau2b, w, u, h, g1, A)
    output = incorrectIndices
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    m0 = "message0"
    m1 = "message1"
    (pk, sk) = keygen()
    S1list = [0, 1]
    S2list = [0, 1]
    S3list = [0, 1]
    S4list = [0, 1]
    S5list = [0, 1]
    S6list = [0, 1]
    S7list = [0, 1]
    SKlist = [0, 1]
    tagklist = [0, 1]
    mlist = [m0, m1]
    (S1list[0], S2list[0], S3list[0], S4list[0], S5list[0], S6list[0], S7list[0], SKlist[0], tagklist[0]) = sign(pk, sk, m0)
    (S1list[1], S2list[1], S3list[1], S4list[1], S5list[1], S6list[1], S7list[1], SKlist[1], tagklist[1]) = sign(pk, sk, m1)

    g1, g2, g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, uG1, u, wG1, hG1, w, h, A = pk
    print(verify(g1, g2, g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, u, w, h, A, S1list[0], S2list[0], S3list[0], S4list[0], S5list[0], S6list[0], S7list[0], SKlist[0], tagklist[0], m0))
    print(verify(g1, g2, g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, u, w, h, A, S1list[1], S2list[1], S3list[1], S4list[1], S5list[1], S6list[1], S7list[1], SKlist[1], tagklist[1], m1))
    
    incorrectIndices = []
    batchverify(A, S1list, S2list, S3list, S4list, S5list, S6list, S7list, SKlist, g1, g1a1, g1a2, g1b, g1ba1, g1ba2, g2, h, mlist, tagklist, tau1, tau1b, tau2, tau2b, u, w, incorrectIndices)
    print("incorrectIndices: ", incorrectIndices)

if __name__ == '__main__':
    main()

