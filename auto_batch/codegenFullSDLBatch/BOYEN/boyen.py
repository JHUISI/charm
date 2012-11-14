from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

l = 3

secparam = 80

D = {}
c = {}
a = {}
b = {}
m = {}

def setup():
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

def sign(g1, Alist, Blist, Clist, sk, M, index):
    S = {}
    s = {}
    t = {}

    a, b, c = sk
    dotProd0 = 1
    dotProd1 = 1
    m = group.hash(M, ZR)
    for y in range(0, l):
        if ( ( (y) != (index) ) ):
            s[y] = group.random(ZR)
            S[y] = (g1 ** s[y])
    for y in range(0, l):
        t[y] = group.random(ZR)
    dotProd0 = (((Alist[0] * (Blist[0] ** m)) * (Clist[0] ** t[0])) ** -s[0])
    for y in range(1, l):
        if ( ( (y) != (index) ) ):
            dotProd1 = (dotProd1 * ((Alist[y] * ((Blist[y] ** m) * (Clist[y] ** t[y]))) ** -s[y]))
    result0 = (dotProd0 * dotProd1)
    d = ((a + (b * m)) + (c * t[index]))
    S[index] = ((g1 * result0) ** (1 / d))
    output = (S, t)
    return output

def verify(g1, g2, Atlist, Btlist, Ctlist, M, S, t):
    D = pair(g1, g2)
    dotProd2 = 1
    m = group.hash(M, ZR)
    for y in range(0, l):
        dotProd2 = (dotProd2 * pair(S[y], (Atlist[y] * ((Btlist[y] ** m) * (Ctlist[y] ** t[y])))))
    if ( ( (dotProd2) == (D) ) ):
        output = True
    else:
        output = False
        return output
    return output

def membership(Atlist, Btlist, Ctlist, Slist, g1, g2, tlist):
    if ( ( (group.ismember(Atlist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(Btlist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(Ctlist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(Slist)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g1)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(g2)) == (False) ) ):
        output = False
        return output
    if ( ( (group.ismember(tlist)) == (False) ) ):
        output = False
        return output
    output = True
    return output

def dividenconquer(delta, startSigNum, endSigNum, incorrectIndices, dotDCache, Atlist, Btlist, Ctlist, Mlist, Slist, g1, g2, tlist):
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
        dividenconquer(delta, startSigNum, midSigNum, incorrectIndices, dotDCache, Atlist, Btlist, Ctlist, Mlist, Slist, g1, g2, tlist)
        dividenconquer(delta, midSigNum, endSigNum, incorrectIndices, dotDCache, Atlist, Btlist, Ctlist, Mlist, Slist, g1, g2, tlist)
    output = None

def batchverify(Atlist, Btlist, Ctlist, Mlist, Slist, g1, g2, tlist, incorrectIndices):
    dotDCache = {}
    delta = {}

    for z in range(0, N):
        delta[z] = SmallExp(secparam)
    if ( ( (membership(Atlist, Btlist, Ctlist, Slist, g1, g2, tlist)) == (False) ) ):
        output = False
        return output
    D = pair(g1, g2)
    for z in range(0, N):
        dotDCache[z] = (D ** delta[z])
    dividenconquer(delta, 0, N, incorrectIndices, dotDCache, Atlist, Btlist, Ctlist, Mlist, Slist, g1, g2, tlist)
    output = incorrectIndices
    return output

def indivverify(Atlist, Btlist, Ctlist, Mlist, Slist, g1, g2, tlist, incorrectIndices):
    if ( ( (membership(Atlist, Btlist, Ctlist, Slist, g1, g2, tlist)) == (False) ) ):
        output = False
        return output
    for z in range(0, N):
        if verify(g1, g2, Atlist, Btlist, Ctlist, Mlist[z], Slist[z], tlist[z]) == False:
            incorrectIndices.append(z)
    return incorrectIndices
    
def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('BN256')

    (mpk, g1, g2) = setup()
    #mpk = [A0, B0, C0, At0, Bt0, Ct0]

    # pk = [A, B, C, At, Bt, Ct]
    (pk0, sk0) = keygen(g1, g2)
    print("pk0 :=>", pk0)
    print("sk0 :=>", sk0)
    (pk1, sk1) = keygen(g1, g2)

    M0 = "test message 0"
    M1 = "test message 1"
    Mlist = [M0, M1]
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

    my_index = 1
    (S0, t0) = sign(g1, Alist, Blist, Clist, sk0, Mlist[0], my_index)
    my_index = 2
    (S1, t1) = sign(g1, Alist, Blist, Clist, sk1, Mlist[1], my_index)

    Slist = [S0, S1]
    tlist = [t0, t1]

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

    assert verify(g1, g2, Atlist, Btlist, Ctlist, Mlist[0], Slist[0], tlist[0]), "failed verification!!"
    assert verify(g1, g2, Atlist, Btlist, Ctlist, Mlist[1], Slist[1], tlist[1]), "failed verification!!"
    print("Successful Verification")

    incorrectIndices = []
    #Mlist[0] = Mlist[1] = "foo"
    batchverify(Atlist, Btlist, Ctlist, Mlist, Slist, g1, g2, tlist, incorrectIndices)
    print(incorrectIndices)


if __name__ == '__main__':
    main()

