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
    g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga = mpk
    galpha, galpha_a1, v, v1, v2, alpha = msk
    r1 = group.random(ZR)
    r2 = group.random(ZR)
    z1 = group.random(ZR)
    z2 = group.random(ZR)
    tag_k = group.random(ZR)
    r = (r1 + r2)
    id_hash = group.hash(id, ZR)
    D1 = (galpha_a1 * (v ** r))
    D2 = ((g ** -alpha) * ((v1 ** r) * (g ** z1)))
    D3 = (gb ** -z1)
    D4 = ((v2 ** r) * (g ** z2))
    D5 = (gb ** -z2)
    D6 = (gb ** r2)
    D7 = (g ** r1)
    K = ((((u ** id_hash) * (w ** tag_k)) * h) ** r1)
    sk = [id, D1, D2, D3, D4, D5, D6, D7, K, tag_k]
    output = sk
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

def decrypt(ct, sk):
    input = [ct, sk]
    id, D1, D2, D3, D4, D5, D6, D7, K, tag_k = sk
    C, E1, E2, tag_c = ct
    tag = ((tag_c - tag_k) ** -1)
    A1 = (pair(C[1], D1) * (pair(C[2], D2) * (pair(C[3], D3) * (pair(C[4], D4) * pair(C[5], D5)))))
    A2 = (pair(C[6], D6) * pair(C[7], D7))
    A3 = (A1 / A2)
    A4 = (pair(E1, D7) / pair(E2, K))
    result0 = (A4 ** tag)
    result1 = (A3 / result0)
    M = (C[0] / result1)
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('SS512')

    (mpk, msk) = setup()
    sk = keygen(mpk, msk, "john@example.com")
    M = group.random(GT)
    print(M)
    print("\n\n\n")
    ct = encrypt(mpk, M, "john@example.com")
    M2 = decrypt(ct, sk)
    print(M2)
    if (M == M2):
        print("successful decryption!!!")
    else:
        print("failed decryption.")

if __name__ == '__main__':
    main()

