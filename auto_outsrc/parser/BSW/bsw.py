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
    g, h, f, egg = pk
    beta, i = mk
    r = group.random(ZR)
    p0 = (pk[1] ** r)
    D = ((mk[1] * p0) ** (1 / mk[0]))
    Y = len(S)
    for y in range(0, Y):
        s_y = group.random(ZR)
        y0 = S[y]
        #print(y0)
        Dj[y0] = (p0 * (group.hash(y0, G1) ** s_y))
        Djp[y0] = (g ** s_y)
    sk = [S, D, Dj, Djp]
    output = sk
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

def decrypt(pk, sk, ct):
    input = [pk, sk, ct]
    policy_str, Ctl, C, Cr, Cpr = ct
    S, D, Dj, Djp = sk
    policy = createPolicy(policy_str)
    attrs = prune(policy, S)
    coeff = getCoefficients(policy)
    Y = len(attrs)
    #print("Dj:  ", Dj)
    #print("Djp:  ", Djp)
    #print("Cr:  ", Cr)
    #print("Cpr:  ", Cpr)
    A = dotprod2(range(0, Y), lam_func1, attrs, Cr, Dj, Djp, Cpr, coeff)
    result0 = (pair(C, D) / A)
    M = (Ctl / result0)
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup('SS512')

    attrs = ['ONE', 'TWO', 'THREE']
    access_policy = '((four or three) and (two or one))'
    #print("Attributes =>", attrs); print("Policy =>", access_policy)

    (mk, pk) = setup()

    sk = keygen(pk, mk, attrs)
    #print("sk :=>", sk)

    rand_msg = group.random(GT)
    print("msg =>", rand_msg)
    ct = encrypt(pk, rand_msg, access_policy)
    #print("\n\nCiphertext...\n")
    group.debug(ct)

    rec_msg = decrypt(pk, sk, ct)
    #print("\n\nDecrypt...\n")
    print("Rec msg =>", rec_msg)

    assert rand_msg == rec_msg, "FAILED Decryption: message is incorrect"
    print("Successful Decryption!!!")


if __name__ == '__main__':
    main()

