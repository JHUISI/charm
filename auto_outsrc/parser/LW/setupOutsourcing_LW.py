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
    s = group.random(ZR)
    w = 0
    s_sh = calculateSharesDict(s, policy)
    w_sh = calculateSharesDict(w, policy)
    Y = len(s_sh)
    egg = pair(g, g_2)
    C0 = (M * (egg ** s))
    for y in range(0, Y):
        r = group.random(ZR)
        k = attrs[y]
        C1[k] = ((egg ** s_sh[k]) * (pk[k][0] ** r))
        C2[k] = (g_2 ** r)
        C3[k] = ((pk[k][1] ** r) * (g_2 ** w_sh[k]))
    ct = [policy_str, C0, C1, C2, C3]
    output = ct
    return output

if __name__ == "__main__":
    global group
    group = PairingGroup(MNT160)

    S = ['ONE', 'TWO', 'THREE']
    M = "balls on fire345"
    policy_str = '((four or three) and (two or one))'

    (msk, pk) = authsetup(gpk, authS)
    (blindingFactor_deleteMeVarBlinded, blindingFactor_KBlinded, skBlinded) = keygen(gpk, msk, gid, userS)
    (ct) = encrypt(pk, gpk, M, policy_str)

    f_ct_LW = open('ct_LW.charmPickle', 'wb')
    pick_ct_LW = objectToBytes(ct, group)
    f_ct_LW.write(pick_ct_LW)
    f_ct_LW.close()

    f_gpk_LW = open('gpk_LW.charmPickle', 'wb')
    pick_gpk_LW = objectToBytes(gpk, group)
    f_gpk_LW.write(pick_gpk_LW)
    f_gpk_LW.close()

    f_skBlinded_LW = open('skBlinded_LW.charmPickle', 'wb')
    pick_skBlinded_LW = objectToBytes(skBlinded, group)
    f_skBlinded_LW.write(pick_skBlinded_LW)
    f_skBlinded_LW.close()

    keys = {'sk':zz, 'pk':pk[4]}
    writeToFile('keys_LW_.txt', objectOut(group, keys))

