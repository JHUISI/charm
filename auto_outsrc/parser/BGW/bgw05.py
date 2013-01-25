from bgw05USER import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80


def setup(nParam):
    giValues = {}

    n = nParam
    g = group.random(G1)
    alpha = group.random(ZR)
    endIndexOfList = ((2 * n) + 1)
    for i in range(1, endIndexOfList):
        giValues[i] = (g ** (alpha ** i))
    gamma = group.random(ZR)
    v = (g ** gamma)
    pk = [g, n, giValues, v]
    dummyVar = group.random(ZR)
    msk = [gamma, dummyVar]
    output = (pk, msk)
    return output

def keygen(pk, msk):
    sk = {}

    g, n, giValues, v = pk
    gamma, dummyVar = msk
    for i in range(1, n+1):
        sk[i] = (giValues[i] ** gamma)
    dummyVar2 = group.random(ZR)
    skComplete = [sk, dummyVar2]
    output = skComplete
    return output

def encrypt(S, pk):
    g, n, giValues, v = pk
    t = group.random(ZR)
    K = (pair(giValues[n], giValues[1]) ** t)
    dotProdEncrypt = group.init(G1)
    for jEncrypt in S:
        dotProdEncrypt = (dotProdEncrypt * giValues[n+1-jEncrypt])
    Hdr2 = ((v * dotProdEncrypt) ** t)
    Hdr1 = (g ** t)
    Hdr = [Hdr1, Hdr2]
    output = (Hdr, K)
    return output

def decrypt(S, i, Hdr, pk, skComplete):
    Hdr1, Hdr2 = Hdr
    g, n, giValues, v = pk
    sk, dummyVar2 = skComplete
    numerator = pair(giValues[i], Hdr2)
    dotProdDecrypt = group.init(G1)
    for jDecrypt in S:
        if ( ( (jDecrypt) != (i) ) ):
            dotProdDecrypt = (dotProdDecrypt * giValues[n+1-jDecrypt+i])
    denominator = pair((sk[i] * dotProdDecrypt), Hdr1)
    KDecrypt = (numerator / denominator)
    output = KDecrypt
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup("SS512")

    (pk, msk) = setup(15)
    skComplete = keygen(pk, msk)
    S = [1, 3, 5, 12, 14]
    (Hdr, K) = encrypt(S, pk)
    print("K:  ", K)
    i = 1
    Krecovered = decrypt(S, i, Hdr, pk, skComplete)
    print("Recovered K = ", Krecovered)
    if (K == Krecovered):
        print("Successful")
    else:
        print("Failed")


if __name__ == '__main__':
    main()

