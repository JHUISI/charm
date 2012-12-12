from userFuncs import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80


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

    g, dummyVar = gpk
    h = group.hash(gid, G1)
    Y = len(userS)
    for i in range(0, Y):
        z = userS[i]
        K[z] = ((g ** msk[z][0]) * (h ** msk[z][1]))
    sk = [gid, userS, K]
    output = sk
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

def decrypt(sk, ct):
    policy_str, C0, C1, C2, C3 = ct
    gid, userS, K = sk
    policy = createPolicy(policy_str)
    attrs = prune(policy, userS)
    coeff = getCoefficients(policy)
    h_gid = group.hash(gid, G1)
    Y = len(attrs)
    dotProd = group.init(GT)
    for y in range(0, Y):
        k = GetString(attrs[y])
        print(k)
        result0 = pair(h_gid, C3[k])
        result1 = (result0 ** coeff[k])
        result2 = (C1[k] ** coeff[k])
        numerator = (result1 * result2)
        denominator0 = pair(K[k], C2[k])
        denominator = (denominator0 ** coeff[k])
        fraction = (numerator / denominator)
        dotProd = (dotProd * fraction)
    M = (C0 / dotProd)
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    gpk = setup()
    (msk, pk) = authsetup(gpk, ['ONE', 'TWO', 'THREE', 'FOUR'])
    sk = keygen(gpk, msk, "john@example.com", ['ONE', 'TWO', 'THREE'])
    M = group.random(GT)
    ct = encrypt(pk, gpk, M, '((four or three) and (two or one))')
    M2 = decrypt(sk, ct)
    print(M)
    print("\n\n\n")
    print(M2)


if __name__ == '__main__':
    main()

