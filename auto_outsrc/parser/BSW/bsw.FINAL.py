from userFuncs import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80


def setup():
    input = None
    g = group.random(G1)
    alpha = group.random(ZR)
    beta = group.random(ZR)
    h = (g ** beta)
    f = (g ** (1 / beta))
    i = (g ** alpha)
    egg = (pair(g, g) ** alpha)
    mk = [beta, i]
    pk = [g, h, f, egg]
    output = (mk, pk)
    return output

def keygen(pk, mk, S):
    Djp = {}
    Dj = {}

    input = [pk, mk, S]
    blindingFactorDBlinded = group.random(ZR)
    SBlinded = S
    zz = group.random(ZR)
    g, h, f, egg = pk
    beta, i = mk
    r = group.random(ZR)
    p0 = (pk[1] ** r)
    D = ((mk[1] * p0) ** (1 / mk[0]))
    DBlinded = (D ** (1 / blindingFactorDBlinded))
    Y = len(S)
    for y in range(0, Y):
        s_y = group.random(ZR)
        y0 = S[y]
        Dj[y0] = (p0 * (group.hash(y0, G1) ** s_y))
        Djp[y0] = (g ** s_y)
    DjpBlinded = Djp
    DjBlinded = Dj
    sk = [SBlinded, DBlinded, DjBlinded, DjpBlinded]
    skBlinded = [SBlinded, DBlinded, DjBlinded, DjpBlinded]
    output = (blindingFactorDBlinded, skBlinded)
    return output

def encrypt(pk, M, policy_str):
    share = {}
    Cpr = {}
    Cr = {}

    input = [pk, M, policy_str]
    g, h, f, egg = pk
    policy = createPolicy(policy_str)
    attrs = getAttributeList(policy)
    s = group.random(ZR)
    sh = calculateSharesDict(s, policy)
    Y = len(sh)
    Ctl = (M * (egg ** s))
    C = (h ** s)
    for y in range(0, Y):
        y1 = attrs[y]
        share[y1] = sh[y1]
        Cr[y1] = (g ** share[y1])
        Cpr[y1] = (group.hash(y1, G1) ** share[y1])
    ct = [policy_str, Ctl, C, Cr, Cpr]
    output = ct
    return output

def transform(pk, sk, ct):
    transformOutputList = {}

    input = [pk, sk, ct]
    policy_str, Ctl, C, Cr, Cpr = ct
    S, D, Dj, Djp = sk
    transformOutputList[0] = createPolicy(policy_str)
    policy = transformOutputList[0]
    transformOutputList[1] = prune(policy, S)
    attrs = transformOutputList[1]
    transformOutputList[2] = getCoefficients(policy)
    coeff = transformOutputList[2]
    transformOutputList[3] = len(attrs)
    Y = transformOutputList[3]
    transformOutputList[4] = dotprod2(range(0, Y), lam_func1, attrs, Cr, coeff, Dj, Djp, Cpr)
    A = transformOutputList[4]
    transformOutputList[5] = pair(C, D)
    result0 = transformOutputList[5]
    output = transformOutputList
    return output

def decout(pk, sk, ct, transformOutputList, blindingFactorDBlinded):
    input = [pk, sk, ct, transformOutputList, blindingFactorDBlinded]
    policy_str, Ctl, C, Cr, Cpr = ct
    S, D, Dj, Djp = sk
    policy = transformOutputList[0]
    attrs = transformOutputList[1]
    coeff = transformOutputList[2]
    Y = transformOutputList[3]
    A = transformOutputList[4]
    result0 = (transformOutputList[5] ** blindingFactorDBlinded)
    result1 = (result0 * (A ** -1))
    M = (Ctl * (result1 ** -1))
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('SS512')

    attrs = ['ONE', 'TWO', 'THREE']
    access_policy = '((four or three) and (two or one))'

    (mk, pk) = setup()

    (blindingFactorDBlinded, skBlinded) = keygen(pk, mk, attrs)

    rand_msg = group.random(GT)
    print("msg =>", rand_msg)
    ct = encrypt(pk, rand_msg, access_policy)
    transformOutputList = transform(pk, skBlinded, ct)
    rec_msg = decout(pk, skBlinded, ct, transformOutputList, blindingFactorDBlinded)
    print("Rec msg =>", rec_msg)

    assert rand_msg == rec_msg, "FAILED Decryption: message is incorrect"
    print("Successful Decryption!!!")



if __name__ == '__main__':
    main()

