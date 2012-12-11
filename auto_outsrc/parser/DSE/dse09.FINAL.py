from userFuncs import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80


def setup():
    input = None
    g = group.random(G1)
    w = group.random(G1)
    u = group.random(G1)
    h = group.random(G1)
    v = group.random(G1)
    v1 = group.random(G1)
    v2 = group.random(G1)
    a1 = group.random(ZR)
    a2 = group.random(ZR)
    b = group.random(ZR)
    alpha = group.random(ZR)
    gb = (g ** b)
    ga1 = (g ** a1)
    ga2 = (g ** a2)
    gba1 = (gb ** a1)
    gba2 = (gb ** a2)
    tau1 = (v * (v1 ** a1))
    tau2 = (v * (v2 ** a2))
    tau1b = (tau1 ** b)
    tau2b = (tau2 ** b)
    egga = (pair(g, g) ** (alpha * (a1 * b)))
    galpha = (g ** alpha)
    galpha_a1 = (galpha ** a1)
    mpk = [g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga]
    msk = [galpha, galpha_a1, v, v1, v2, alpha]
    output = (mpk, msk)
    return output

def keygen(mpk, msk, id):
    input = [mpk, msk, id]
    blindingFactorD1Blinded = group.random(ZR)
    blindingFactorD2Blinded = group.random(ZR)
    blindingFactor0Blinded = group.random(ZR)
    idBlinded = id
    zz = group.random(ZR)
    g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga = mpk
    galpha, galpha_a1, v, v1, v2, alpha = msk
    r1 = group.random(ZR)
    r2 = group.random(ZR)
    z1 = group.random(ZR)
    z2 = group.random(ZR)
    tag_k = group.random(ZR)
    tag_kBlinded = tag_k
    r = (r1 + r2)
    id_hash = group.hash(idBlinded, ZR)
    D1 = (galpha_a1 * (v ** r))
    D1Blinded = (D1 ** (1 / blindingFactorD1Blinded))
    D2 = ((g ** -alpha) * ((v1 ** r) * (g ** z1)))
    D2Blinded = (D2 ** (1 / blindingFactorD2Blinded))
    D3 = (gb ** -z1)
    D3Blinded = D3
    D4 = ((v2 ** r) * (g ** z2))
    D4Blinded = (D4 ** (1 / blindingFactor0Blinded))
    D5 = (gb ** -z2)
    D5Blinded = D5
    D6 = (gb ** r2)
    D6Blinded = D6
    D7 = (g ** r1)
    D7Blinded = D7
    K = ((((u ** id_hash) * (w ** tag_kBlinded)) * h) ** r1)
    KBlinded = K
    sk = [idBlinded, D1Blinded, D2Blinded, D3Blinded, D4Blinded, D5Blinded, D6Blinded, D7Blinded, KBlinded, tag_kBlinded]
    skBlinded = [idBlinded, D1Blinded, D2Blinded, D3Blinded, D4Blinded, D5Blinded, D6Blinded, D7Blinded, KBlinded, tag_kBlinded]
    output = (blindingFactorD1Blinded, blindingFactorD2Blinded, blindingFactor0Blinded, blindingFactor0Blinded, skBlinded)
    return output

def encrypt(mpk, M, id):
    C = {}

    input = [mpk, M, id]
    g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga = mpk
    s1 = group.random(ZR)
    s2 = group.random(ZR)
    t = group.random(ZR)
    tag_c = group.random(ZR)
    s = (s1 + s2)
    id_hash2 = group.hash(id, ZR)
    C[0] = (M * (egga ** s2))
    C[1] = (gb ** s)
    C[2] = (gba1 ** s1)
    C[3] = (ga1 ** s1)
    C[4] = (gba2 ** s2)
    C[5] = (ga2 ** s2)
    C[6] = ((tau1 ** s1) * (tau2 ** s2))
    C[7] = (((tau1b ** s1) * (tau2b ** s2)) * (w ** -t))
    E1 = ((((u ** id_hash2) * (w ** tag_c)) * h) ** t)
    E2 = (g ** t)
    ct = [C, E1, E2, tag_c]
    output = ct
    return output

def transform(ct, sk):
    transformOutputList = {}

    input = [ct, sk]
    id, D1, D2, D3, D4, D5, D6, D7, K, tag_k = sk
    C, E1, E2, tag_c = ct
    transformOutputList[0] = ((tag_c - tag_k) ** -1)
    tag = transformOutputList[0]
    transformOutputList[1] = pair(C[1], D1)
    transformOutputList[2] = pair(C[2], D2)
    transformOutputList[3] = (pair(C[3], D3) * pair(C[5], D5))
    transformOutputList[4] = pair(C[4], D4)
    transformOutputList[5] = (pair(C[6], D6) * pair(C[7], D7))
    A2 = transformOutputList[5]
    transformOutputList[6] = (pair(E1, D7) * pair((E2 ** -1), K))
    A4 = transformOutputList[6]
    transformOutputList[7] = (A4 ** tag)
    result0 = transformOutputList[7]
    output = transformOutputList
    return output

def decout(ct, sk, transformOutputList, blindingFactorD1Blinded, blindingFactorD2Blinded, blindingFactor0Blinded):
    input = [ct, sk, transformOutputList, blindingFactorD1Blinded, blindingFactorD2Blinded, blindingFactor0Blinded, blindingFactor0Blinded]
    id, D1, D2, D3, D4, D5, D6, D7, K, tag_k = sk
    C, E1, E2, tag_c = ct
    tag = transformOutputList[0]
    A1 = ((transformOutputList[1] ** blindingFactorD1Blinded) * ((transformOutputList[2] ** blindingFactorD2Blinded) * (transformOutputList[3] * (transformOutputList[4] ** blindingFactor0Blinded))))
    A2 = transformOutputList[5]
    A3 = (A1 * (A2 ** -1))
    A4 = transformOutputList[6]
    result0 = transformOutputList[7]
    result1 = (A3 * (result0 ** -1))
    M = (C[0] * (result1 ** -1))
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('SS512')

    (mpk, msk) = setup()
    (blindingFactorD1Blinded, blindingFactorD2Blinded, blindingFactor0Blinded, blindingFactor0Blinded, skBlinded) = keygen(mpk, msk, "john@example.com")
    M = group.random(GT)
    print(M)
    print("\n\n\n")
    ct = encrypt(mpk, M, "john@example.com")
    transformOutputList = transform(ct, skBlinded)
    M2 = decout(ct, skBlinded, transformOutputList, blindingFactorD1Blinded, blindingFactorD2Blinded, blindingFactor0Blinded)


    print(M2)
    if (M == M2):
        print("successful decryption for outsourcing!!!")
    else:
        print("failed decryption.")


if __name__ == '__main__':
    main()

