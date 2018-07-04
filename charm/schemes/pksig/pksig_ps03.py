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
    Signatures over committed messages, section 6.1 of the paper
    """

    def __init__(self, groupObj):
        global group
        group = groupObj

    @staticmethod
    def keygen(num_messages=1):
        x = group.random(ZR)
        g1 = group.random(G1)
        sk = {'x': x, 'X1': g1 ** x}
        g2 = group.random(G2)
        ys = [group.random(ZR) for _ in range(num_messages)]
        X2 = g2 ** x
        y1s = [g1 ** y for y in ys]
        y2s = [g2 ** y for y in ys]
        pk = {'X2': X2, 'Y2': y2s, 'Y1': y1s, 'g2': g2, 'g1': g1}
        return pk, sk

    def commitment(self, pk, *messages):
        t = group.random(ZR)
        return t, (pk['g1'] ** t) * self.product([y1 ** group.hash(m, ZR) for (y1, m) in zip(pk['Y1'], messages)])

    def sign(self, sk, pk, commitment):
        u = group.random(ZR)
        return pk['g1'] ** u, (sk['X1'] * commitment) ** u

    @staticmethod
    def unblind_signature(t, sig):
        s1, s2 = sig
        return s1, (s2 / (s1 ** t))

    def verify(self, pk, sig, *messages):
        ms = [group.hash(m, ZR) for m in messages]
        s1, s2 = sig
        if group.init(G1) == s1:
            return False
        l2 = pk['X2'] * self.product([pk['Y2'][i] ** ms[i] for i in range(len(messages))])
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

    messages = ['Hi there', 'Not there', 'Some message ................', 'Dont know .............']
    (pk, sk) = ps.keygen(len(messages))
    if debug:
        print("Keygen...")
        print("pk :=", pk)
        print("sk :=", sk)

    t, commitment = ps.commitment(pk, *messages)

    sig = ps.sign(sk, pk, commitment)
    if debug:
        print("Signature: ", sig)

    sig = ps.unblind_signature(t, sig)

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
