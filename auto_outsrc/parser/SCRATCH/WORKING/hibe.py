from hibeUSER import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

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
    mpk = [g, g1, h, gb, g1b, hb, v, l, z]
    mk = [g0b, None]
    output = (mpk, mk)
    return output

def keygen(mpk, mk, id):
    d = {}
    dBlinded = {}
    r = {}
    blindingFactordBlinded = {}

    blindingFactor0Blinded = group.random(ZR)
    zz = group.random(ZR)
    g, g1, h, gb, g1b, hb, v, l, z = mpk
    g0b, dummyVar = mk
    Id = stringToInt(id, 5, 32)
    for y in range(0, 5):
        r[y] = group.random(ZR)
        d[y] = (gb ** r[y])
    for y in d:
        blindingFactordBlinded[y] = blindingFactor0Blinded
        dBlinded[y] = (d[y] ** (1 / blindingFactordBlinded[y]))
    reservedVarName0 = group.init(G2)
    for y in range(0, 5):
        reservedVarName1 = (((g1b ** Id[y]) * hb[y]) ** r[y])
        reservedVarName0 = (reservedVarName0 * reservedVarName1)
    d0DotProdCalc = reservedVarName0
    d0 = (g0b * d0DotProdCalc)
    d0Blinded = (d0 ** (1 / blindingFactor0Blinded))
    dummyVar3 = group.random(ZR)
    pk = [id, dummyVar3]
    pkBlinded = pk
    sk = [d0Blinded, dBlinded]
    skBlinded = [d0Blinded, dBlinded]
    output = (pkBlinded, blindingFactor0Blinded, skBlinded)
    return output

def encrypt(mpk, pk, M):
    C = {}

    g, g1, h, gb, g1b, hb, v, l, z = mpk
    id, dummyVar2 = pk
    s = group.random(ZR)
    A = (M * (v ** s))
    B = (g ** s)
    Id = stringToInt(id, 5, 32)
    for y in range(0, 5):
        C[y] = (((g1 ** Id[y]) * h[y]) ** s)
    ct = [A, B, C]
    output = ct
    return output

def transform(pk, sk, ct):
    transformOutputList = {}

    d0, d = sk
    A, B, C = ct
    for y in range(0, 5):
        pass
        transformOutputList[1000+3*y] = pair(C[y], d[y])
        reservedVarName3 = transformOutputList[1000+3*y]
    transformOutputList[0] = pair(B, d0)
    denominator = transformOutputList[0]
    output = transformOutputList
    return output

def decout(pk, sk, ct, transformOutputList, blindingFactor0Blinded):
    d0, d = sk
    A, B, C = ct
    reservedVarName2 = group.init(GT)
    for y in range(0, 5):
        pass
        reservedVarName3 = (transformOutputList[1000+3*y] ** blindingFactor0Blinded)
        reservedVarName2 = (reservedVarName2 * reservedVarName3)
    D = reservedVarName2
    denominator = (transformOutputList[0] ** blindingFactor0Blinded)
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
    M2 = decout(pkBlinded, skBlinded, ct, transformOutputList, blindingFactor0Blinded)
    print(M2)

    if (M == M2):
        print("it worked")


if __name__ == '__main__':
    main()

