from userFuncs import *

from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80

L = {}
Dn = {}
g1a = {}
policy = {}
A = {}
C = {}
g2 = {}
g1 = {}
K = {}
g2alph = {}
Y = {}
Cpr = {}
Kl = {}
Cn = {}
result0 = {}
g2a = {}
egg = {}
coeff = {}
attrs = {}
sh = {}

def setup():
    global g1a
    global g2
    global g1
    global g2alph
    global g2a
    global egg

    input = None
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
    global L
    global K
    global Y
    global Kl

    Kl = {}

    input = [pk, msk, S]
    blindingFactor0Blinded = group.random(ZR)
    SBlinded = S
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
    sk = [SBlinded, KBlinded, LBlinded, KlBlinded]
    skBlinded = [SBlinded, KBlinded, LBlinded, KlBlinded]
    output = (blindingFactor0Blinded, skBlinded)
    return output

def encrypt(pk, M, policy_str):
    global Dn
    global policy
    global C
    global Y
    global Cpr
    global Cn
    global attrs
    global sh

    Dn = {}
    Cn = {}

    input = [pk, M, policy_str]
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
    global policy
    global A
    global Y
    global result0
    global coeff
    global attrs

    transformOutputList = {}

    input = [pk, sk, ct]
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
    transformOutputList[4] = dotprod2(range(0, Y), lam_func1, attrs, Cn, coeff, L, Kl, Dn)
    A = transformOutputList[4]
    transformOutputList[5] = pair(Cpr, K)
    result0 = transformOutputList[5]
    output = transformOutputList
    return output

def decout(pk, sk, ct, transformOutputList, blindingFactor0Blinded):
    global policy
    global A
    global Y
    global result0
    global coeff
    global attrs

    input = [pk, sk, ct, transformOutputList, blindingFactor0Blinded]
    policy_str, C, Cpr, Cn, Dn = ct
    S, K, L, Kl = sk
    policy = transformOutputList[0]
    attrs = transformOutputList[1]
    coeff = transformOutputList[2]
    Y = transformOutputList[3]
    A = transformOutputList[4]
    result0 = (transformOutputList[5] ** blindingFactor0Blinded)
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
    transformOutputList = transform(pk, skBlinded, ct)
    M2 = decout(pk, skBlinded, ct, transformOutputList, blindingFactor0Blinded)
    print(M2)

    if (M == M2):
        print("it worked")

if __name__ == '__main__':
    main()

