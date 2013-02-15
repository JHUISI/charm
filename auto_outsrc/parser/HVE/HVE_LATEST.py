from HVE_LATEST_USER import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

secparam = 80


def setup(n):
    M = {}
    V = {}
    m = {}
    r = {}
    t = {}
    v = {}
    R = {}
    T = {}

    g1 = group.random(G1)
    g2 = group.random(G2)
    egg = pair(g1, g2)
    y = group.random(ZR)
    Y = (egg ** y)
    for i in range(0, n):
        t[i] = group.random(ZR)
        v[i] = group.random(ZR)
        r[i] = group.random(ZR)
        m[i] = group.random(ZR)
        T[i] = (g1 ** t[i])
        V[i] = (g1 ** v[i])
        R[i] = (g1 ** r[i])
        M[i] = (g1 ** m[i])
    pk = [g1, g2, Y, T, V, R, M, n]
    msk = [y, t, v, r, m]
    output = (pk, msk)
    return output

def keygen(pk, msk, yVector):
    a = {}
    LVectorBlinded = {}
    blindingFactorLVectorBlinded = {}
    blindingFactorYVectorBlinded = {}
    LVector = {}
    YVectorBlinded = {}
    YVector = {}

    bf0 = group.random(ZR)
    g1, g2, Y, T, V, R, M, n = pk
    y, t, v, r, m = msk
    numNonDontCares = 0
    for i in range(0, n):
        if ( ( (yVector[i]) != (2) ) ):
            numNonDontCares = (numNonDontCares + 1)
    sumUSaisUSsoFar = 0
    endForLoop = (numNonDontCares - 1)
    for i in range(0, endForLoop):
        a[i] = group.random(ZR)
        sumUSaisUSsoFar = (sumUSaisUSsoFar + a[i])
    a[numNonDontCares-1] = (y - sumUSaisUSsoFar)
    currentUSaUSindex = 0
    for i in range(0, n):
        if ( ( (yVector[i]) == (2) ) ):
            YVector[i] = group.init(G2)
            LVector[i] = group.init(G2)
        if ( ( (yVector[i]) == (0) ) ):
            YVector[i] = (g2 ** (a[currentUSaUSindex] / r[i]))
            LVector[i] = (g2 ** (a[currentUSaUSindex] / m[i]))
            currentUSaUSindex = (currentUSaUSindex + 1)
        if ( ( (yVector[i]) == (1) ) ):
            YVector[i] = (g2 ** (a[currentUSaUSindex] / t[i]))
            LVector[i] = (g2 ** (a[currentUSaUSindex] / v[i]))
            currentUSaUSindex = (currentUSaUSindex + 1)
    for y in YVector:
        blindingFactorYVectorBlinded[y] = bf0
        YVectorBlinded[y] = (YVector[y] ** (1 / blindingFactorYVectorBlinded[y]))
    for y in LVector:
        blindingFactorLVectorBlinded[y] = bf0
        LVectorBlinded[y] = (LVector[y] ** (1 / blindingFactorLVectorBlinded[y]))
    skBlinded = [YVectorBlinded, LVectorBlinded]
    output = (bf0, skBlinded)
    return output

def encrypt(Message, xVector, pk):
    WVector = {}
    sUSi = {}
    XVector = {}

    g1, g2, Y, T, V, R, M, n = pk
    s = group.random(ZR)
    for i in range(0, n):
        sUSi[i] = group.random(ZR)
    omega = (Message * (Y ** -s))
    C0 = (g1 ** s)
    for i in range(0, n):
        if ( ( (xVector[i]) == (0) ) ):
            XVector[i] = (R[i] ** (s - sUSi[i]))
            WVector[i] = (M[i] ** sUSi[i])
        if ( ( (xVector[i]) == (1) ) ):
            XVector[i] = (T[i] ** (s - sUSi[i]))
            WVector[i] = (V[i] ** sUSi[i])
    CT = [omega, C0, XVector, WVector]
    output = CT
    return output

def transform(CT, skBlinded):
    transformOutputList = {}

    omega, C0, XVector, WVector = CT
    YVectorBlinded, LVectorBlinded = skBlinded
    transformOutputList[1] = omega
    transformOutputList[0] = group.init(G2)
    g2Id = transformOutputList[0]
    nn = len(YVectorBlinded)
    for i in range(0, nn):
        pass
        if ( ( (( (YVectorBlinded[i]) != (g2Id) )) and (( (LVectorBlinded[i]) != (g2Id) )) ) ):
            pass
            transformOutputList[1000+7*i] = (pair(XVector[i], YVectorBlinded[i]) * pair(WVector[i], LVectorBlinded[i]))
            intermediateResults = transformOutputList[1000+7*i]
    output = (transformOutputList, nn)
    return output

def decout(transformOutputList, bf0, nn):
    omega = transformOutputList[1]
    dotProd = group.init(GT)
    g2Id = transformOutputList[0]
    for i in range(0, nn):
        pass
        if ( ( (( (YVectorBlinded[i]) != (g2Id) )) and (( (LVectorBlinded[i]) != (g2Id) )) ) ):
            pass
            intermediateResults = (transformOutputList[1000+7*i] ** bf0)
            dotProd = (dotProd * intermediateResults)
    Message2 = (omega * dotProd)
    output = Message2
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup("SS512")

    (pk, msk) = setup(4)
    (bf0, skBlinded) = keygen(pk, msk, [2, 1, 0, 2])
    M = group.random(GT)
    print(M)
    print("\n\n")
    CT = encrypt(M, [1, 1, 0, 1], pk)
    (transformOutputList, nn) = transform(CT, skBlinded)
    M2 = decout(transformOutputList, bf0, nn)

    print(M2)
    if (M == M2):
        print("success")
    else:
        print("failed")


if __name__ == '__main__':
    main()

