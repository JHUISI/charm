''' BLS Multi-Signatures

 | From: "Dan Boneh, Manu Drijvers, Gregory Neven. BLS Multi-Signatures With Public-Key Aggregation".
 | Available from: https://crypto.stanford.edu/~dabo/pubs/papers/BLSmultisig.html

 * type:         signature (identity-based)
 * setting:      bilinear groups (asymmetric)

:Authors: Lovesh Harchandani
:Date:    5/2018
'''

from functools import reduce

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, pair
from charm.core.engine.util import objectToBytes

debug = False


class BLSAggregation:
    def __init__(self, groupObj):
        global group
        group = groupObj

    def keygen(self, g, secparam=None):
        x = group.random()
        g_x = g ** x
        pk = {'g^x': g_x, 'g': g, 'identity': str(g_x), 'secparam': secparam}
        sk = {'x': x}
        return pk, sk

    def sign(self, x, message):
        M = self.dump(message)
        if debug:
            print("Message => '%s'" % M)
        return group.hash(M, G1) ** x

    def verify(self, pk, sig, message):
        M = self.dump(message)
        h = group.hash(M, G1)
        return pair(pk['g'], sig) == pair(h, pk['g^x'])

    def aggregate_sigs_vulnerable(self, signatures):
        """
        This method of aggregation is vulnerable to rogue public key attack
        """
        return self.product(signatures)

    def verify_aggregate_sig_vulnerable(self, message, aggregate_sig, public_keys):
        # This method of verification is vulnerable to rogue public key attack
        g = self.check_and_return_same_generator_in_public_keys(public_keys)
        M = self.dump(message)
        h = group.hash(M, G1)
        combined_pk = self.product([pk['g^x'] for pk in public_keys])
        return pair(g, aggregate_sig) == pair(combined_pk, h)

    def aggregate_sigs_safe(self, pubkey_signatures):
        # This method of aggregation is resistant to rogue public key attack
        sigs = []
        all_pubkeys = [i[0] for i in pubkey_signatures]
        for pk, sig in pubkey_signatures:
            e = sig ** self.hash_keys(pk, all_pubkeys)
            sigs.append(e)

        return self.product(sigs)

    def verify_aggregate_sig_safe(self, message, aggregate_sig, public_keys):
        # This method of verification is resistant to rogue public key attack
        g = self.check_and_return_same_generator_in_public_keys(public_keys)
        aggregated_pk = self.aggregate_pub_key(public_keys)
        M = self.dump(message)
        h = group.hash(M, G1)
        return pair(g, aggregate_sig) == pair(aggregated_pk, h)

    @staticmethod
    def product(seq):
        return reduce(lambda x, y: x * y, seq)

    @staticmethod
    def dump(obj):
        return objectToBytes(obj, group)

    @staticmethod
    def check_and_return_same_generator_in_public_keys(public_keys):
        gs = {pk['g'] for pk in public_keys}
        assert len(gs) == 1, 'All public keys should have same generator'
        return next(iter(gs))

    @staticmethod
    def hash_keys(pk, all_pks):
        acc = BLSAggregation.dump(pk['g^x'])
        for p in all_pks:
            acc += BLSAggregation.dump(p['g^x'])
        return group.hash(acc, ZR)

    @staticmethod
    def aggregate_pub_key(pks):
        r = []
        for pk in pks:
            h = BLSAggregation.hash_keys(pk, pks)
            r.append(pk['g^x'] ** h)
        return BLSAggregation.product(r)


def vulnerable():
    groupObj = PairingGroup('MNT224')

    m = {'a': "hello world!!!", 'b': "test message"}
    bls = BLSAggregation(groupObj)
    g = group.random(G2)

    pk1, sk1 = bls.keygen(g)
    pk2, sk2 = bls.keygen(g)
    pk3, sk3 = bls.keygen(g)

    sig1 = bls.sign(sk1['x'], m)
    sig2 = bls.sign(sk2['x'], m)
    sig3 = bls.sign(sk3['x'], m)

    if debug:
        print("Message: '%s'" % m)
        print("Signature1: '%s'" % sig1)
        print("Signature2: '%s'" % sig2)
        print("Signature3: '%s'" % sig3)

    assert bls.verify(pk1, sig1, m), 'Failure!!!'
    assert bls.verify(pk2, sig2, m), 'Failure!!!'
    assert bls.verify(pk3, sig3, m), 'Failure!!!'

    if debug:
        print('VERIFICATION SUCCESS!!!')

    aggregate_sig = bls.aggregate_sigs_vulnerable([sig1, sig2, sig3])
    if debug:
        print("Aggregate signature: '%s'" % aggregate_sig)

    assert bls.verify_aggregate_sig_vulnerable(m, aggregate_sig, [pk1, pk2, pk3]), \
        'Failure!!!'

    if debug:
        print('AGGREGATION VERIFICATION SUCCESS!!!')

    assert not bls.verify_aggregate_sig_vulnerable(m, aggregate_sig, [pk1, pk2])

    if debug:
        print('AGGREGATION VERIFICATION SUCCESS AGAIN!!!')


def demo_rogue_public_key_attack():
    # Attack mentioned here https://crypto.stanford.edu/~dabo/pubs/papers/BLSmultisig.html
    groupObj = PairingGroup('MNT224')

    m = {'a': "hello world!!!", 'b': "test message"}
    bls = BLSAggregation(groupObj)
    g = group.random(G2)

    pk0, sk0 = bls.keygen(g)
    pk1, sk1 = bls.keygen(g)

    # Construct the attacker's public key (pk2) as `g^beta * (pk1*pk2)^-1`,
    # i.e inverse of the product of all public keys that the attacker wants
    # to forge the multi-sig over
    pk_inverse = 1 / (BLSAggregation.product([pk0['g^x'], pk1['g^x']]))
    beta = group.random()
    pk2, _ = bls.keygen(g)
    pk2['g^x'] = (g ** beta) * pk_inverse

    M = BLSAggregation.dump(m)
    h = group.hash(M, G1)
    fake_aggregate_sig = h ** beta
    assert bls.verify_aggregate_sig_vulnerable(m, fake_aggregate_sig, [pk0, pk1, pk2]), \
        'Failure!!!'

    if debug:
        print('ROGUE PUBLIC KEY ATTACK SUCCESS!!!')


def safe():
    groupObj = PairingGroup('MNT224')

    m = {'a': "hello world!!!", 'b': "test message"}
    bls = BLSAggregation(groupObj)
    g = group.random(G2)

    pk1, sk1 = bls.keygen(g)
    pk2, sk2 = bls.keygen(g)
    pk3, sk3 = bls.keygen(g)

    sig1 = bls.sign(sk1['x'], m)
    sig2 = bls.sign(sk2['x'], m)
    sig3 = bls.sign(sk3['x'], m)

    if debug:
        print("Message: '%s'" % m)
        print("Signature1: '%s'" % sig1)
        print("Signature2: '%s'" % sig2)
        print("Signature3: '%s'" % sig3)

    assert bls.verify(pk1, sig1, m), 'Failure!!!'
    assert bls.verify(pk2, sig2, m), 'Failure!!!'
    assert bls.verify(pk3, sig3, m), 'Failure!!!'

    if debug:
        print('VERIFICATION SUCCESS!!!')

    aggregate_sig = bls.aggregate_sigs_safe([(pk1, sig1), (pk2, sig2),
                                             (pk3, sig3)])
    if debug:
        print("Aggregate signature: '%s'" % aggregate_sig)

    assert bls.verify_aggregate_sig_safe(m, aggregate_sig, [pk1, pk2, pk3]), \
        'Failure!!!'

    if debug:
        print('NEW AGGREGATION VERIFICATION SUCCESS!!!')

    assert not bls.verify_aggregate_sig_safe(m, aggregate_sig, [pk1, pk2])

    if debug:
        print('NEW AGGREGATION VERIFICATION SUCCESS AGAIN!!!')


def defend_rogue_public_key_attack():
    # Defence mentioned here https://crypto.stanford.edu/~dabo/pubs/papers/BLSmultisig.html
    groupObj = PairingGroup('MNT224')

    m = {'a': "hello world!!!", 'b': "test message"}
    bls = BLSAggregation(groupObj)
    g = group.random(G2)

    pk0, sk0 = bls.keygen(g)
    pk1, sk1 = bls.keygen(g)

    # Construct the attacker's public key (pk2) as `g^beta * (pk1*pk2)^-1`,
    # i.e inverse of the product of all public keys that the attacker wants
    # to forge the multi-sig over
    pk_inverse = 1 / (BLSAggregation.product([pk0['g^x'], pk1['g^x']]))
    beta = group.random()
    pk2, _ = bls.keygen(g)
    pk2['g^x'] = (g ** beta) * pk_inverse

    M = BLSAggregation.dump(m)
    h = group.hash(M, G1)
    fake_aggregate_sig = h ** beta
    assert not bls.verify_aggregate_sig_safe(m, fake_aggregate_sig, [pk0, pk1, pk2]), \
        'Failure!!!'

    if debug:
        print('ROGUE PUBLIC KEY ATTACK DEFENDED!!!')


if __name__ == "__main__":
    debug = True
    vulnerable()
    demo_rogue_public_key_attack()
    safe()
    defend_rogue_public_key_attack()
