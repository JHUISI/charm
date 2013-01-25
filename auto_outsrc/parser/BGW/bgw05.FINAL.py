#from bgw05.FINAL.USER import *

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
    skBlinded = {}
    sk = {}
    blindingFactorskBlinded = {}

    blindingFactor0Blinded = group.random(ZR)
    zz = group.random(ZR)
    g, n, giValues, v = pk
    gamma, dummyVar = msk
    for i in range(1, n+1):
        sk[i] = (giValues[i] ** gamma)
    dummyVar2 = group.random(ZR)
    dummyVar2Blinded = dummyVar2
    for y in sk:
        blindingFactorskBlinded[y] = blindingFactor0Blinded
        skBlinded[y] = (sk[y] ** (1 / blindingFactorskBlinded[y]))
    skComplete = [skBlinded, dummyVar2Blinded]
    skCompleteBlinded = [skBlinded, dummyVar2Blinded]
    output = (blindingFactor0Blinded, skCompleteBlinded)
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

def transform(S, i, Hdr, pk, skComplete):
    transformOutputList = {}

    Hdr1, Hdr2 = Hdr
    g, n, giValues, v = pk
    sk, dummyVar2 = skComplete
    transformOutputList[0] = pair(giValues[i], Hdr2)
    numerator = transformOutputList[0]
    transformOutputList[1] = group.init(G1)
    dotProdDecrypt = transformOutputList[1]
    for jDecrypt in S:
        if ( ( (jDecrypt) != (i) ) ):
            pass
            transformOutputList[2] = (dotProdDecrypt * giValues[n+1-jDecrypt+i])
            dotProdDecrypt = transformOutputList[2]
    transformOutputList[3] = pair(sk[i], Hdr1)
    transformOutputList[4] = pair(dotProdDecrypt, Hdr1)
    output = transformOutputList
    return output

def decout(S, i, Hdr, pk, skComplete, transformOutputList, blindingFactor0Blinded):
    Hdr1, Hdr2 = Hdr
    g, n, giValues, v = pk
    sk, dummyVar2 = skComplete
    numerator = transformOutputList[0]
    dotProdDecrypt = transformOutputList[1]
    for jDecrypt in S:
        if ( ( (jDecrypt) != (i) ) ):
            pass
            dotProdDecrypt = transformOutputList[2]
    denominator = ((transformOutputList[3] ** blindingFactor0Blinded) * transformOutputList[4])
    KDecrypt = (numerator * (denominator ** -1))
    #KDecrypt = (numerator * (denominator))
    output = KDecrypt
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup("SS512")

    (pk, msk) = setup(15)
    (blindingFactor0Blinded, skComplete) = keygen(pk, msk)
    S = [1, 3, 5, 12, 14]
    (Hdr, K) = encrypt(S, pk)
    print("K:  ", K)
    i = 1
    transformOutputList = transform(S, i, Hdr, pk, skComplete)
    Krecovered = decout(S, i, Hdr, pk, skComplete, transformOutputList, blindingFactor0Blinded)
    print("Recovered K = ", Krecovered)
    if (K == Krecovered):
        print("Successful")
    else:
        print("Failed")



if __name__ == '__main__':
    main()

