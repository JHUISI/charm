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

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,pair

debug = False


class PS02:
    """
    Sequential Aggregate signatures over known messages, section 5 of the paper
    """

    def __init__(self, groupObj):
        global group
        group = groupObj

    def setup(self):
        x = group.random(ZR)
        g1 = group.random(G1)
        g2 = group.random(G2)
        self.x = x
        self.g1 = g1
        self.X1 = g1 ** x
        self.g2 = g2
        self.X2 = g2 ** x

    def keygen(self, num_messages):
        ys = [group.random(ZR) for _ in range(num_messages)]
        sk = {'y': ys}
        pk = {'Y': [self.g2 ** y for y in ys]}
        return pk, sk

    def sign(self, sk, pk, messages):
        if not (len(pk['Y']) == len(messages) == len(sk['y'])):
            raise ValueError('Missing or extra messages or keys')
        for m in messages:
            if m == 0:
                raise ValueError('message cant be 0')
        for i in range(len(messages)):
            for j in range(i+1, len(messages)):
                if pk['Y'][i] == pk['Y'][j]:
                    raise ValueError('all public keys should be distinct')

        prev_sig = (self.g1, self.X1)

        for i in range(len(messages)):
            if i > 0 and not self.verify({'Y': pk['Y'][:i]}, prev_sig, messages[:i]):
                raise ValueError('Intermediate verification error')
            t = group.random(ZR)
            s1, s2 = prev_sig
            m = group.hash(messages[i], ZR)
            prev_sig = (s1 ** t, (s2 * (s1 ** (sk['y'][i] * m))) ** t)

        return prev_sig

    def verify(self, pk, sig, messages):
        if len(pk['Y']) != len(messages):
            raise ValueError('Missing or extra messages or keys')
        s1, s2 = sig
        if group.init(G1) == s1:
            return False
        l2 = self.X2 * self.product([pk['Y'][i] ** group.hash(messages[i], ZR) for i in range(len(messages))])
        return pair(s1, l2) == pair(self.g2, s2)

    @staticmethod
    def product(seq):
        return reduce(lambda x, y: x * y, seq)


def main():
    grp = PairingGroup('MNT224')
    ps = PS02(grp)
    ps.setup()

    if debug:
        print("Setup...")
        print("x :=", ps.x)
        print("g1 :=", ps.g1)
        print("X1 :=", ps.X1)
        print("g2 :=", ps.g2)
        print("X2 :=", ps.X2)

    messages = ['Hi there', 'Not there', 'Some message ................', 'Dont know .............']

    (pk, sk) = ps.keygen(len(messages))
    if debug:
        print("Keygen...")
        print("pk :=", pk)
        print("sk :=", sk)

    sig = ps.sign(sk, pk, messages)
    if debug:
        print("Signature: ", sig)

    result = ps.verify(pk, sig, messages)
    assert result, "INVALID signature!"
    if debug:
        print("Successful Verification!!!")


if __name__ == "__main__":
    debug = True
    main()
