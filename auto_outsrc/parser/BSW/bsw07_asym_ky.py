import userFuncs2
import builtInFuncs
from userFuncs2 import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

secparam = 80


def setup():
    gG1 = group.random(G1)
    gG2 = group.random(G2)
    alpha = group.random(ZR)
    beta = group.random(ZR)
    hG1 = (gG1 ** beta)
    hG2 = (gG2 ** beta)
    i = (gG1 ** alpha)
    egg = (pair(gG1, gG2) ** alpha)
    mk = [beta, i]
    pk = [gG1, gG2, hG1, hG2, egg]
    output = (mk, pk)
    return output

def keygen(pk, mk, S):
    Djp = {}
    Dj = {}

    r = group.random(ZR)
    p0 = (pk[2] ** r)
    D = ((mk[1] * p0) ** (1 / mk[0]))
    Y = len(S)
    for y in range(0, Y):
        s_y = group.random(ZR)
        y0 = S[y]
        Dj[y0] = (p0 * (group.hash(y0, G1) ** s_y))
        Djp[y0] = (pk[1] ** s_y)
    sk = [S, D, Dj, Djp]
    output = sk
    return output

def encrypt(pk, M, policy_str):
    share = {}
    Cpr = {}
    Cr = {}

    gG1, gG2, hG1, hG2, egg = pk
    policy = createPolicy(policy_str)
    attrs = getAttributeList(policy)
    s = group.random(ZR)
    sh = calculateSharesDict(s, policy)
    Y = len(sh)
    Ctl = (M * (egg ** s))
    C = (hG2 ** s)
    for y in range(0, Y):
        y1 = attrs[y]
        share[y1] = sh[y1]
        Cr[y1] = (gG2 ** share[y1])
        Cpr[y1] = (group.hash(y1, G1) ** share[y1])
    ct = [policy_str, Ctl, C, Cr, Cpr]
    output = ct
    return output

def decrypt(pk, sk, ct):
    policy_str, Ctl, C, Cr, Cpr = ct
    S, D, Dj, Djp = sk
    policy = createPolicy(policy_str)
    attrs = prune(policy, S)
    coeff = getCoefficients(policy)
    Y = len(attrs)
    A = dotprod2(range(0, Y), lam_func1, attrs, Cr, Dj, Djp, Cpr, coeff)
    result0 = (pair(C, D) / A)
    M = (Ctl / result0)
    output = M
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)
    
    userFuncs2.groupObj = group
    builtInFuncs.util = SecretUtil(group, verbose=False)

    attrs = ['ONE', 'TWO', 'THREE']
    access_policy = '((four or three) and (two or one))'
    print("Attributes =>", attrs); print("Policy =>", access_policy)

    (mk, pk) = setup()

    sk = keygen(pk, mk, attrs)
    print("sk :=>", sk)

    rand_msg = group.random(GT)
    print("msg =>", rand_msg)
    ct = encrypt(pk, rand_msg, access_policy)
    print("\nCiphertext...\n")
    group.debug(ct)

    rec_msg = decrypt(pk, sk, ct)
    print("\nDecrypt...\n")
    print("Rec msg =>", rec_msg)

    assert rand_msg == rec_msg, "FAILED Decryption: message is incorrect"
    print("Successful Decryption!!!")

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()

