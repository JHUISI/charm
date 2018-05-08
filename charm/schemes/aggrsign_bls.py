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
        if debug: print("Message => '%s'" % M)
        return group.hash(M, G1) ** x

    def verify(self, pk, sig, message):
        M = self.dump(message)
        h = group.hash(M, G1)
        return pair(pk['g'], sig) == pair(h, pk['g^x'])

    def aggregate_sigs(self, signatures):
        return self.product(signatures)

    def verify_aggregate_sig(self, message, aggregate_sig, public_keys):
        g = self.check_and_return_same_generator_in_public_keys(public_keys)
        M = self.dump(message)
        h = group.hash(M, G1)
        combined_pk = self.product([pk['g^x'] for pk in public_keys])
        return pair(g, aggregate_sig) == pair(combined_pk, h)

    def aggregate_sigs_new(self, pubkey_signatures):
        # This method of aggregation is resistant to rogue public key attack
        sigs = []
        for pk, sig in pubkey_signatures:
            p = self.dump(pk['g^x'])
            t = group.hash(p, ZR)
            e = sig ** t
            sigs.append(e)

        return self.product(sigs)

    def verify_aggregate_sig_new(self, message, aggregate_sig, public_keys):
        # This method of aggregation is resistant to rogue public key attack
        g = self.check_and_return_same_generator_in_public_keys(public_keys)
        pks = []
        for pk in public_keys:
            p = self.dump(pk['g^x'])
            t = group.hash(p, ZR)
            pks.append(pk['g^x'] ** t)

        combined_pk = self.product(pks)
        M = self.dump(message)
        h = group.hash(M, G1)
        return pair(g, aggregate_sig) == pair(combined_pk, h)

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


def simple():
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

    aggregate_sig = bls.aggregate_sigs([sig1, sig2, sig3])
    if debug:
        print("Aggregate signature: '%s'" % aggregate_sig)

    assert bls.verify_aggregate_sig(m, aggregate_sig, [pk1, pk2, pk3]), \
        'Failure!!!'

    if debug:
        print('AGGREGATION VERIFICATION SUCCESS!!!')

    assert not bls.verify_aggregate_sig(m, aggregate_sig, [pk1, pk2])

    if debug:
        print('AGGREGATION VERIFICATION SUCCESS AGAIN!!!')


def rogue_public_key_attack():
    # Attack mentioned here https://crypto.stanford.edu/~dabo/pubs/papers/BLSmultisig.html
    groupObj = PairingGroup('MNT224')

    m = {'a': "hello world!!!", 'b': "test message"}
    bls = BLSAggregation(groupObj)
    g = group.random(G2)

    pk1, sk1 = bls.keygen(g)

    # Construct the attacker's public key (pk2) as g^beta * pk1^-1
    pk1_inverse = 1 / pk1['g^x']
    beta = group.random()
    pk2, _ = bls.keygen(g)
    pk2['g^x'] = (g ** beta) * pk1_inverse

    M = BLSAggregation.dump(m)
    h = group.hash(M, G1)
    fake_aggregate_sig = h ** beta
    assert bls.verify_aggregate_sig(m, fake_aggregate_sig, [pk1, pk2]), \
        'Failure!!!'

    if debug:
        print('ROGUE PUBLIC KEY ATTACK SUCCESS!!!')


def new():
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

    aggregate_sig = bls.aggregate_sigs_new([(pk1, sig1), (pk2, sig2),
                                            (pk3, sig3)])
    if debug:
        print("Aggregate signature: '%s'" % aggregate_sig)

    assert bls.verify_aggregate_sig_new(m, aggregate_sig, [pk1, pk2, pk3]), \
        'Failure!!!'

    if debug:
        print('NEW AGGREGATION VERIFICATION SUCCESS!!!')

    assert not bls.verify_aggregate_sig_new(m, aggregate_sig, [pk1, pk2])

    if debug:
        print('NEW AGGREGATION VERIFICATION SUCCESS AGAIN!!!')


def rogue_public_key_defence():
    # Defence mentioned here https://crypto.stanford.edu/~dabo/pubs/papers/BLSmultisig.html
    groupObj = PairingGroup('MNT224')

    m = {'a': "hello world!!!", 'b': "test message"}
    bls = BLSAggregation(groupObj)
    g = group.random(G2)

    pk1, sk1 = bls.keygen(g)

    # Construct the attacker's public key (pk2) as g^beta * pk1^-1
    pk1_inverse = 1 / pk1['g^x']
    beta = group.random()
    pk2, _ = bls.keygen(g)
    pk2['g^x'] = (g ** beta) * pk1_inverse

    M = BLSAggregation.dump(m)
    h = group.hash(M, G1)
    fake_aggregate_sig = h ** beta
    assert not bls.verify_aggregate_sig_new(m, fake_aggregate_sig, [pk1, pk2]), \
        'Failure!!!'

    if debug:
        print('ROGUE PUBLIC KEY ATTACK DEFENDED!!!')


if __name__ == "__main__":
    debug = True
    simple()
    rogue_public_key_attack()
    new()
    rogue_public_key_defence()
