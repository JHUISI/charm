"""End-to-end regressions for duplicate attributes and policy serialization."""
import base64
import zlib
import pytest
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc import ac17, bsw07, cgw15, waters11
from charm.schemes.abenc.abenc_maabe_yj14 import MAABE
from charm.schemes.abenc.abenc_dacmacs_yj14 import DACMACS
from charm.schemes.abenc.abenc_unmcpabe_yahk14 import CPABE_YAHK14
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.adapters.abenc_adapt_hybrid import HybridABEnc


@pytest.mark.parametrize('scheme_type', [MAABE, DACMACS])
@pytest.mark.parametrize('policy', ['(A and B) or (A and B)',
                                    '(TEAM_ROLE and B) or (TEAM_ROLE and B)',
                                    '(A and B) or (A and C)'])
def test_duplicate_attributes_and_revocation(scheme_type, policy):
    group = PairingGroup('SS512')
    scheme = scheme_type(group)
    gp, _ = scheme.setup()
    attribute = 'TEAM_ROLE' if 'TEAM_ROLE' in policy else 'A'
    authorities = {}
    scheme.setupAuthority(gp, 'authority', [attribute, 'B', 'C'], authorities)
    authority = authorities['authority']
    private, public = scheme.registerUser(gp)
    keys = {}
    for name in [attribute, 'B', 'C']:
        scheme.keygen(gp, authority, name, public, keys)
    msg = group.random(GT)
    ct = scheme.encrypt(gp, policy, msg, authority)

    def decrypt():
        if scheme_type is MAABE:
            return scheme.decrypt(gp, ct, {'keys': private, 'authoritySecretKeys': keys})
        token = scheme.generateTK(gp, ct, keys, private[0])
        return scheme.decrypt(ct, token, private[1])

    assert decrypt() == msg
    # Force the second branch to exercise every updated occurrence of A.
    if '(A and C)' in policy:
        del keys['AK']['B']
        assert decrypt() == msg
    update = scheme.ukeygen(gp, authority, attribute, public)
    if scheme_type is MAABE:
        scheme.skupdate(keys, attribute, update['UKs'])
        scheme.ctupdate(gp, ct, attribute, update['UKc'])
    else:
        scheme.skupdate(keys, attribute, update['KUK'])
        scheme.ctupdate(gp, ct, attribute, update['CUK'])
    assert decrypt() == msg


@pytest.mark.parametrize('policy,attrs', [('(1 and 2) or (1 and 3)', ['1', '2']),
                                         ('(!1 and 2) or (!1 and 3)', ['2'])])
def test_yahk14_duplicate_roundtrip(policy, attrs):
    group = PairingGroup('SS512')
    scheme = CPABE_YAHK14(group)
    pp, mk = scheme.setup()
    msg = group.random(GT)
    ct = scheme.encrypt(pp, msg, policy)
    sk = scheme.keygen(pp, mk, attrs)
    assert scheme.decrypt(pp, sk, ct) == msg


@pytest.mark.parametrize('kind', ['ac17', 'bsw07', 'cgw15', 'waters11'])
@pytest.mark.parametrize('policy', ['1 and 2', '(1 and 2) or (1 and 3)'])
def test_policy_tree_ciphertext_serialization(kind, policy):
    group = PairingGroup('BN254')
    factories = {'ac17': lambda: ac17.AC17CPABE(group, 2),
                 'bsw07': lambda: bsw07.BSW07(group),
                 'cgw15': lambda: cgw15.CGW15CPABE(group, 2, 4),
                 'waters11': lambda: waters11.Waters11(group, 4)}
    scheme = factories[kind]()
    pk, mk = scheme.setup()
    msg = group.random(GT)
    key = scheme.keygen(pk, mk, ['1', '2'])
    ct = scheme.encrypt(pk, msg, policy)
    restored = bytesToObject(objectToBytes(ct, group), group)
    assert str(restored['policy']) == str(ct['policy'])
    assert scheme.decrypt(pk, restored, key) == msg
    # Missing shares must be detected even in an unused OR branch.
    del restored['C'][next(reversed(restored['C']))]
    with pytest.raises(ValueError, match='Policy leaves'):
        scheme.decrypt(pk, restored, key)


@pytest.mark.parametrize('over_wire', [False, True])
def test_hybrid_rejects_policy_swapping(over_wire):
    group = PairingGroup('BN254')
    scheme = HybridABEnc(CPabe_BSW07(group), group)
    pk, mk = scheme.setup()
    ct = scheme.encrypt(pk, b'authenticated payload', 'A and B')
    full_key = scheme.keygen(pk, mk, ['A', 'B'])
    assert scheme.decrypt(pk, full_key, bytesToObject(objectToBytes(ct, group), group)) == b'authenticated payload'
    key = scheme.keygen(pk, mk, ['A'])
    if over_wire:
        data = zlib.decompress(base64.b64decode(objectToBytes(ct, group)))
        assert b'"str:A and B"' in data
        data = data.replace(b'"str:A and B"', b'"str:A or B"')
        ct = bytesToObject(base64.b64encode(zlib.compress(data)), group)
    else:
        ct['c1']['policy'] = 'A or B'
    with pytest.raises(ValueError, match='authentication tag'):
        scheme.decrypt(pk, key, ct)
