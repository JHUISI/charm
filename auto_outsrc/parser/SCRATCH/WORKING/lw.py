from lwUSER import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = "SS512"


def setup():
    g = group.random(G1)
    dummyVar = group.random(G1)
    gpk = [g, dummyVar]
    output = gpk
    return output

def authsetup(gpk, authS):
    msk = {}
    pk = {}

    g, dummyVar = gpk
    Y = len(authS)
    for i in range(0, Y):
        alpha = group.random(ZR)
        y = group.random(ZR)
        z = authS[i]
        eggalph = (pair(g, g) ** alpha)
        gy = (g ** y)
        msk[z] = [alpha, y]
        pk[z] = [eggalph, gy]
    output = (msk, pk)
    return output

def keygen(gpk, msk, gid, userS):
    K = {}
    KBlinded = {}
    blindingFactorKBlinded = {}

    userSBlinded = userS
    gidBlinded = gid
    zz = group.random(ZR)
    g, dummyVar = gpk
    h = group.hash(gidBlinded, G1)
    Y = len(userS)
    for i in range(0, Y):
        z = userS[i]
        K[z] = ((g ** msk[z][0]) * (h ** msk[z][1]))
    for y in K:
        blindingFactorKBlinded[y] = group.random(ZR)
        KBlinded[y] = (K[y] ** (1 / blindingFactorKBlinded[y]))
    sk = [gidBlinded, userSBlinded, KBlinded]
    skBlinded = [gidBlinded, userSBlinded, KBlinded]
    output = (blindingFactorKBlinded, skBlinded)
    return output

def encrypt(pk, gpk, M, policy_str):
    C2 = {}
    C1 = {}
    C3 = {}

    g, dummyVar = gpk
    policy = createPolicy(policy_str)
    attrs = getAttributeList(policy)
    s = group.random(ZR)
    w = 0
    s_sh = calculateSharesDict(s, policy)
    w_sh = calculateSharesDict(w, policy)
    Y = len(s_sh)
    egg = pair(g, g)
    C0 = (M * (egg ** s))
    for y in range(0, Y):
        r = group.random(ZR)
        k = attrs[y]
        C1[k] = ((egg ** s_sh[k]) * (pk[k][0] ** r))
        C2[k] = (g ** r)
        C3[k] = ((pk[k][1] ** r) * (g ** w_sh[k]))
    ct = [policy_str, C0, C1, C2, C3]
    output = ct
    return output

def transform(sk, ct):
    transformOutputList = {}

    policy_str, C0, C1, C2, C3 = ct
    gid, userS, K = sk
    transformOutputList[0] = createPolicy(policy_str)
    policy = transformOutputList[0]
    transformOutputList[1] = prune(policy, userS)
    attrs = transformOutputList[1]
    transformOutputList[2] = getCoefficients(policy)
    coeff = transformOutputList[2]
    transformOutputList[3] = group.hash(gid, G1)
    h_gid = transformOutputList[3]
    transformOutputList[4] = len(attrs)
    Y = transformOutputList[4]
    for y in range(0, Y):
        pass
        transformOutputList[1000+11*y] = GetString(attrs[y])
        kDecrypt = transformOutputList[1000+11*y]
        transformOutputList[1001+11*y] = pair(h_gid, C3[kDecrypt])
        result0 = transformOutputList[1001+11*y]
        transformOutputList[1002+11*y] = (result0 ** coeff[kDecrypt])
        result1 = transformOutputList[1002+11*y]
        transformOutputList[1003+11*y] = (C1[kDecrypt] ** coeff[kDecrypt])
        result2 = transformOutputList[1003+11*y]
        transformOutputList[1004+11*y] = (result1 * result2)
        numerator = transformOutputList[1004+11*y]
        transformOutputList[1005+11*y] = pair(K[kDecrypt], C2[kDecrypt])
        denominator0 = transformOutputList[1005+11*y]
    output = transformOutputList
    return output

def decout(sk, ct, transformOutputList, blindingFactorKBlinded):
    policy_str, C0, C1, C2, C3 = ct
    gid, userS, K = sk
    policy = transformOutputList[0]
    attrs = transformOutputList[1]
    coeff = transformOutputList[2]
    h_gid = transformOutputList[3]
    Y = transformOutputList[4]
    dotProd = group.init(GT)
    for y in range(0, Y):
        pass
        kDecrypt = transformOutputList[1000+11*y]
        result0 = transformOutputList[1001+11*y]
        result1 = transformOutputList[1002+11*y]
        result2 = transformOutputList[1003+11*y]
        numerator = transformOutputList[1004+11*y]
        denominator0 = (transformOutputList[1005+11*y] ** blindingFactorKBlinded[kDecrypt])
        denominator = (denominator0 ** coeff[kDecrypt])
        fraction = (numerator * (denominator ** -1))
        dotProd = (dotProd * fraction)
    M = (C0 * (dotProd ** -1))
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    gpk = setup()
    (msk, pk) = authsetup(gpk, ['ONE', 'TWO', 'THREE', 'FOUR'])
    (blindingFactorKBlinded, skBlinded) = keygen(gpk, msk, "john@example.com", ['ONE', 'TWO', 'THREE'])
    M = group.random(GT)
    ct = encrypt(pk, gpk, M, '((four or three) and (two or one))')
    transformOutputList = transform(skBlinded, ct)
    M2 = decout(skBlinded, ct, transformOutputList, blindingFactorKBlinded)
    print(M)
    print("\n\n\n")
    print(M2)
    print("\n\n")
    if (M == M2):
        print("success")
    else:
        print("failed")


if __name__ == '__main__':
    main()

