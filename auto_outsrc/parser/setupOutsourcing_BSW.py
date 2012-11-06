from userFuncs_BSW import *

t3 = {}
t1 = {}
gl = {}
v1 = {}
v2 = {}
v3 = {}
v4 = {}
hl = {}
alpha = {}
omega = {}
h = {}
t4 = {}
t2 = {}
c = {}
z = {}

def setup(n, l):
    global t3
    global t1
    global gl
    global v1
    global v2
    global v3
    global v4
    global hl
    global alpha
    global omega
    global h
    global t4
    global t2
    global z

    input = [n, l]
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

    input = [mpk, msk, id]
    idBlinded = id
    zz = group.random(ZR)
    omega, g, h, gl, hl, v1, v2, v3, v4, n, l = mpk
    alpha, t1, t2, t3, t4 = msk
    r1 = group.random(ZR)
    r2 = group.random(ZR)
    hID = strToId(mpk, id)
    hashIDDotProd = dotprod2(range(0,n), lam_func1, hl, hID)
    hashID = (hl[0] * hashIDDotProd)
    d0 = (h ** ((r1 * (t1 * t2)) + (r2 * (t3 * t4))))
    blindingFactor_d0Blinded = group.random(ZR)
    d0Blinded = (d0 ** (1 / blindingFactor_d0Blinded))
    halpha = (h ** -alpha)
    hashID2r1 = (hashID ** -r1)
    d1 = ((halpha ** t2) * (hashID2r1 ** t2))
    blindingFactor_d1Blinded = group.random(ZR)
    d1Blinded = (d1 ** (1 / blindingFactor_d1Blinded))
    d2 = ((halpha ** t1) * (hashID2r1 ** t1))
    blindingFactor_d2Blinded = group.random(ZR)
    d2Blinded = (d2 ** (1 / blindingFactor_d2Blinded))
    hashID2r2 = (hashID ** -r2)
    d3 = (hashID2r2 ** t4)
    blindingFactor_d3Blinded = group.random(ZR)
    d3Blinded = (d3 ** (1 / blindingFactor_d3Blinded))
    d4 = (hashID2r2 ** t3)
    blindingFactor_d4Blinded = group.random(ZR)
    d4Blinded = (d4 ** (1 / blindingFactor_d4Blinded))
    sk = [idBlinded, d0Blinded, d1Blinded, d2Blinded, d3Blinded, d4Blinded]
    skBlinded = [idBlinded, d0Blinded, d1Blinded, d2Blinded, d3Blinded, d4Blinded]
    output = (blindingFactor_d0Blinded, blindingFactor_d1Blinded, blindingFactor_d2Blinded, blindingFactor_d3Blinded, blindingFactor_d4Blinded, skBlinded)
    return output

def encrypt(mpk, M, id):
    global c

    input = [mpk, M, id]
    omega, g, h, gl, hl, v1, v2, v3, v4, n, l = mpk
    s = group.random(ZR)
    s1 = group.random(ZR)
    s2 = group.random(ZR)
    hID1 = strToId(mpk, id)
    hashID1DotProd = dotprod2(range(0,n), lam_func2, gl, hID1)
    hashID1 = (gl[0] * hashID1DotProd)
    c_pr = ((omega ** s) * M)
    c[0] = (hashID1 ** s)
    c[1] = (v1 ** (s - s1))
    c[2] = (v2 ** s1)
    c[3] = (v3 ** (s - s2))
    c[4] = (v4 ** s2)
    ct = [c, c_pr]
    output = ct
    return output

