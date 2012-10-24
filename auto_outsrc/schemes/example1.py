from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

secparam = 80

d = {}

def setup():

    input = None
    a = group.random(ZR)
    g1 = group.random(G1)
    g2 = group.random(G2)
    egga = (pair(g1, g2) ** a)
    msk = a
    output = (g1, g2, egga, msk)
    return output

def keygen(g2, egga, msk):
    global d

    input = [g2, egga, msk]
    t = group.random(ZR)
    d = (g2 ** (msk * t))
    eggat = (egga ** t)
    pk = eggat
    sk = d
    output = (pk, sk)
    return output

def encrypt(g1, pk, M):

    c = {}

    input = [g1, pk, M]
    s1 = group.random(ZR)
    s2 = group.random(ZR)
    s3 = group.random(ZR)
    s = (s1 + (s2 + s3))
    c[0] = (M * (pk ** s))
    c[1] = (g1 ** s1)
    c[2] = (g1 ** s2)
    c[3] = (g1 ** s3)
    output = c
    return output

def decrypt(pk, sk, c):

    input = [pk, sk, c]
    result = (pair(c[1], d) * (pair(c[2], d) * pair(c[3], d)))
    M = (c[0] / result)
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)
 
    (g1, g2, egga, msk) = setup()

    (pk, sk) = keygen(g2, egga, msk)

    M = group.random(GT)
    c = encrypt(g1, pk, M)

    M_orig = decrypt(pk, sk, c) 
    assert M == M_orig, "failed decryption!"
    print("Successful Decryption!")

if __name__ == '__main__':
    main()

