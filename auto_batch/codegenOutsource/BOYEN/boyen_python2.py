from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2
l = 3

secparam = 80

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

def sign(g1, Alist, Blist, Clist, sk, M, index):

    S = {}
    s = {}
    t = {}

    input = [g1, Alist, Blist, Clist, sk, M]
    a, b, c = sk
    prod0 = 1
    prod1 = 1
    m = group.hash(M, ZR)
    for y in range(0, l):
        if y != index:
           s[y] = group.random(ZR)
           S[y] = (g1 ** s[y])
           print("S[%s] :=> %s" % (y, S[y]))
    for y in range(0, l):
        t[y] = group.random(ZR)
        print("t[%s] = %s" % (y, t[y])) 
    prod0 = (((Alist[0] * (Blist[0] ** m)) * (Clist[0] ** t[0])) ** -s[0])
    for y in range(1, l):
        if y != index:
           print("sign loop: ", y)
           prod0 *= (((Alist[y] * ((Blist[y] ** m) * (Clist[y] ** t[y]))) ** -s[y]))
    #result = (prod0 * prod1)
    d = ((a + (b * m)) + (c * t[index]))
    S[index] = ((g1 * prod0) ** (1 / d))
    print("S[%s] :=> %s" % (index, S[index]))
    output = (S, t)
    return output

def verify(g1, g2, Atlist, Btlist, Ctlist, M, S, t, l):
    global D

    input = [g1, g2, Atlist, Btlist, Ctlist, M, S, t, l]
    D = pair(g1, g2)
    result = 1
    m = group.hash(M, ZR)
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
    group = PairingGroup("MNT224")

    (mpk, g1, g2) = setup()
    #mpk = [A0, B0, C0, At0, Bt0, Ct0]

    # l = 2 so need two keys
    # pk = [A, B, C, At, Bt, Ct]
    (pk0, sk0) = keygen(g1, g2)
    print("pk0 :=>", pk0)
    print("sk0 :=>", sk0)
    (pk1, sk1) = keygen(g1, g2)

    M = "this is my message."
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
    (S0, t0) = sign(g1, Alist, Blist, Clist, sk0, M, my_index)
    my_index = l-1
    (S1, t1) = sign(g1, Alist, Blist, Clist, sk1, M, my_index)

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

    assert verify(g1, g2, Atlist, Btlist, Ctlist, M, S0, t0, l), "failed verification!!"
    assert verify(g1, g2, Atlist, Btlist, Ctlist, M, S1, t1, l), "failed verification!!"
    print("Successful Verification")

    
if __name__ == '__main__':
    main()

