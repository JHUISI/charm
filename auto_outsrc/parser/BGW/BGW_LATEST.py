from BGW_LATEST_USER import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

secparam = 80


def setup(n):
    giValues = {}

    g = group.random(G1)
    alpha = group.random(ZR)
    endIndexOfList = ((2 * n) + 1)
    for i in range(1, endIndexOfList):
        giValues[i] = (g ** (alpha ** i))
    gamma = group.random(ZR)
    v = (g ** gamma)
    pk = [g, giValues, v]
    msk = [gamma]
    output = (pk, msk, n)
    return output

def keygen(pk, msk, n):
    skBlinded = {}
    sk = {}
    blindingFactorskBlinded = {}

    bf0 = group.random(ZR)
    g, giValues, v = pk
    [gamma] = msk
    for i in range(1, n+1):
        sk[i] = (giValues[i] ** gamma)
    for y in sk:
        blindingFactorskBlinded[y] = bf0
        skBlinded[y] = (sk[y] ** (1 / blindingFactorskBlinded[y]))
    skCompleteBlinded = [skBlinded]
    output = (bf0, skCompleteBlinded)
    return output

def encrypt(S, pk, n):
    g, giValues, v = pk
    t = group.random(ZR)
    K = (pair(giValues[n], giValues[1]) ** t)
    dotProdEncrypt = group.init(G1)
    for jEncrypt in S:
        dotProdEncrypt = (dotProdEncrypt * giValues[n+1-jEncrypt])
    Hdr2 = ((v * dotProdEncrypt) ** t)
    Hdr1 = (g ** t)
    Hdr = [Hdr1, Hdr2]
    ct = [Hdr, K]
    output = ct
    return output

def transform(S, i, n, Hdr, pk, skCompleteBlinded):
    transformOutputList = {}

    Hdr1, Hdr2 = Hdr
    g, giValues, v = pk
    [skBlinded] = skCompleteBlinded
    transformOutputList[0] = pair(giValues[i], Hdr2)
    numerator = transformOutputList[0]
    transformOutputList[1] = group.init(G1)
    dotProdDecrypt = transformOutputList[1]
    for jDecrypt in S:
        if ( ( (jDecrypt) != (i) ) ):
            pass
            transformOutputList[2] = (dotProdDecrypt * giValues[n+1-jDecrypt+i])
            dotProdDecrypt = transformOutputList[2]
    transformOutputList[3] = pair(skBlinded[i], Hdr1)
    transformOutputList[4] = pair(dotProdDecrypt, Hdr1)
    output = transformOutputList
    return output

def decout(S, i, n, Hdr, pk, skCompleteBlinded, transformOutputList, bf0):
    Hdr1, Hdr2 = Hdr
    g, giValues, v = pk
    [skBlinded] = skCompleteBlinded
    numerator = transformOutputList[0]
    dotProdDecrypt = transformOutputList[1]
    for jDecrypt in S:
        if ( ( (jDecrypt) != (i) ) ):
            pass
            dotProdDecrypt = transformOutputList[2]
    denominator = ((transformOutputList[3] ** bf0) * transformOutputList[4])
    KDecrypt = (numerator * (denominator ** -1))
    output = KDecrypt
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group


    group = PairingGroup("SS512")

    (pk, msk, n) = setup(15)
    (blindingFactor0Blinded, skComplete) = keygen(pk, msk, n)
    S = [1, 3, 5, 12, 14]
    (Hdr, K) = encrypt(S, pk, n)
    print("K:  ", K)
    i = 1
    transformOutputList = transform(S, i, n, Hdr, pk, skComplete)
    Krecovered = decout(S, i, n, Hdr, pk, skComplete, transformOutputList, blindingFactor0Blinded)
    print("Recovered K = ", Krecovered)
    if (K == Krecovered):
        print("Successful")
    else:
        print("Failed")



if __name__ == '__main__':
    main()

