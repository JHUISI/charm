from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
#from charm.core.math.integer import randomBits

group = None

N = 100

l = 3

secparam = 80

Lt = {}
dotProd = {}
h = {}
l = {}

def setup():

    input = None
    g = group.random(G2)
    alpha = group.random(ZR)
    P = (g ** alpha)
    output = (P, g, alpha)
    return output

def concat(ID_List):
    global l

    input = ID_List
    L = 1
    l = len(L)
    for y in range(0, l):
        L = (L, ID_List[y])
    output = L
    return output

def keygen(alpha, ID):

    input = [alpha, ID]
    sk = (group.hash(ID, G1) ** alpha)
    pk = group.hash(ID, G1)
    output = (pk, sk)
    return output

def sign(ID, pk, sk, L, M):
    global Lt
    global dotProd
    global h

    h = {}
    u = {}
    pklist = {}

    input = [ID, pk, sk, L, M]
    Lt = concat(L)
    for i in range(0, l):
        if ( ( (ID) != (L[i]) ) ):
            u[i] = group.random(G1)
            h[i] = group.hash((M, (Lt, u[i])), ZR)
        else:
            s = i
    r = group.random(ZR)
    for y in range(0, l):
        pklist[y] = group.hash(L[y], G1)
    dotProd = 1
    for i in range(0, l):
        if ( ( (ID) != (L[i]) ) ):
            dotProd = (dotProd * (u[i] * (pk[i] ** h[i])))
    u[s] = ((pk ** r) * dotProd)
    h[s] = group.hash((M, (Lt, u[s])), ZR)
    S = (sk ** (h[s] + r))
    output = (u, S)
    return output

def verify(P, g, L, M, u, S):
    global Lt
    global dotProd
    global h

    input = [P, g, L, M, u, S]
    Lt = concat(L)
    num_sign = len(L)
    h = 1
    for y in range(0, l):
        h[y] = group.hash((M, (Lt, u[y])), ZR)
        pk[y] = group.hash(L[y], G1)
    dotProd = 1
    for y in range(0, l):
        dotProd = (dotProd * (u[y] * (pk[y] ** h[y])))
    if ( ( (pair(dotProd, P)) == (pair(S, g)) ) ):
        output = True
    else:
        output = False
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    (P, g, alpha) = setup()
    (pk, sk) = keygen(alpha, "alice")
    L = ["alice", "bob", "charlie"]
    (u, S) = sign("alice", pk, sk, L, "message")
    print(verify(P, g, L, "message", u, S))


if __name__ == '__main__':
    main()

