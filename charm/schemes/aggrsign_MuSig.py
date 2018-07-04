''' MuSig: Key Aggregation for Schnorr Signatures

 | From: "Gregory Maxwell and Andrew Poelstra and Yannick Seurin and Pieter Wuille. Simple Schnorr Multi-Signatures with Applications to Bitcoin".
 | Available from: https://eprint.iacr.org/2018/068

 * type:         Aggregate signatures

:Authors: Lovesh Harchandani
:Date:    6/2018
'''

from functools import reduce

from charm.toolbox.eccurve import secp256k1
from charm.toolbox.ecgroup import ZR, G, ECGroup
from charm.core.engine.util import objectToBytes


debug = False


class MuSig:
    def __init__(self, groupObj):
        global group
        group = groupObj

    def keygen(self, g, secparam=None):
        x = group.random()
        g_x = g ** x
        pk = {'g^x': g_x, 'g': g, 'identity': str(g_x), 'secparam': secparam}
        sk = {'x': x}
        return pk, sk

    def sign(self, nonce, sk, pk, challenge, all_pub_keys):
        hash_of_pub_keys = MuSig.hash_pub_keys(all_pub_keys)
        h = group.hash(MuSig.dump(pk['g^x']) + MuSig.dump(hash_of_pub_keys), ZR)
        return nonce + challenge * sk['x'] * h

    def verify(self, pub_keys, sig, message):
        apk = self.aggregated_pub_key(pub_keys)
        R, s = sig
        challenge = self.compute_challenge(apk, R, message)
        g = pub_keys[0]['g']
        return g ** s == R * (apk ** challenge)

    @staticmethod
    def aggregate_sigs(signatures):
        return sum(signatures)

    @staticmethod
    def new_nonce():
        return group.random()

    @staticmethod
    def aggregate_nonce(g, nonces):
        return MuSig.product([g ** n for n in nonces])

    @staticmethod
    def hash_pub_keys(pub_keys):
        acc = b''
        for p in pub_keys:
            acc += MuSig.dump(p['g^x'])
        return group.hash(acc, ZR)

    @staticmethod
    def aggregated_pub_key(pub_keys):
        hash_of_pub_keys = MuSig.hash_pub_keys(pub_keys)
        hash_dump = MuSig.dump(hash_of_pub_keys)
        xs = []
        for pk in pub_keys:
            d = MuSig.dump(pk['g^x']) + hash_dump
            xs.append(pk['g^x'] ** group.hash(d, ZR))
        return MuSig.product(xs)

    @staticmethod
    def compute_challenge(aggregated_pub_key, aggregate_nonce, message):
        m = MuSig.dump(message)
        message_hash = group.hash(m, ZR)
        return group.hash(MuSig.dump(aggregated_pub_key) + MuSig.dump(aggregate_nonce) + MuSig.dump(message_hash))

    @staticmethod
    def product(seq):
        return reduce(lambda x, y: x * y, seq)

    @staticmethod
    def dump(obj):
        return objectToBytes(obj, group)


def main():
    grp = ECGroup(secp256k1)
    ms = MuSig(grp)
    g = grp.random(G)
    if debug:
        print('Generator...', g)

    msg = 'hello there'
    num_signers = 5

    if debug:
        print('{} signers will sign {}'.format(num_signers, msg))

    signers = [ms.keygen(g) for _ in range(num_signers)]

    nonces = [ms.new_nonce() for _ in range(num_signers)]
    an = ms.aggregate_nonce(g, nonces)
    all_pub_keys = [signer[0] for signer in signers]

    if debug:
        print('Public keys...')
        for pk in all_pub_keys:
            print(pk)

    apk = ms.aggregated_pub_key(all_pub_keys)
    if debug:
        print('Aggregated Public key: ', apk)

    challenge = ms.compute_challenge(apk, an, msg)
    sigs = [ms.sign(nonces[i], signers[i][1], signers[i][0], challenge, all_pub_keys) for i in range(num_signers)]

    if debug:
        print('Signatures...')
        for sig in sigs:
            print(sig)

    asig = ms.aggregate_sigs(sigs)

    if debug:
        print('Aggregated signature: ', asig)

    assert ms.verify(all_pub_keys, (an, asig), msg), 'Aggregated sig verification failed'

    if debug:
        print('Verification succeeded')


if __name__ == "__main__":
    debug = True
    main()
