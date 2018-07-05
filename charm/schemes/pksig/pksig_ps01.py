"""
Identity Based Signature
 
| From: "David Pointcheval and Olivier Sanders. Short Randomizable Signatures"
| Published in: 2015
| Available from: https://eprint.iacr.org/2015/525.pdf

* type:           signature (identity-based)
* setting:        bilinear groups (asymmetric)

:Authors:    Lovesh Harchandani
:Date:       6/2018
"""
from functools import reduce

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, pair

debug = False


class PS01:
    """
    Signatures over known messages, section 4 of the paper
    """

    def __init__(self, groupObj):
        global group
        group = groupObj

    @staticmethod
    def keygen(num_messages=1):
        x = group.random(ZR)
        ys = [group.random(ZR) for _ in range(num_messages)]
        sk = {'x': x, 'y': ys}
        g2 = group.random(G2)
        pk = {'X': g2 ** x, 'Y': [g2 ** y for y in ys], 'g2': g2}
        return pk, sk

    def sign(self, sk, *messages):
        h = group.random(G1)
        ms = [group.hash(m, ZR) for m in messages]
        exp = sk['x'] + sum([sk['y'][i] * ms[i] for i in range(len(messages))])
        return h, h ** exp

    def verify(self, pk, sig, *messages):
        s1, s2 = sig
        if group.init(G1) == s1:
            return False
        ms = [group.hash(m, ZR) for m in messages]
        l2 = pk['X'] * self.product([pk['Y'][i] ** ms[i] for i in range(len(messages))])
        return pair(s1, l2) == pair(pk['g2'], s2)

    def randomize_sig(self, sig):
        s1, s2 = sig
        t = group.random(ZR)
        return s1 ** t, s2 ** t

    @staticmethod
    def product(seq):
        return reduce(lambda x, y: x * y, seq)


def main():
    grp = PairingGroup('MNT224')
    ps = PS01(grp)

    print("Signing a single message")

    (pk, sk) = ps.keygen()

    if debug:
        print("Keygen...")
        print("pk :=", pk)
        print("sk :=", sk)

    M = "Please sign this stupid message!"
    sig = ps.sign(sk, M)
    if debug:
        print("Signature: ", sig)

    result = ps.verify(pk, sig, M)
    assert result, "INVALID signature!"
    if debug:
        print("Successful Verification!!!")

    rand_sig = ps.randomize_sig(sig)
    assert sig != rand_sig
    if debug:
        print("Randomized Signature: ", rand_sig)

    result = ps.verify(pk, rand_sig, M)
    assert result, "INVALID signature!"
    if debug:
        print("Successful Verification!!!")

    print("Signing multiple messages")

    messages = ['Hi there', 'Not there', 'Some message ................', 'Dont know .............']
    (pk, sk) = ps.keygen(len(messages))
    if debug:
        print("Keygen...")
        print("pk :=", pk)
        print("sk :=", sk)

    sig = ps.sign(sk, *messages)
    if debug:
        print("Signature: ", sig)

    result = ps.verify(pk, sig, *messages)
    assert result, "INVALID signature!"
    if debug:
        print("Successful Verification!!!")

    rand_sig = ps.randomize_sig(sig)
    assert sig != rand_sig
    if debug:
        print("Randomized Signature: ", rand_sig)

    result = ps.verify(pk, rand_sig, *messages)
    assert result, "INVALID signature!"
    if debug:
        print("Successful Verification!!!")


if __name__ == "__main__":
    debug = True
    main()
