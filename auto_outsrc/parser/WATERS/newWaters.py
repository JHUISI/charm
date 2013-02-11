from newWatersUSER import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

secparam = 80


def setup():
    g1 = group.random(G1)
    g2 = group.random(G2)
    alpha = group.random(ZR)
    a = group.random(ZR)
    egg = (pair(g1, g2) ** alpha)
    g1alph = (g1 ** alpha)
    g2alph = (g2 ** alpha)
    g1a = (g1 ** a)
    g2a = (g2 ** a)
    msk = [g1alph, g2alph]
    pk = [g1, g2, egg, g1a, g2a]
    output = (msk, pk)
    return output

def keygen(pk, msk, S):
    Kl = {}

    blindingFactor0Blinded = group.random(ZR)
    zz = group.random(ZR)
    g1, g2, egg, g1a, g2a = pk
    g1alph, g2alph = msk
    t = group.random(ZR)
    K = (g2alph * (g2a ** t))
    KBlinded = (K ** (1 / blindingFactor0Blinded))
    L = (g2 ** t)
    LBlinded = L
    Y = len(S)
    for y in range(0, Y):
        z = S[y]
        Kl[z] = (group.hash(z, G1) ** t)
    KlBlinded = Kl
    skBlinded = [KBlinded, LBlinded, KlBlinded]
    output = (blindingFactor0Blinded, skBlinded)
    return output

def encrypt(pk, M, policy_str):
    Dn = {}
    Cn = {}

    g1, g2, egg, g1a, g2a = pk
    policy = createPolicy(policy_str)
    attrs = getAttributeList(policy)
    s = group.random(ZR)
    sh = calculateSharesList(s, policy)
    Y = len(sh)
    C = (M * (egg ** s))
    Cpr = (g1 ** s)
    for y in range(0, Y):
        r = group.random(ZR)
        k = attrs[y]
        x = sh[y]
        Cn[k] = ((g1a ** x) * (group.hash(k, G1) ** -r))
        Dn[k] = (g2 ** r)
    ct = [policy_str, C, Cpr, Cn, Dn]
    output = ct
    return output

def transform(pk, skBlinded, S, ct):
    transformOutputList = {}

    policy_str, C, Cpr, Cn, Dn = ct
    KBlinded, LBlinded, KlBlinded = skBlinded
    transformOutputList[5] = C
    policy = createPolicy(policy_str)
    transformOutputList[0] = prune(policy, S)
    attrs = transformOutputList[0]
    coeff = getCoefficients(policy)
    transformOutputList[1] = len(attrs)
    Y = transformOutputList[1]
    transformOutputList[2] = group.init(GT)
    reservedVarName0 = transformOutputList[2]
    for y in range(0, Y):
        pass
        transformOutputList[1000+5*y] = GetString(attrs[y])
        yGetStringSuffix = transformOutputList[1000+5*y]
        transformOutputList[1001+5*y] = (pair((Cn[yGetStringSuffix] ** coeff[yGetStringSuffix]), LBlinded) * pair((KlBlinded[yGetStringSuffix] ** coeff[yGetStringSuffix]), Dn[yGetStringSuffix]))
        reservedVarName1 = transformOutputList[1001+5*y]
        transformOutputList[1002+5*y] = (reservedVarName0 * reservedVarName1)
        reservedVarName0 = transformOutputList[1002+5*y]
    transformOutputList[3] = reservedVarName0
    A = transformOutputList[3]
    transformOutputList[4] = pair(Cpr, KBlinded)
    result0 = transformOutputList[4]
    output = (transformOutputList, policy, coeff)
    return output

def decout(pk, S, transformOutputList, blindingFactor0Blinded, policy, coeff):
    C = transformOutputList[5]
    attrs = transformOutputList[0]
    Y = transformOutputList[1]
    reservedVarName0 = transformOutputList[2]
    for y in range(0, Y):
        pass
        yGetStringSuffix = transformOutputList[1000+5*y]
        reservedVarName1 = transformOutputList[1001+5*y]
        reservedVarName0 = transformOutputList[1002+5*y]
    A = transformOutputList[3]
    result0 = (transformOutputList[4] ** blindingFactor0Blinded)
    result1 = (result0 * (A ** -1))
    M = (C * (result1 ** -1))
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup("SS512")

    (msk, pk) = setup()
    S = ['THREE', 'ONE', 'TWO']
    (blindingFactor0Blinded, skBlinded) = keygen(pk, msk, S)
    policy_str = '((ONE or THREE) and (TWO or FOUR))'
    M = group.random(GT)
    print(M)
    print("\n\n\n")
    ct = encrypt(pk, M, policy_str)
    (transformOutputList, policy, coeff) = transform(pk, skBlinded, S, ct)
    M2 = decout(pk, S, transformOutputList, blindingFactor0Blinded, policy, coeff)
    print(M2)

    if (M == M2):
        print("it worked")


if __name__ == '__main__':
    main()

