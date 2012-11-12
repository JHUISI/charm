from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80

gb = {}
gba1 = {}
gba2 = {}
gbus2 = {}
g2 = {}
vus2 = {}
galphausa1 = {}
h = {}
tagusc = {}
w2 = {}
tagusk = {}
E1 = {}
v1us2 = {}
hus2 = {}
E2 = {}
K = {}
w = {}
tau2b = {}
tau1b = {}
ga2 = {}
ga1 = {}
u2 = {}
tau2 = {}
tau1 = {}
C3 = {}
C2 = {}
C1 = {}
C0 = {}
C7 = {}
C6 = {}
C5 = {}
C4 = {}
g = {}
v2us2 = {}
egga = {}
alpha = {}
u = {}
D6 = {}
D7 = {}
D4 = {}
D5 = {}
D2 = {}
D3 = {}
D1 = {}

def setup():
    global gb
    global gba1
    global gba2
    global gbus2
    global g2
    global vus2
    global galphausa1
    global h
    global w2
    global v1us2
    global hus2
    global w
    global tau2b
    global tau1b
    global ga2
    global ga1
    global u2
    global tau2
    global tau1
    global g
    global v2us2
    global egga
    global alpha
    global u

    input = None
    g = group.random(G1)
    g2 = group.random(G2)
    w = group.random(G1)
    w2 = group.random(G2)
    u = group.random(G1)
    u2 = group.random(G2)
    h = group.random(G1)
    hus2 = group.random(G2)
    v = group.random(G1)
    vus2 = group.random(G2)
    v1 = group.random(G1)
    v1us2 = group.random(G2)
    v2 = group.random(G1)
    v2us2 = group.random(G2)
    a1 = group.random(ZR)
    a2 = group.random(ZR)
    b = group.random(ZR)
    alpha = group.random(ZR)
    gb = (g ** b)
    gbus2 = (g2 ** b)
    ga1 = (g ** a1)
    ga2 = (g ** a2)
    gba1 = (gb ** a1)
    gba1us2 = (gbus2 ** a1)
    gba2 = (gb ** a2)
    gba2us2 = (gbus2 ** a2)
    tau1 = (v * (v1 ** a1))
    tau1us2 = (vus2 * (v1us2 ** a1))
    tau2 = (v * (v2 ** a2))
    tau2us2 = (vus2 * (v2us2 ** a2))
    tau1b = (tau1 ** b)
    tau1bus2 = (tau1us2 ** b)
    tau2b = (tau2 ** b)
    tau2bus2 = (tau2us2 ** b)
    egga = (pair(g, g2) ** (alpha * (a1 * b)))
    galpha = (g2 ** alpha)
    galphausa1 = (galpha ** a1)
    mpk = [g, g2, gb, gbus2, ga1, ga2, gba1, gba1us2, gba2, gba2us2, tau1, tau1us2, tau2, tau2us2, tau1b, tau1bus2, tau2b, tau2bus2, w, w2, u, u2, h, hus2, egga]
    msk = [galpha, galphausa1, v, vus2, v1, v1us2, v2, v2us2, alpha]
    output = (mpk, msk)
    return output

def keygen(mpk, msk, id):
    global tagusk
    global K
    global D6
    global D7
    global D4
    global D5
    global D2
    global D3
    global D1

    input = [mpk, msk, id]
    blindingFactorD1Blinded = group.random(ZR)
    blindingFactorD2Blinded = group.random(ZR)
    blindingFactor0Blinded = group.random(ZR)
    idBlinded = id
    zz = group.random(ZR)
    g, g2, gb, gbus2, ga1, ga2, gba1, gba1us2, gba2, gba2us2, tau1, tau1us2, tau2, tau2us2, tau1b, tau1bus2, tau2b, tau2bus2, w, w2, u, u2, h, hus2, egga = mpk
    galpha, galphausa1, v, vus2, v1, v1us2, v2, v2us2, alpha = msk
    r1 = group.random(ZR)
    r2 = group.random(ZR)
    z1 = group.random(ZR)
    z2 = group.random(ZR)
    tagusk = group.random(ZR)
    taguskBlinded = tagusk
    r = (r1 + r2)
    idushash = group.hash(idBlinded, ZR)
    D1 = (galphausa1 * (vus2 ** r))
    D1Blinded = (D1 ** (1 / blindingFactorD1Blinded))
    D2 = ((g2 ** -alpha) * ((v1us2 ** r) * (g2 ** z1)))
    D2Blinded = (D2 ** (1 / blindingFactorD2Blinded))
    D3 = (gbus2 ** -z1)
    D3Blinded = D3
    D4 = ((v2us2 ** r) * (g2 ** z2))
    D4Blinded = (D4 ** (1 / blindingFactor0Blinded))
    D5 = (gbus2 ** -z2)
    D5Blinded = D5
    D6 = (gbus2 ** r2)
    D6Blinded = D6
    D7 = (g2 ** r1)
    D7Blinded = D7
    K = ((((u2 ** idushash) * (w2 ** taguskBlinded)) * hus2) ** r1)
    KBlinded = K
    sk = [idBlinded, D1Blinded, D2Blinded, D3Blinded, D4Blinded, D5Blinded, D6Blinded, D7Blinded, KBlinded, taguskBlinded]
    skBlinded = [idBlinded, D1Blinded, D2Blinded, D3Blinded, D4Blinded, D5Blinded, D6Blinded, D7Blinded, KBlinded, taguskBlinded]
    output = (blindingFactorD1Blinded, blindingFactorD2Blinded, blindingFactor0Blinded, blindingFactor0Blinded, skBlinded)
    return output

def encrypt(mpk, M, id):
    global tagusc
    global E1
    global E2
    global C3
    global C2
    global C1
    global C0
    global C7
    global C6
    global C5
    global C4

    input = [mpk, M, id]
    g, g2, gb, gbus2, ga1, ga2, gba1, gba1us2, gba2, gba2us2, tau1, tau1us2, tau2, tau2us2, tau1b, tau1bus2, tau2b, tau2bus2, w, w2, u, u2, h, hus2, egga = mpk
    s1 = group.random(ZR)
    s2 = group.random(ZR)
    t = group.random(ZR)
    tagusc = group.random(ZR)
    s = (s1 + s2)
    idushash2 = group.hash(id, ZR)
    C0 = (M * (egga ** s2))
    C1 = (gb ** s)
    C2 = (gba1 ** s1)
    C3 = (ga1 ** s1)
    C4 = (gba2 ** s2)
    C5 = (ga2 ** s2)
    C6 = ((tau1 ** s1) * (tau2 ** s2))
    C7 = (((tau1b ** s1) * (tau2b ** s2)) * (w ** -t))
    E1 = ((((u ** idushash2) * (w ** tagusc)) * h) ** t)
    E2 = (g ** t)
    ct = [C1, C2, C3, C4, C5, C6, C7, E1, E2, tagusc]
    output = ct
    return output

def transform(ct, sk):

    transformOutputList = {}

    input = [ct, sk]
    id, D1, D2, D3, D4, D5, D6, D7, K, tagusk = sk
    C1, C2, C3, C4, C5, C6, C7, E1, E2, tagusc = ct
    transformOutputList[0] = pair(C1, D1)
    transformOutputList[1] = pair(C2, D2)
    transformOutputList[2] = (pair(C3, D3) * pair(C5, D5))
    transformOutputList[3] = pair(C4, D4)
    transformOutputList[4] = (pair(C6, D6) * pair(C7, D7))
    output = transformOutputList
    return output

def decout(ct, sk, transformOutputList, blindingFactorD1Blinded, blindingFactorD2Blinded, blindingFactor0Blinded):

    input = [ct, sk, transformOutputList, blindingFactorD1Blinded, blindingFactorD2Blinded, blindingFactor0Blinded, blindingFactor0Blinded]
    id, D1, D2, D3, D4, D5, D6, D7, K, tagusk = sk
    C1, C2, C3, C4, C5, C6, C7, E1, E2, tagusc = ct
    tag = ((tagusc - tagusk) ** -1)
    A1 = ((transformOutputList[0] ** blindingFactorD1Blinded) * ((transformOutputList[1] ** blindingFactorD2Blinded) * transformOutputList[2]))
    A2 = transformOutputList[4]
    A3 = (A1 * (A2 ** -1))
    A4 = (pair((E1 ** tag), D7) * pair((E2 ** -tag), K))
    M = (C0 / (A3 * (A4 ** -1)))
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    (mpk, msk) = setup()
    (blindingFactorD1Blinded, blindingFactorD2Blinded, blindingFactor0Blinded, blindingFactor0Blinded, skBlinded) = keygen(mpk, msk, "test")
    M = group.random(GT)
    print(M)
    print("\n\n\n")
    ct = encrypt(mpk, M, "test")
    transformOutputList = transform(ct, skBlinded)
    M2 = decout(ct, skBlinded, transformOutputList, blindingFactorD1Blinded, blindingFactorD2Blinded, blindingFactor0Blinded)
    print(M2)

if __name__ == '__main__':
    main()

