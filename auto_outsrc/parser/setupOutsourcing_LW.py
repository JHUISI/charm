from userFuncs_LW import *

g_2 = {}
Y = {}
g = {}
z = {}
sk = {}
attrs = {}
s_sh = {}
w_sh = {}
coeff = {}
K = {}
C1 = {}
C2 = {}
C3 = {}
KBlinded = {}

def setup():
    global g_2
    global g

    input = None
    g = group.random(G1)
    g_2 = group.random(G2)
    gpk = [g, g_2]
    output = gpk
    return output

def authsetup(gpk, authS):
    global Y
    global z

    msk = {}
    pk = {}

    input = [gpk, authS]
    g, g_2 = gpk
    Y = len(authS)
    for i in range(0, Y):
        alpha = group.random(ZR)
        y = group.random(ZR)
        z = authS[i]
        eggalph = (pair(g, g_2) ** alpha)
        g2y = (g_2 ** y)
        msk[z] = [alpha, y]
        pk[z] = [eggalph, g2y]
    output = (msk, pk)
    return output

def keygen(gpk, msk, gid, userS):
    global Y
    global z
    global sk
    global K
    global KBlinded

    blindingFactor_KBlinded = {}

    input = [gpk, msk, gid, userS]
    userSBlinded = userS
    gidBlinded = gid
    zz = group.random(ZR)
    g, g_2 = gpk
    h = group.hash(gidBlinded, G1)
    deleteMeVar = msk[0][0]
    blindingFactor_deleteMeVarBlinded = group.random(ZR)
    deleteMeVarBlinded = (deleteMeVar ** (1 / blindingFactor_deleteMeVarBlinded))
    Y = len(userS)
    for i in range(0, Y):
        z = userS[i]
        K[z] = ((g ** msk[z][0]) * (h ** msk[z][1]))
    for y in K:
        blindingFactor_KBlinded[y] = group.random(ZR)
        KBlinded[y] = (K[y] ** (1 / blindingFactor_KBlinded[y]))
    sk = [gidBlinded, userSBlinded, KBlinded, deleteMeVarBlinded]
    skBlinded = [gidBlinded, userSBlinded, KBlinded, deleteMeVarBlinded]
    output = (blindingFactor_deleteMeVarBlinded, blindingFactor_KBlinded, skBlinded)
    return output

def encrypt(pk, gpk, M, policy_str):
    global Y
    global attrs
    global s_sh
    global w_sh
    global C1
    global C2
    global C3

    input = [pk, gpk, M, policy_str]
    g, g_2 = gpk
    policy = createPolicy(policy_str)
    attrs = getAttributeList(policy)
    egg = pair(g, g_2)
    R = group.random(GT)
    hashRandM = [R, M]
    s = group.hash(hashRandM, ZR)
    s_sesskey = DeriveKey(R)
    C0 = (R * (egg ** s))
    w = 0
    s_sh = calculateSharesDict(s, policy)
    w_sh = calculateSharesDict(w, policy)
    Y = len(s_sh)
    for y in range(0, Y):
        r = group.random(ZR)
        k = attrs[y]
        C1[k] = ((egg ** s_sh[k]) * (pk[k][0] ** r))
        C2[k] = (g_2 ** r)
        C3[k] = ((pk[k][1] ** r) * (g_2 ** w_sh[k]))
        T1 = SymEnc(s_sesskey, M)
    ct = [policy_str, C0, C1, C2, C3, T1]
    output = ct
    return output

