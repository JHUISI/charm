from watersUSER import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = "SS512"


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

    blindingFactor0Blinded = group.random(ZR)
    SBlinded = S
    zz = group.random(ZR)
    g1, g2, egg, g1a, g2a = pk
    g1alph, g2alph = msk
    t = group.random(ZR)
    K = (g2alph * (g2a ** t))
    KBlinded = (K ** (1 / blindingFactor0Blinded))
    L = (g2 ** t)
    LBlinded = (L ** (1 / blindingFactor0Blinded))
    Y = len(S)
    for y in range(0, Y):
        z = S[y]
        Kl[z] = (group.hash(z, G1) ** t)
    for y in Kl:
        blindingFactorKlBlinded[y] = blindingFactor0Blinded
        KlBlinded[y] = (Kl[y] ** (1 / blindingFactorKlBlinded[y]))
    sk = [SBlinded, KBlinded, LBlinded, KlBlinded]
    skBlinded = [SBlinded, KBlinded, LBlinded, KlBlinded]
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
        Cn[k] = ((g1a ** x[1]) * (group.hash(k, G1) ** -r))
        Dn[k] = (g2 ** r)
    ct = [policy_str, C, Cpr, Cn, Dn]
    output = ct
    return output

def transform(pk, sk, ct):
    transformOutputList = {}

    policy_str, C, Cpr, Cn, Dn = ct
    S, K, L, Kl = sk
    transformOutputList[0] = createPolicy(policy_str)
    policy = transformOutputList[0]
    transformOutputList[1] = prune(policy, S)
    attrs = transformOutputList[1]
    transformOutputList[2] = getCoefficients(policy)
    coeff = transformOutputList[2]
    transformOutputList[3] = len(attrs)
    Y = transformOutputList[3]
    for y in range(0, Y):
        pass
        transformOutputList[1000+5*y] = GetString(attrs[y])
        yGetStringSuffix = transformOutputList[1000+5*y]
        transformOutputList[1001+5*y] = (pair((Cn[yGetStringSuffix] ** coeff[yGetStringSuffix]), L) * pair((Kl[yGetStringSuffix] ** coeff[yGetStringSuffix]), Dn[yGetStringSuffix]))
        reservedVarName1 = transformOutputList[1001+5*y]
    transformOutputList[4] = pair(Cpr, K)
    result0 = transformOutputList[4]
    output = transformOutputList
    return output

def decout(pk, sk, ct, transformOutputList, blindingFactor0Blinded):
    policy_str, C, Cpr, Cn, Dn = ct
    S, K, L, Kl = sk
    policy = transformOutputList[0]
    attrs = transformOutputList[1]
    coeff = transformOutputList[2]
    Y = transformOutputList[3]
    reservedVarName0 = group.init(GT)
    for y in range(0, Y):
        pass
        yGetStringSuffix = transformOutputList[1000+5*y]
        reservedVarName1 = (transformOutputList[1001+5*y] ** blindingFactor0Blinded)
        reservedVarName0 = (reservedVarName0 * reservedVarName1)
    A = reservedVarName0
    result0 = (transformOutputList[4] ** blindingFactor0Blinded)
    result1 = (result0 * (A ** -1))
    M = (C * (result1 ** -1))
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

if __name__ == '__main__':
    main()

