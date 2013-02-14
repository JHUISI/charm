from BSW_LATEST_USER import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

secparam = 80


def setup():
    g = group.random(G1)
    alpha = group.random(ZR)
    beta = group.random(ZR)
    h = (g ** beta)
    i = (g ** alpha)
    egg = (pair(g, g) ** alpha)
    mk = [beta, i]
    pk = [g, h, egg]
    output = (mk, pk)
    return output

def keygen(pk, mk, S):
    Djp = {}
    DjpBlinded = {}
    blindingFactorDjBlinded = {}
    blindingFactorDjpBlinded = {}
    Dj = {}
    DjBlinded = {}

    bf0 = group.random(ZR)
    g, h, egg = pk
    beta, i = mk
    r = group.random(ZR)
    p0 = (h ** r)
    D = ((i * p0) ** (1 / beta))
    DBlinded = (D ** (1 / bf0))
    Y = len(S)
    for y in range(0, Y):
        sUSy = group.random(ZR)
        y0 = S[y]
        Dj[y0] = (p0 * (group.hash(y0, G1) ** sUSy))
        Djp[y0] = (g ** sUSy)
    for y in Dj:
        blindingFactorDjBlinded[y] = bf0
        DjBlinded[y] = (Dj[y] ** (1 / blindingFactorDjBlinded[y]))
    for y in Djp:
        blindingFactorDjpBlinded[y] = bf0
        DjpBlinded[y] = (Djp[y] ** (1 / blindingFactorDjpBlinded[y]))
    skBlinded = [DBlinded, DjBlinded, DjpBlinded]
    output = (bf0, skBlinded)
    return output

def encrypt(pk, M, policyUSstr):
    Cpr = {}
    Cr = {}

    g, h, egg = pk
    policy = createPolicy(policyUSstr)
    attrs = getAttributeList(policy)
    s = group.random(ZR)
    sh = calculateSharesDict(s, policy)
    Y = len(sh)
    Ctl = (M * (egg ** s))
    C = (h ** s)
    for y in range(0, Y):
        y1 = attrs[y]
        Cr[y1] = (g ** sh[y1])
        Cpr[y1] = (group.hash(y1, G1) ** sh[y1])
    ct = [policyUSstr, Ctl, C, Cr, Cpr]
    output = ct
    return output

def transform(pk, skBlinded, S, ct):
    transformOutputList = {}

    policyUSstr, Ctl, C, Cr, Cpr = ct
    DBlinded, DjBlinded, DjpBlinded = skBlinded
    transformOutputList[1] = Ctl
    policy = createPolicy(policyUSstr)
    attrs = prune(policy, S)
    coeff = getCoefficients(policy)
    Y = len(attrs)
    for y in range(0, Y):
        pass
        yGetStringSuffix = GetString(attrs[y])
        transformOutputList[1000+5*y] = (pair((Cr[yGetStringSuffix] ** coeff[yGetStringSuffix]), DjBlinded[yGetStringSuffix]) * pair((DjpBlinded[yGetStringSuffix] ** -coeff[yGetStringSuffix]), Cpr[yGetStringSuffix]))
        reservedVarName1 = transformOutputList[1000+5*y]
    transformOutputList[0] = pair(C, DBlinded)
    result0 = transformOutputList[0]
    output = (transformOutputList, Y)
    return output

def decout(pk, S, transformOutputList, bf0, Y):
    Ctl = transformOutputList[1]
    reservedVarName0 = group.init(GT)
    for y in range(0, Y):
        pass
        reservedVarName1 = (transformOutputList[1000+5*y] ** bf0)
        reservedVarName0 = (reservedVarName0 * reservedVarName1)
    A = reservedVarName0
    result0 = (transformOutputList[0] ** bf0)
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
    (transformOutputList, Y) = transform(pk, skBlinded, attrs, ct)
    rec_msg = decout(pk, attrs, transformOutputList, blindingFactorDBlinded, Y)
    print("Rec msg =>", rec_msg)

    assert rand_msg == rec_msg, "FAILED Decryption: message is incorrect"
    print("Successful Decryption!!!")



if __name__ == '__main__':
    main()

