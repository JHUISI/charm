from userFuncs import *

from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80

g0b = {}
d0 = {}
g1b = {}
A = {}
C = {}
B = {}
D = {}
g1 = {}
denominator = {}
hb = {}
d = {}
g = {}
h = {}
v = {}
gb = {}

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
    global g0b
    global g1b
    global g1
    global hb
    global g
    global h
    global v
    global gb

    h = {}
    delta = {}
    hb = {}

    input = [l, z]
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
    global d0
    global d

    d = {}
    r = {}

    input = [mpk, mk, id]
    blindingFactor0Blinded = group.random(ZR)
    zz = group.random(ZR)
    g, g1, h, gb, g1b, hb, v, l, z = mpk
    g0b, dummyVar = mk
    Id = stringToInt(id, 5, 32)
    for y in range(0, 5):
        r[y] = group.random(ZR)
        d[y] = (gb ** r[y])
    dBlinded = d
    d0DotProdCalc = dotprod2(range(0,5), lam_func1, g1b, Id, hb, r)
    d0 = (g0b * d0DotProdCalc)
    d0Blinded = (d0 ** (1 / blindingFactor0Blinded))
    pk = [id, None]
    pkBlinded = pk
    sk = [d0Blinded, dBlinded]
    skBlinded = [d0Blinded, dBlinded]
    output = (pkBlinded, blindingFactor0Blinded, skBlinded)
    return output

def encrypt(mpk, pk, M):
    global A
    global C
    global B

    C = {}

    input = [mpk, pk, M]
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
    global D
    global denominator

    transformOutputList = {}

    input = [pk, sk, ct]
    d0, d = sk
    A, B, C = ct
    transformOutputList[0] = (pair(C[0], d[0]) * (pair(C[1], d[1]) * (pair(C[2], d[2]) * (pair(C[3], d[3]) * pair(C[4], d[4])))))
    D = transformOutputList[0]
    transformOutputList[1] = pair(B, d0)
    denominator = transformOutputList[1]
    output = transformOutputList
    return output

def decout(pk, sk, ct, transformOutputList, blindingFactor0Blinded):
    global D
    global denominator

    input = [pk, sk, ct, transformOutputList, blindingFactor0Blinded]
    d0, d = sk
    A, B, C = ct
    D = transformOutputList[0]
    denominator = (transformOutputList[1] ** blindingFactor0Blinded)
    fraction = (D * (denominator ** -1))
    M = (A * fraction)
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    (mpk, mk) = setup(5, 32)
    (pkBlinded, blindingFactor0Blinded, skBlinded) = keygen(mpk, mk, "test")
    M = group.random(GT)
    print(M)
    print("\n\n\n")
    ct = encrypt(mpk, pkBlinded, M)
    transformOutputList = transform(pkBlinded, skBlinded, ct)
    M2 = decout(pkBlinded, skBlinded, ct, transformOutputList, blindingFactor0Blinded)
    print(M2)

if __name__ == '__main__':
    main()

