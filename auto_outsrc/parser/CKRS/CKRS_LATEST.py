from  builtInFuncs import * 
import builtInFuncs 
from charm.toolbox.secretutil import SecretUtil

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80


def setup(n, l):
    gl = {}
    hl = {}
    z = {}

    alpha = group.random(ZR)
    t1 = group.random(ZR)
    t2 = group.random(ZR)
    t3 = group.random(ZR)
    t4 = group.random(ZR)
    g = group.random(G1)
    h = group.random(G2)
    omega = (pair(g, h) ** (t1 * (t2 * alpha)))
    for y in range(0, n):
        z[y] = group.random(ZR)
        gl[y] = (g ** z[y])
        hl[y] = (h ** z[y])
    v1 = (g ** t1)
    v2 = (g ** t2)
    v3 = (g ** t3)
    v4 = (g ** t4)
    mpk = [omega, g, h, gl, hl, v1, v2, v3, v4, n, l]
    msk = [alpha, t1, t2, t3, t4]
    output = (mpk, msk)
    return output

def extract(mpk, msk, id):
    bf1 = group.random(ZR)
    idBlinded = id
    omega, g, h, gl, hl, v1, v2, v3, v4, n, l = mpk
    alpha, t1, t2, t3, t4 = msk
    r1 = group.random(ZR)
    r2 = group.random(ZR)
    hID = stringToInt(idBlinded, 5, 32)
    reservedVarName0 = group.init(G2)
    for y in range(0, n):
        reservedVarName1 = (hl[y] ** hID[y])
        reservedVarName0 = (reservedVarName0 * reservedVarName1)
    hashIDDotProd = reservedVarName0
    hashID = (hl[0] * hashIDDotProd)
    d0 = (h ** ((r1 * (t1 * t2)) + (r2 * (t3 * t4))))
    d0Blinded = (d0 ** (1 / bf1))
    halpha = (h ** -alpha)
    hashID2r1 = (hashID ** -r1)
    d1 = ((halpha ** t2) * (hashID2r1 ** t2))
    d1Blinded = (d1 ** (1 / bf1))
    d2 = ((halpha ** t1) * (hashID2r1 ** t1))
    d2Blinded = (d2 ** (1 / bf1))
    hashID2r2 = (hashID ** -r2)
    d3 = (hashID2r2 ** t4)
    d3Blinded = (d3 ** (1 / bf1))
    d4 = (hashID2r2 ** t3)
    d4Blinded = (d4 ** (1 / bf1))
    d5 = ((h ** t1) * (h ** t2))
    d5Blinded = (d5 ** (1 / bf1))
    skBlinded = [idBlinded, d0Blinded, d1Blinded, d2Blinded, d3Blinded, d4Blinded, d5Blinded]
    output = (bf1, skBlinded)
    return output

def encrypt(mpk, M, id):
    omega, g, h, gl, hl, v1, v2, v3, v4, n, l = mpk
    s = group.random(ZR)
    s1 = group.random(ZR)
    s2 = group.random(ZR)
    hID1 = stringToInt(id, 5, 32)
    reservedVarName2 = group.init(G1)
    for y in range(0, n):
        reservedVarName3 = (gl[y] ** hID1[y])
        reservedVarName2 = (reservedVarName2 * reservedVarName3)
    hashID1DotProd = reservedVarName2
    hashID1 = (gl[0] * hashID1DotProd)
    cpr = ((omega ** s) * M)
    c0 = (hashID1 ** s)
    c1 = (v1 ** (s - s1))
    c2 = (v2 ** s1)
    c3 = (v3 ** (s - s2))
    c4 = (v4 ** s2)
    ct = [c0, c1, c2, c3, c4, cpr]
    output = ct
    return output

def transform(skBlinded, ct):
    transformOutputList = {}

    idBlinded, d0Blinded, d1Blinded, d2Blinded, d3Blinded, d4Blinded, d5Blinded = skBlinded
    c0, c1, c2, c3, c4, cpr = ct
    transformOutputList[1] = cpr
    transformOutputList[0] = ((((pair(c0, d0Blinded) * pair(c1, d1Blinded)) * pair(c2, d2Blinded)) * pair(c3, d3Blinded)) * pair(c4, d4Blinded))
    result = transformOutputList[0]
    output = transformOutputList
    return output

def decout(transformOutputList, bf1):
    cpr = transformOutputList[1]
    result = (transformOutputList[0] ** bf1)
    M = (cpr * result)
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup("SS512")
    builtInFuncs.groupObjBuiltInFuncs = group
    builtInFuncs.utilBuiltInFuncs = SecretUtil(group, verbose=False)

    (mpk, msk) = setup(5, 32)
    (blindingFactord0Blinded, skBlinded) = extract(mpk, msk, "test")
    M = group.random(GT)
    print(M)
    print("\n\n\n")
    ct = encrypt(mpk, M, "test")
    transformOutputList = transform(skBlinded, ct)
    M2 = decout(transformOutputList, blindingFactord0Blinded)
    print(M2)

    if (M == M2):
        print("it worked")


if __name__ == '__main__':
    main()

