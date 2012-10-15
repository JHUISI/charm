from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

l = 3

secparam = 80

#D = {}
#m = {}

def setup():
#    global A0
#    global C0
#    global B0

    input = None
    g1 = group.random(G1)
    g2 = group.random(G2)
    a0 = group.random(ZR)
    b0 = group.random(ZR)
    c0 = group.random(ZR)
    A0 = (g1 ** a0)
    B0 = (g1 ** b0)
    C0 = (g1 ** c0)
    At0 = (g2 ** a0)
    Bt0 = (g2 ** b0)
    Ct0 = (g2 ** c0)
    mpk = [A0, B0, C0, At0, Bt0, Ct0]
    output = (mpk, g1, g2)
    return output

def keygen(g1, g2):
#    global Bt
#    global c
#    global a
#    global b
#    global At
#    global Ct

    input = [g1, g2]
    a = group.random(ZR)
    b = group.random(ZR)
    c = group.random(ZR)
    A = (g1 ** a)
    At = (g2 ** a)
    B = (g1 ** b)
    Bt = (g2 ** b)
    C = (g1 ** c)
    Ct = (g2 ** c)
    sk = [a, b, c]
    pk = [A, B, C, At, Bt, Ct]
    output = (pk, sk)
    return output

def sign(g1, Alist, Blist, Clist, sk, M, l):

    S = {}
    s = {}
    t = {}

    input = [g1, Alist, Blist, Clist, sk, M, l]
    a, b, c = sk
    prod0 = 1
    prod1 = 1
    m = group.hash(M, ZR)
    for y in range(0, l-1):
        s[y] = group.random(ZR)
        S[y] = (g1 ** s[y])
        print("S[%s] :=> %s" % (y, S[y]))
    for y in range(0, l):
        t[y] = group.random(ZR)
        print("t[%s] = %s" % (y, t[y])) 
    prod0 = (((Alist[0] * (Blist[0] ** m)) * (Clist[0] ** t[0])) ** -s[0])
    for y in range(1, l-1):
        print("sign loop: ", y)
        prod0 *= (((Alist[y] * ((Blist[y] ** m) * (Clist[y] ** t[y]))) ** -s[y]))
    #result = (prod0 * prod1)
    d = ((a + (b * m)) + (c * t[l-1]))
    S[l-1] = ((g1 * prod0) ** (1 / d))
    print("S[%s] :=> %s" % (l-1, S[l-1]))
    output = (S, t)
    return output

def verify(At, Bt, Ct, M, S, t, g1, g2):
    #global D
    #global m

    input = [At, Bt, Ct, M, S, t, g1, g2]
    D = pair(g1, g2)
    m = group.hash(M, ZR)
    result = 1
    for y in range(0, l):
        result = (result * pair(S[y], (At[y] * ((Bt[y] ** m) * (Ct[y] ** t[y])))))
    if ( ( (result) == (D) ) ):
        output = True
    else:
        output = False
    return output

def membership(Slist, tlist, g2, g1, Atlist, Btlist, Ctlist):

    input = [Slist, tlist, g2, g1, Atlist, Btlist, Ctlist]
    if ( ( (group.ismember(Slist)) == (False) ) ):
        output = False
    if ( ( (group.ismember(g2)) == (False) ) ):
        output = False
    if ( ( (group.ismember(g1)) == (False) ) ):
        output = False
    if ( ( (group.ismember(Atlist)) == (False) ) ):
        output = False
    if ( ( (group.ismember(Btlist)) == (False) ) ):
        output = False
    if ( ( (group.ismember(Ctlist)) == (False) ) ):
        output = False
    output = True
    return output

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotDCache, Mlist, Atlist, Btlist, Ctlist, tlist, Slist):
    #global m

    input = [delta, startSigNum, endSigNum, incorrectIndices, dotDCache, Mlist, Atlist, Btlist, Ctlist, tlist, Slist]
    dotDLoopVal = 1
    for z in range(startSigNum, endSigNum):
        dotDLoopVal = (dotDLoopVal * dotDCache[z])
    dotELoopVal = 1
    for y in range(0, l):
        dotALoopVal = 1
        dotBLoopVal = 1
        dotCLoopVal = 1
        for z in range(startSigNum, endSigNum):
            m = group.hash(Mlist[z], ZR)
            dotALoopVal = (dotALoopVal * (Slist[z][y] ** delta[z]))
            dotBLoopVal = (dotBLoopVal * (Slist[z][y] ** (m * delta[z])))
            dotCLoopVal = (dotCLoopVal * (Slist[z][y] ** (tlist[z][y] * delta[z])))
        dotELoopVal = (dotELoopVal * (pair(dotALoopVal, Atlist[y]) * (pair(dotBLoopVal, Btlist[y]) * pair(dotCLoopVal, Ctlist[y]))))
    if ( ( (dotELoopVal) == (dotDLoopVal) ) ):
        return
    else:
        midwayFloat = ((endSigNum - startSigNum) / 2)
        midway = int(midwayFloat)
    if ( ( (midway) == (0) ) ):
        incorrectIndices.append(startSigNum)
        output = None
    else:
        midSigNum = (startSigNum + midway)
        dividenconquer(delta, startSigNum, midSigNum, incorrectIndices, dotDCache, Mlist, Atlist, Btlist, Ctlist, tlist, Slist)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotDCache, Mlist, Atlist, Btlist, Ctlist, tlist, Slist)
    output = None

def batchverify(Mlist, Slist, tlist, g2, g1, Btlist, Atlist, Ctlist, incorrectIndices):
    #global D

    dotDCache = {}
    delta = {}

    input = [Mlist, Slist, tlist, g2, g1, Btlist, Atlist, Ctlist, incorrectIndices]
    for z in range(0, N):
        delta[z] = SmallExp(secparam)
    if ( ( (membership(Slist, t1list, g2, g1, Bt, At, Ct)) == (False) ) ):
        output = False
    D = pair(g1, g2)
    for z in range(0, N):
        dotDCache[z] = (D ** delta[z])
    dividenconquer(delta, 0, N, incorrectIndices, dotDCache, dotDCache, Mlist, Atlist, Btlist, Ctlist, tlist, Slist)
    output = incorrectIndices
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    (mpk, g1, g2) = setup()
    #mpk = [A0, B0, C0, At0, Bt0, Ct0]

    # l = 2 so need two keys
    # pk = [A, B, C, At, Bt, Ct]
    (pk0, sk0) = keygen(g1, g2)
    print("pk0 :=>", pk0)
    print("sk0 :=>", sk0)
    (pk1, sk1) = keygen(g1, g2)

    M = "this is my message."
    M2 = "test"
    Mlist = [M, M2]
    Alist = {} 
    Blist = {}
    Clist = {}
    Alist[0] = mpk[0]
    Alist[1] = pk0[0]
    Alist[2] = pk1[0]

    Blist[0] = mpk[1]
    Blist[1] = pk0[1]
    Blist[2] = pk1[1]
    
    Clist[0] = mpk[2]
    Clist[1] = pk0[2]
    Clist[2] = pk1[2]

    Alist2 = {}
    Blist2 = {}
    Clist2 = {}

    Alist2[0] = mpk[0]
    Alist2[1] = pk1[0]
    Alist2[2] = pk0[0]

    Blist2[0] = mpk[1]
    Blist2[1] = pk1[1]
    Blist2[2] = pk0[1]

    Clist2[0] = mpk[2]
    Clist2[1] = pk1[2]
    Clist2[2] = pk0[2]

    (S0, t0) = sign(g1, Alist, Blist, Clist, sk1, M, l)
    (S1, t1) = sign(g1, Alist2, Blist2, Clist2, sk0, M2, l)

    Atlist = {}
    Btlist = {}
    Ctlist = {}

    Atlist[0] = mpk[3]    
    Atlist[1] = pk0[3]
    Atlist[2] = pk1[3]

    Btlist[0] = mpk[4]    
    Btlist[1] = pk0[4]
    Btlist[2] = pk1[4]

    Ctlist[0] = mpk[5]    
    Ctlist[1] = pk0[5]
    Ctlist[2] = pk1[5]

    assert verify(Atlist, Btlist, Ctlist, M, S0, t0, g1, g2), "failed verification!!"
    assert verify(Atlist, Btlist, Ctlist, M2, S1, t1, g1, g2), "failed verification!!"
    print("Successful Verification")

    #batchverify(Mlist, Slist, tlist, g2, g1, Btlist, Atlist, Ctlist, incorrectIndices)

if __name__ == '__main__':
    main()

