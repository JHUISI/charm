from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 100

secparam = 80

result = {}
A0 = {}
Bt = {}
C0 = {}
D = {}
c = {}
a = {}
b = {}
m = {}
B0 = {}
At = {}
Ct = {}

def setup():
    global A0
    global C0
    global B0

    input = None
    g1 = group.random(G1)
    g2 = group.random(G2)
    a0 = group.random(ZR)
    b0 = group.random(ZR)
    c0 = group.random(ZR)
    A0 = (g1 ** a0)
    B0 = (g1 ** b0)
    C0 = (g1 ** c0)
    mpk = [A0, B0, C0]
    output = (mpk, g1, g2)
    return output

def keygen(g1, g2):
    global Bt
    global c
    global a
    global b
    global At
    global Ct

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

def sign(g1, mpk, Alist, Blist, Clist, sk, M, l):
    global result
    global m

    S = {}
    s = {}
    t = {}

    input = [g1, mpk, Alist, Blist, Clist, sk, M, l]
    A0, B0, C0 = mpk
    prod0 = 1
    prod1 = 1
    m = group.hash(M, ZR)
    for y in range(0, l-1):
        s[y] = group.random(ZR)
        S[y] = (g1 ** s[y])
    for y in range(0, l):
        t[y] = group.random(ZR)
    prod0 = (((A0 * (B0 ** m)) * (C0 ** t[0])) ** -s[0])
    for y in range(0, l-1):
        prod1 = (prod1 * ((Alist[y] * ((Blist[y] ** m) * (Clist[y] ** t[y]))) ** -s[y]))
    result = (prod0 * prod1)
    d = ((a + (b * m)) + (c * t[l-1]))
    S[l-1] = ((g1 * result) ** (1 / d))
    output = (S, t)
    return output

def verify(g1, g2, Atlist, Btlist, Ctlist, M, S, t, l):
    global result
    global D
    global m

    input = [g1, g2, Atlist, Btlist, Ctlist, M, S, t, l]
    D = pair(g1, g2)
    m = group.hash(M, ZR)
    result = 1
    for y in range(0, l):
        result = (result * pair(S[y], (Atlist[y] * ((Btlist[y] ** m) * (Ctlist[y] ** t[y])))))
    if ( ( (result) == (D) ) ):
        output = True
    else:
        output = False
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    (mpk, g1, g2) = setup()
    (pk0, sk0) = keygen(g1, g2)
    (pk1, sk1) = keygen(g1, g2)
    Alist = [pk0[0], pk1[0]]
    Blist = [pk0[1], pk1[1]]
    Clist = [pk0[2], pk1[2]]
    (S0, t0) = sign(g1, mpk, Alist, Blist, Clist, sk0, "m0", 2)
    (S1, t1) = sign(g1, mpk, Alist, Blist, Clist, sk1, "m1", 2)
    Atlist = [pk0[3], pk1[3]]
    Btlist = [pk0[4], pk1[4]]
    Ctlist = [pk0[5], pk1[5]]    
    print(verify(g1, g2, Atlist, Btlist, Ctlist, "m0", S0, t0, 2))
    print(verify(g1, g2, Atlist, Btlist, Ctlist, "m1", S1, t1, 2))


if __name__ == '__main__':
    main()

