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
    blindingFactord0Blinded = group.random(ZR)
    blindingFactord1Blinded = group.random(ZR)
    blindingFactord2Blinded = group.random(ZR)
    blindingFactor0Blinded = group.random(ZR)
    blindingFactor1Blinded = group.random(ZR)
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
    sk = [idBlinded, d0Blinded, d1Blinded, d2Blinded, d3Blinded, d4Blinded]
    skBlinded = [idBlinded, d0Blinded, d1Blinded, d2Blinded, d3Blinded, d4Blinded]
    output = (blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor0Blinded, blindingFactor1Blinded, blindingFactor1Blinded, skBlinded)
    return output

def encrypt(mpk, M, id):

    input = [mpk, M, id]
    omega, g, h, gl, hl, v1, v2, v3, v4, n, l = mpk
    s = group.random(ZR)
    s1 = group.random(ZR)
    s2 = group.random(ZR)
    hID1 = strToId(mpk, id)
    hashID1DotProd = dotprod2(range(0,n), lam_func2, gl, hID1)
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
    input = [sk, ct]
    id, d0, d1, d2, d3, d4 = sk
    c0, c1, c2, c3, c4, cpr = ct
    transformOutputList = {}
    transformOutputList[0] = pair(c0, d0)
    transformOutputList[1] = pair(c1, d1)
    transformOutputList[2] = pair(c2, d2)
    transformOutputList[3] = pair(c3, d3)
    transformOutputList[4] = pair(c4, d4)
    output = transformOutputList
    return output

def decout(sk, ct, transformOutputList, blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor1Blinded):
    input = [sk, ct, transformOutputList, blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor0Blinded, blindingFactor1Blinded, blindingFactor1Blinded]
    id, d0, d1, d2, d3, d4 = sk
    c0, c1, c2, c3, c4, cpr = ct
    result = ((transformOutputList[0] ** blindingFactord0Blinded) * ((transformOutputList[1] ** blindingFactord1Blinded) * ((transformOutputList[2] ** blindingFactord2Blinded) * ((transformOutputList[3] ** blindingFactor0Blinded) * (transformOutputList[4] ** blindingFactor1Blinded)))))
    M = (cpr * result)
    output = M
    return output


if __name__ == "__main__":
    global group
    group = PairingGroup(MNT160)

    S = ['ONE', 'TWO', 'THREE']
    M = "balls on fire345"
    policy_str = '((four or three) and (two or one))'
    n = 10
    l = 5
    id = 'example@email.com'

    (mpk, msk) = setup(n, l)
    (blindingFactord0Blinded, blindingFactord1Blinded, blindingFactord2Blinded, blindingFactor0Blinded, blindingFactor1Blinded, skBlinded) = extract(mpk, msk, id)
    (ct) = encrypt(mpk, M, id)

    f_ct_BSW = open('ct_BSW.charmPickle', 'wb')
    pick_ct_BSW = objectToBytes(ct, group)
    f_ct_BSW.write(pick_ct_BSW)
    f_ct_BSW.close()

    f_sk_BSW = open('sk_BSW.charmPickle', 'wb')
    pick_sk_BSW = objectToBytes(sk, group)
    f_sk_BSW.write(pick_sk_BSW)
    f_sk_BSW.close()

    keys = {'sk':zz, 'pk':mpk[0]}
    writeToFile('keys_BSW_.txt', objectOut(group, keys))

