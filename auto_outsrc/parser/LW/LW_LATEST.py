from LW_LATEST_USER import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

secparam = 80


def setup():
    g = group.random(G1)
    gpk = [g]
    output = gpk
    return output

def authsetup(gpk, authS):
    msk = {}
    pk = {}

    [g] = gpk
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

    [g] = gpk
    h = group.hash(gid, G1)
    Y = len(userS)
    for i in range(0, Y):
        z = userS[i]
        K[z] = ((g ** msk[z][0]) * (h ** msk[z][1]))
    for y in K:
        blindingFactorKBlinded[y] = group.random(ZR)
        KBlinded[y] = (K[y] ** (1 / blindingFactorKBlinded[y]))
    skBlinded = [gid, KBlinded]
    output = (blindingFactorKBlinded, skBlinded)
    return output

def encrypt(pk, gpk, M, policy_str):
    C2 = {}
    C1 = {}
    C3 = {}

    [g] = gpk
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

def transform(skBlinded, userS, ct):
    transformOutputList = {}

    policy_str, C0, C1, C2, C3 = ct
    gidBlinded, KBlinded = skBlinded
    transformOutputList[1] = C0
    policy = createPolicy(policy_str)
    attrs = prune(policy, userS)
    coeff = getCoefficients(policy)
    transformOutputList[0] = group.hash(gidBlinded, G1)
    h_gid = transformOutputList[0]
    Y = len(attrs)
    for y in range(0, Y):
        pass
        kDecrypt = GetString(attrs[y])
        transformOutputList[1000+12*y] = pair(h_gid, C3[kDecrypt])
        result0 = transformOutputList[1000+12*y]
        transformOutputList[1001+12*y] = ((result0 ** coeff[kDecrypt]) * (C1[kDecrypt] ** coeff[kDecrypt]))
        numerator = transformOutputList[1001+12*y]
        transformOutputList[1002+12*y] = pair(KBlinded[kDecrypt], C2[kDecrypt])
        denominator0 = transformOutputList[1002+12*y]
    output = (transformOutputList, coeff, Y, attrs)
    return output

def decout(userS, transformOutputList, blindingFactorKBlinded, coeff, Y, attrs):
    C0 = transformOutputList[1]
    h_gid = transformOutputList[0]
    dotProd = group.init(GT)
    for y in range(0, Y):
        pass
        kDecrypt = GetString(attrs[y])
        result0 = transformOutputList[1000+12*y]
        numerator = transformOutputList[1001+12*y]
        denominator0 = (transformOutputList[1002+12*y] ** blindingFactorKBlinded[kDecrypt])
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
    #group = PairingGroup(secparam)

    group = PairingGroup("SS512")

    gpk = setup()
    (msk, pk) = authsetup(gpk, ['ONE', 'TWO', 'THREE', 'FOUR'])
    (blindingFactorKBlinded, skBlinded) = keygen(gpk, msk, "john@example.com", ['ONE', 'TWO', 'THREE'])
    M = group.random(GT)
    ct = encrypt(pk, gpk, M, '((four or three) and (two or one))')
    (transformOutputList, coeff, Y, attrs) = transform(skBlinded, ['ONE', 'TWO', 'THREE'], ct)
    M2 = decout(['ONE', 'TWO', 'THREE'], transformOutputList, blindingFactorKBlinded, coeff, Y, attrs)
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

