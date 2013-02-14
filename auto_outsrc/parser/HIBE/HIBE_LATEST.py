from HIBE_LATEST_USER import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

l = 5

secparam = 80

def stringToInt(strID, zz, ll):
    '''Hash the identity string and break it up in to l bit pieces'''
    h = hashlib.new('sha1')
    h.update(bytes(strID, 'utf-8'))
    _hash = Bytes(h.digest())
    val = Conversion.OS2IP(_hash) #Convert to integer format
    bstr = bin(val)[2:]   #cut out the 0b header

    v=[]
    for i in range(zz):  #z must be greater than or equal to 1
        binsubstr = bstr[ll*i : ll*(i+1)]
        intval = int(binsubstr, 2)
        intelement = group.init(ZR, intval)
        v.append(intelement)
    return v


def setup(l, z):
    h = {}
    delta = {}
    hb = {}

    alpha = group.random(ZR)
    beta = group.random(ZR)
    g = group.random(G1)
    gb = group.random(G2)
    g1 = (g ** alpha)
    g1b = (gb ** alpha)
    for y in range(0, l):
        delta[y] = group.random(ZR)
        h[y] = (g ** delta[y])
        hb[y] = (gb ** delta[y])
    g0b = (gb ** (alpha * beta))
    v = pair(g, g0b)
    mpk = [g, g1, h, gb, g1b, hb, v]
    mk = [g0b]
    output = (mpk, mk)
    return output

def keygen(mpk, mk, id):
    d = {}
    dBlinded = {}
    r = {}
    blindingFactordBlinded = {}

    bf0 = group.random(ZR)
    g, g1, h, gb, g1b, hb, v = mpk
    [g0b] = mk
    Id = stringToInt(id, 5, 32)
    for y in range(0, 5):
        r[y] = group.random(ZR)
        d[y] = (gb ** r[y])
    for y in d:
        blindingFactordBlinded[y] = bf0
        dBlinded[y] = (d[y] ** (1 / blindingFactordBlinded[y]))
    resVarName0 = group.init(G2)
    for y in range(0, 5):
        resVarName1 = (((g1b ** Id[y]) * hb[y]) ** r[y])
        resVarName0 = (resVarName0 * resVarName1)
    d0DotProdCalc = resVarName0
    d0 = (g0b * d0DotProdCalc)
    d0Blinded = (d0 ** (1 / bf0))
    pk = [id]
    skBlinded = [d0Blinded, dBlinded]
    output = (pk, bf0, skBlinded)
    return output

def encrypt(mpk, pk, M):
    C = {}

    g, g1, h, gb, g1b, hb, v = mpk
    [id] = pk
    s = group.random(ZR)
    A = (M * (v ** s))
    B = (g ** s)
    Id = stringToInt(id, 5, 32)
    for y in range(0, 5):
        C[y] = (((g1 ** Id[y]) * h[y]) ** s)
    ct = [A, B, C]
    output = ct
    return output

def transform(pk, skBlinded, ct):
    transformOutputList = {}

    d0Blinded, dBlinded = skBlinded
    A, B, C = ct
    transformOutputList[1] = A
    for y in range(0, 5):
        pass
        transformOutputList[1000+3*y] = pair(C[y], dBlinded[y])
        resVarName3 = transformOutputList[1000+3*y]
    transformOutputList[0] = pair(B, d0Blinded)
    denominator = transformOutputList[0]
    output = transformOutputList
    return output

def decout(pk, transformOutputList, bf0):
    A = transformOutputList[1]
    resVarName2 = group.init(GT)
    for y in range(0, 5):
        pass
        resVarName3 = (transformOutputList[1000+3*y] ** bf0)
        resVarName2 = (resVarName2 * resVarName3)
    D = resVarName2
    denominator = (transformOutputList[0] ** bf0)
    fraction = (D * (denominator ** -1))
    M = (A * fraction)
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup("SS512")

    (mpk, mk) = setup(5, 32)
    (pkBlinded, blindingFactor0Blinded, skBlinded) = keygen(mpk, mk, "test")
    M = group.random(GT)
    print(M)
    print("\n\n\n")
    ct = encrypt(mpk, pkBlinded, M)
    transformOutputList = transform(pkBlinded, skBlinded, ct)
    M2 = decout(pkBlinded, transformOutputList, blindingFactor0Blinded)
    print(M2)

    if (M == M2):
        print("it worked")


if __name__ == '__main__':
    main()

