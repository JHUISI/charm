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
    KlBlinded = {}
    Kl = {}
    blindingFactorKlBlinded = {}

    bf0 = group.random(ZR)
    g1, g2, egg, g1a, g2a = pk
    g1alph, g2alph = msk
    t = group.random(ZR)
    K = (g2alph * (g2a ** t))
    KBlinded = (K ** (1 / bf0))
    L = (g2 ** t)
    LBlinded = (L ** (1 / bf0))
    Y = len(S)
    for y in range(0, Y):
        z = S[y]
        Kl[z] = (group.hash(z, G1) ** t)
    for y in Kl:
        blindingFactorKlBlinded[y] = bf0
        KlBlinded[y] = (Kl[y] ** (1 / blindingFactorKlBlinded[y]))
    skBlinded = [KBlinded, LBlinded, KlBlinded]
    output = (bf0, skBlinded)
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
    transformOutputList[1] = C
    policy = createPolicy(policy_str)
    attrs = prune(policy, S)
    coeff = getCoefficients(policy)
    Y = len(attrs)
    for y in range(0, Y):
        pass
        yGetStringSuffix = GetString(attrs[y])
        transformOutputList[1000+5*y] = (pair((Cn[yGetStringSuffix] ** coeff[yGetStringSuffix]), LBlinded) * pair((KlBlinded[yGetStringSuffix] ** coeff[yGetStringSuffix]), Dn[yGetStringSuffix]))
        reservedVarName1 = transformOutputList[1000+5*y]
    transformOutputList[0] = pair(Cpr, KBlinded)
    result0 = transformOutputList[0]
    output = (transformOutputList, Y)
    return output

def decout(pk, S, transformOutputList, bf0, Y):
    C = transformOutputList[1]
    reservedVarName0 = group.init(GT)
    for y in range(0, Y):
        pass
        reservedVarName1 = (transformOutputList[1000+5*y] ** bf0)
        reservedVarName0 = (reservedVarName0 * reservedVarName1)
    A = reservedVarName0
    result0 = (transformOutputList[0] ** bf0)
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
    (transformOutputList, Y) = transform(pk, skBlinded, S, ct)
    M2 = decout(pk, S, transformOutputList, blindingFactor0Blinded, Y)
    print(M2)

    if (M == M2):
        print("it worked")



if __name__ == '__main__':
    main()

