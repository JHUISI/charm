from userFuncs import *

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80

husgid = {}
attrs = {}
gus2 = {}
policy = {}
C1 = {}
C0 = {}
K = {}
C3 = {}
Y = {}
C2 = {}
g = {}
y = {}
z = {}
coeff = {}
sussh = {}
wussh = {}
KBlinded = {}

def setup():
    global gus2
    global g

    input = None
    g = group.random(G1)
    gus2 = group.random(G2)
    gpk = [g, gus2]
    output = gpk
    return output

def authsetup(gpk, authS):
    global Y
    global y
    global z

    msk = {}
    pk = {}

    input = [gpk, authS]
    g, gus2 = gpk
    Y = len(authS)
    for i in range(0, Y):
        alpha = group.random(ZR)
        y = group.random(ZR)
        z = authS[i]
        eggalph = (pair(g, gus2) ** alpha)
        g2y = (gus2 ** y)
        msk[z] = [alpha, y]
        pk[z] = [eggalph, g2y]
    output = (msk, pk)
    return output

def keygen(gpk, msk, gid, userS):
    global K
    global Y
    global z
    global KBlinded

    K = {}
    KBlinded = {}
    blindingFactorKBlinded = {}

    input = [gpk, msk, gid, userS]
    userSBlinded = userS
    gidBlinded = gid
    zz = group.random(ZR)
    g, gus2 = gpk
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
    sk = [gid, userS, K]
    output = sk
    return output

def encrypt(pk, gpk, M, policyusstr):
    global attrs
    global policy
    global C1
    global C0
    global C3
    global Y
    global C2
    global sussh
    global wussh

    C2 = {}
    C1 = {}
    C3 = {}

    input = [pk, gpk, M, policyusstr]
    g, gus2 = gpk
    policy = createPolicy(policyusstr)
    attrs = getAttributeList(policy)
    s = group.random(ZR)
    w = 0
    sussh = calculateSharesDict(s, policy)
    wussh = calculateSharesDict(w, policy)
    Y = len(sussh)
    egg = pair(g, gus2)
    C0 = (M * (egg ** s))
    for y in range(0, Y):
        r = group.random(ZR)
        k = attrs[y]
        C1[k] = ((egg ** sussh[k]) * (pk[k][0] ** r))
        C2[k] = (gus2 ** r)
        C3[k] = ((pk[k][1] ** r) * (gus2 ** wussh[k]))
    ct = [policyusstr, C0, C1, C2, C3]
    output = ct
    return output

def decrypt(gpk, sk, ct):
    g, gus2 = gpk
    policyusstr, C0, C1, C2, C3 = ct
    gid, userS, K = sk
    policy = createPolicy(policyusstr)
    attrs = prune(policy, userS)
    coeff = getCoefficients(policy)
    husgid = group.hash(gid, G1)
    Y = len(attrs)
    
    A = dotprod2(range(0, Y), lam_func1, attrs, C1, coeff, husgid, C3, K, C2)
    M = (C0 * (A ** -1))
    return M

def transform(gpk, sk, ct):
    global husgid
    global attrs
    global policy
    global Y
    global coeff

    transformOutputList = {}

    input = [gpk, sk, ct]
    g, gus2 = gpk
    policyusstr, C0, C1, C2, C3 = ct
    gid, userS, K = sk
    transformOutputList[0] = createPolicy(policyusstr)
    policy = transformOutputList[0]
    transformOutputList[1] = prune(policy, userS)
    attrs = transformOutputList[1]
    transformOutputList[2] = getCoefficients(policy)
    coeff = transformOutputList[2]
    transformOutputList[3] = group.hash(gid, G1)
    husgid = transformOutputList[3]
    transformOutputList[4] = len(attrs)
    Y = transformOutputList[4]
    output = transformOutputList
    return output

def decout(gpk, sk, ct, transformOutputList, blindingFactorKBlinded):
    global husgid
    global attrs
    global policy
    global Y
    global coeff

    input = [gpk, sk, ct, transformOutputList, blindingFactorKBlinded]
    g, gus2 = gpk
    policyusstr, C0, C1, C2, C3 = ct
    gid, userS, K = sk
    policy = transformOutputList[0]
    attrs = transformOutputList[1]
    coeff = transformOutputList[2]
    husgid = transformOutputList[3]
    Y = transformOutputList[4]

    for y in K:
        K[y] = (K[y] ** blindingFactorKBlinded[y])



    A = dotprod2(range(0, Y), lam_func1, attrs, C1, coeff, husgid, C3, K, C2)
    M = (C0 * (A ** -1))
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    gpk = setup()
    authS = ['ONE', 'TWO', 'THREE', 'FOUR']
    (msk, pk) = authsetup(gpk, authS)
    gid = "bob"
    userS = ['THREE', 'ONE', 'TWO']
    #(blindingFactorKBlinded, skBlinded) = keygen(gpk, msk, gid, userS)
    sk = keygen(gpk, msk, gid, userS)
    M = group.random(GT)
    policyusstr = '((ONE or THREE) and (TWO or FOUR))'
    print(M)
    print("\n\n\n")
    ct = encrypt(pk, gpk, M, policyusstr)

    M3 = decrypt(gpk, sk, ct)
    print(M3)

    #transformOutputList = transform(gpk, skBlinded, ct)
    #M2 = decout(gpk, skBlinded, ct, transformOutputList, blindingFactorKBlinded)
    #print(M2)

if __name__ == '__main__':
    main()

