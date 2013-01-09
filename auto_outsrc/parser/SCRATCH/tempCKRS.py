from tempCKRSUSER import *

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
    blindingFactord0Blinded = group.random(ZR)
    blindingFactord1Blinded = group.random(ZR)
    blindingFactord2Blinded = group.random(ZR)
    blindingFactor0Blinded = group.random(ZR)
    blindingFactor1Blinded = group.random(ZR)
    blindingFactord5Blinded = group.random(ZR)
    idBlinded = id
    zz = group.random(ZR)
    omega, g, h, gl, hl, v1, v2, v3, v4, n, l = mpk
    alpha, t1, t2, t3, t4 = msk
    r1 = group.random(ZR)
    r2 = group.random(ZR)
    hID = stringToInt(id, 5, 32)
    reservedVarName0 = group.init(G2)
    for y in range(0, n):
        reservedVarName1 = (hl[y] ** hID[y])
        reservedVarName0 = (reservedVarName0 * reservedVarName1)
    hashIDDotProd = reservedVarName0
    hashID = (hl[0] * hashIDDotProd)
    d0 = (h ** ((r1 * (t1 * t2)) + (r2 * (t3 * t4))))
    d0Blinded = (d0 ** (1 / blindingFactord0Blinded))
    halpha = (h ** -alpha)
    hashID2r1 = (hashID ** -r1)
    d1 = ((halpha ** t2) * (hashID2r1 ** t2))
    d1Blinded = (d1 ** (1 / blindingFactord1Blinded))
    d2 = ((halpha ** t1) * (hashID2r1 ** t1))
    d2Blinded = (d2 ** (1 / blindingFactord2Blinded))
    hashID2r2 = (hashID ** -r2)
    d3 = (hashID2r2 ** t4)
    d3Blinded = (d3 ** (1 / blindingFactor0Blinded))
    d4 = (hashID2r2 ** t3)
    d4Blinded = (d4 ** (1 / blindingFactor1Blinded))
    d5 = (g ** (t1 * t2))
    d5Blinded = (d5 ** (1 / blindingFactord5Blinded))
    sk = [idBlinded, d0Blinded, d1Blinded, d2Blinded, d3Blinded, d4Blinded, d5Blinded]
    skBlinded = [idBlinded, d0Blinded, d1Blinded, d2Blinded, d3Blinded, d4Blinded, d5Blinded]
    output = (blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor0Blinded, blindingFactor1Blinded, blindingFactor1Blinded, blindingFactord5Blinded, skBlinded)
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

def transform(sk, ct):
    transformOutputList = {}

    id, d0, d1, d2, d3, d4, d5 = sk
    c0, c1, c2, c3, c4, cpr = ct
    transformOutputList[0] = pair(d5, d0)
    transformOutputList[1] = pair(c1, d1)
    transformOutputList[2] = pair(c2, d2)
    transformOutputList[3] = pair(c3, d3)
    transformOutputList[4] = pair(c4, d4)
    output = transformOutputList
    return output

def decout(sk, ct, transformOutputList, blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor1Blinded, blindingFactord5Blinded):
    id, d0, d1, d2, d3, d4, d5 = sk
    c0, c1, c2, c3, c4, cpr = ct
    result = ((transformOutputList[0] ** (blindingFactord0Blinded * blindingFactord5Blinded)) * ((transformOutputList[1] ** blindingFactord1Blinded) * ((transformOutputList[2] ** blindingFactord2Blinded) * ((transformOutputList[3] ** blindingFactor0Blinded) * (transformOutputList[4] ** blindingFactor1Blinded)))))
    M = (cpr * result)
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

if __name__ == '__main__':
    main()

