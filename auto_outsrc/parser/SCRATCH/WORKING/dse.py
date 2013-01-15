from dseUSER import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80


def setup():
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
    galphaUSa1 = (galpha ** a1)
    mpk = [g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga]
    msk = [galpha, galphaUSa1, v, v1, v2, alpha]
    output = (mpk, msk)
    return output

def keygen(mpk, msk, id):
    blindingFactor0Blinded = group.random(ZR)
    idBlinded = id
    zz = group.random(ZR)
    g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga = mpk
    galpha, galphaUSa1, v, v1, v2, alpha = msk
    r1 = group.random(ZR)
    r2 = group.random(ZR)
    z1 = group.random(ZR)
    z2 = group.random(ZR)
    tagUSk = group.random(ZR)
    tagUSkBlinded = (tagUSk ** (1 / blindingFactor0Blinded))
    r = (r1 + r2)
    idUShash = group.hash(idBlinded, ZR)
    D1 = (galphaUSa1 * (v ** r))
    D1Blinded = (D1 ** (1 / blindingFactor0Blinded))
    D2 = ((g ** -alpha) * ((v1 ** r) * (g ** z1)))
    D2Blinded = (D2 ** (1 / blindingFactor0Blinded))
    D3 = (gb ** -z1)
    D3Blinded = (D3 ** (1 / blindingFactor0Blinded))
    D4 = ((v2 ** r) * (g ** z2))
    D4Blinded = (D4 ** (1 / blindingFactor0Blinded))
    D5 = (gb ** -z2)
    D5Blinded = (D5 ** (1 / blindingFactor0Blinded))
    D6 = (gb ** r2)
    D6Blinded = (D6 ** (1 / blindingFactor0Blinded))
    D7 = (g ** r1)
    D7Blinded = (D7 ** (1 / blindingFactor0Blinded))
    K = ((((u ** idUShash) * (w ** tagUSkBlinded)) * h) ** r1)
    KBlinded = (K ** (1 / blindingFactor0Blinded))
    sk = [idBlinded, D1Blinded, D2Blinded, D3Blinded, D4Blinded, D5Blinded, D6Blinded, D7Blinded, KBlinded, tagUSkBlinded]
    skBlinded = [idBlinded, D1Blinded, D2Blinded, D3Blinded, D4Blinded, D5Blinded, D6Blinded, D7Blinded, KBlinded, tagUSkBlinded]
    output = (blindingFactor0Blinded, skBlinded)
    return output

def encrypt(mpk, M, id):
    g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga = mpk
    s1 = group.random(ZR)
    s2 = group.random(ZR)
    t = group.random(ZR)
    tagUSc = group.random(ZR)
    s = (s1 + s2)
    idUShash2 = group.hash(id, ZR)
    C0 = (M * (egga ** s2))
    C1 = (gb ** s)
    C2 = (gba1 ** s1)
    C3 = (ga1 ** s1)
    C4 = (gba2 ** s2)
    C5 = (ga2 ** s2)
    C6 = ((tau1 ** s1) * (tau2 ** s2))
    C7 = (((tau1b ** s1) * (tau2b ** s2)) * (w ** -t))
    E1 = ((((u ** idUShash2) * (w ** tagUSc)) * h) ** t)
    E2 = (g ** t)
    ct = [C0, C1, C2, C3, C4, C5, C6, C7, E1, E2, tagUSc]
    output = ct
    return output

def transform(ct, sk):
    transformOutputList = {}

    id, D1, D2, D3, D4, D5, D6, D7, K, tagUSk = sk
    C0, C1, C2, C3, C4, C5, C6, C7, E1, E2, tagUSc = ct
    transformOutputList[0] = ((tagUSc - tagUSk) ** -1)
    tag = transformOutputList[0]
    transformOutputList[1] = (pair(C1, D1) * (pair(C2, D2) * (pair(C3, D3) * (pair(C4, D4) * pair(C5, D5)))))
    A1 = transformOutputList[1]
    transformOutputList[2] = (pair(C6, D6) * pair(C7, D7))
    A2 = transformOutputList[2]
    transformOutputList[3] = (pair(E1, D7) * pair((E2 ** -1), K))
    A4 = transformOutputList[3]
    output = transformOutputList
    return output

def decout(ct, sk, transformOutputList, blindingFactor0Blinded):
    id, D1, D2, D3, D4, D5, D6, D7, K, tagUSk = sk
    C0, C1, C2, C3, C4, C5, C6, C7, E1, E2, tagUSc = ct
    tag = transformOutputList[0]
    A1 = (transformOutputList[1] ** blindingFactor0Blinded)
    A2 = (transformOutputList[2] ** blindingFactor0Blinded)
    A3 = (A1 * (A2 ** -1))
    A4 = (transformOutputList[3] ** blindingFactor0Blinded)
    result0 = (A4 ** tag)
    result1 = (A3 * (result0 ** -1))
    M = (C0 * (result1 ** -1))
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('SS512')

    (mpk, msk) = setup()
    (blindingFactor0Blinded, skBlinded) = keygen(mpk, msk, "john@example.com")
    M = group.random(GT)
    print(M)
    print("\n\n\n")
    ct = encrypt(mpk, M, "john@example.com")
    transformOutputList = transform(ct, skBlinded)
    M2 = decout(ct, skBlinded, transformOutputList, blindingFactor0Blinded)


    print(M2)
    if (M == M2):
        print("successful decryption for outsourcing!!!")
    else:
        print("failed decryption.")


if __name__ == '__main__':
    main()

