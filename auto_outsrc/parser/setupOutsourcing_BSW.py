from charm.toolbox.pairinggroup import *

a = {}

def setup():
    global a

    input = None
    a = group.random(ZR)
    g1 = group.random(G1)
    g2 = group.random(G2)
    egga = (pair(g1, g2) ** a)
    msk = a
    output = (g1, g2, egga, msk)
    return output

def keygen(g2, egga, msk):

    input = [g2, egga, msk]
    blindingFactor0Blinded = group.random(ZR)
    zz = group.random(ZR)
    a = msk
    t = group.random(ZR)
    d = (g2 ** (a * t))
    dBlinded = (d ** (1 / blindingFactor0Blinded))
    eggat = (egga ** t)
    pk = eggat
    pkBlinded = pk
    sk = dBlinded
    skBlinded = dBlinded
    output = (pkBlinded, blindingFactor0Blinded, skBlinded)
    return output

def encrypt(g1, pk, M):

    input = [g1, pk, M]
    s1 = group.random(ZR)
    s2 = group.random(ZR)
    s3 = group.random(ZR)
    s = (s1 + (s2 + s3))
    c0 = (M * (pk ** s))
    c1 = (g1 ** s1)
    c2 = (g1 ** s2)
    c3 = (g1 ** s3)
    output = (c0, c1, c2, c3)
    return output

def transform(pk, sk, c0, c1, c2, c3):
    input = [pk, sk, c0, c1, c2, c3]
    d = sk
    transformOutputList = {}
    transformOutputList[0] = (pair(c1, d) * (pair(c2, d) * pair(c3, d)))
    output = transformOutputList
    return output

def decout(pk, sk, c0, c1, c2, c3, transformOutputList, blindingFactor0Blinded):
    input = [pk, sk, c0, c1, c2, c3, transformOutputList, blindingFactor0Blinded]
    d = sk
    result = (transformOutputList[0] ** blindingFactor0Blinded)
    M = (c0 * (result ** -1))
    #M = (c0 * (result))
    output = M
    return output

if __name__ == "__main__":
    global group
    group = PairingGroup(80)

    (g1, g2, egga, msk) = setup()
    (pkBlinded, blindingFactor0Blinded, skBlinded) = keygen(g2, egga, msk)
    M = group.random(GT)
    print(M)
    print("\n")
    (c0, c1, c2, c3) = encrypt(g1, pkBlinded, M)
    transformOutputList = transform(pkBlinded, skBlinded, c0, c1, c2, c3)
    NN = decout(pkBlinded, skBlinded, c0, c1, c2, c3, transformOutputList, blindingFactor0Blinded)
    print(NN)
