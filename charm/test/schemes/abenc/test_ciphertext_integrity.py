"""All remaining bugs/ attacks must reject, including serialized tampering."""
import base64
from dataclasses import dataclass
import zlib

import pytest

from charm.core.engine.util import objectToBytes, bytesToObject
from charm.toolbox.abeintegrity import AUTH_FIELD, InvalidCiphertext
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc import (
    abenc_bsw07, abenc_lsw08, abenc_waters09, abenc_maabe_rw15,
    abenc_maabe_yj14, abenc_unmcpabe_yahk14, dabe_aw11,
    ac17, bsw07, cgw15, waters11,
)

SCHEMES = ['bsw07', 'lsw08', 'waters09', 'aw11', 'rw15', 'yj14', 'yahk14',
           'ac17', 'bsw07_msp', 'cgw15', 'waters11']


@dataclass
class Case:
    group: object
    encrypt: object
    keygen: object
    decrypt: object
    policy: object
    attrs: list
    share_field: str
    policy_field: str = 'policy'
    kp: bool = False
    domain: str = ''


def make_case(name):
    g = PairingGroup('SS512' if name in ('aw11', 'yj14', 'yahk14') else 'BN254')
    policy = lambda text: text
    attrs = ['1', '2']
    if name in ('ac17', 'bsw07_msp', 'cgw15', 'waters11'):
        constructors = {'ac17': lambda: ac17.AC17CPABE(g, 2),
                        'bsw07_msp': lambda: bsw07.BSW07(g),
                        'cgw15': lambda: cgw15.CGW15CPABE(g, 2, 4),
                        'waters11': lambda: waters11.Waters11(g, 4)}
        scheme = constructors[name]()
        pk, mk = scheme.setup()
        return Case(g, lambda m, p: scheme.encrypt(pk, m, p),
                    lambda a: scheme.keygen(pk, mk, a),
                    lambda ct, key: scheme.decrypt(pk, ct, key),
                    scheme.util.createPolicy, attrs, 'C')
    if name in ('bsw07', 'waters09', 'yahk14'):
        constructors = {'bsw07': abenc_bsw07.CPabe_BSW07,
                        'waters09': abenc_waters09.CPabe09,
                        'yahk14': abenc_unmcpabe_yahk14.CPABE_YAHK14}
        scheme = constructors[name](g)
        first, second = scheme.setup()
        pk, mk = (second, first) if name == 'waters09' else (first, second)
        return Case(g, lambda m, p: scheme.encrypt(pk, m, p),
                    lambda a: scheme.keygen(pk, mk, a),
                    lambda ct, key: scheme.decrypt(pk, key, ct), policy, attrs,
                    {'bsw07': 'Cyp', 'waters09': 'C', 'yahk14': 'C_1'}[name],
                    'Policy' if name == 'yahk14' else 'policy')
    if name == 'lsw08':
        scheme = abenc_lsw08.KPabe(g)
        pk, mk = scheme.setup()
        return Case(g, lambda m, a: scheme.encrypt(pk, m, a),
                    lambda p: scheme.keygen(pk, mk, p),
                    lambda ct, key: scheme.decrypt(ct, key), policy, attrs, 'E3', kp=True)
    if name == 'aw11':
        scheme = dabe_aw11.Dabe(g)
        gp = scheme.setup()
        sk, pk = scheme.authsetup(gp, attrs)
        def keygen(attributes):
            key = {}
            for attr in attributes:
                scheme.keygen(gp, sk, attr, 'user', key)
            return key
        return Case(g, lambda m, p: scheme.encrypt(gp, pk, m, p), keygen,
                    lambda ct, key: scheme.decrypt(gp, key, ct), policy, attrs, 'C1')
    if name == 'rw15':
        scheme = abenc_maabe_rw15.MaabeRW15(g)
        gp = scheme.setup()
        pk, sk = scheme.authsetup(gp, 'UT')
        attrs = ['1@UT', '2@UT']
        def keygen(attributes):
            return {'GID': 'user', 'keys': scheme.multiple_attributes_keygen(gp, sk, 'user', attributes)}
        return Case(g, lambda m, p: scheme.encrypt(gp, {'UT': pk}, m, p), keygen,
                    lambda ct, key: scheme.decrypt(gp, key, ct), policy, attrs, 'C1')
    if name == 'yj14':
        scheme = abenc_maabe_yj14.MAABE(g)
        gp, _ = scheme.setup()
        authorities = {}
        authority = scheme.setupAuthority(gp, 'authority', attrs, authorities)
        def keygen(attributes):
            private, public = scheme.registerUser(gp)
            key = {'keys': private, 'authoritySecretKeys': {}}
            for attr in attributes:
                scheme.keygen(gp, authority, attr, public, key['authoritySecretKeys'])
            return key
        return Case(g, lambda m, p: scheme.encrypt(gp, p, m, authority), keygen,
                    lambda ct, key: scheme.decrypt(gp, ct, key), policy, attrs, 'D')
    raise AssertionError(name)


@pytest.fixture(params=SCHEMES)
def case(request):
    result = make_case(request.param)
    result.domain = {
        'bsw07': 'BSW07-SecretUtil', 'lsw08': 'LSW08', 'waters09': 'Waters09',
        'aw11': 'AW11', 'rw15': 'RW15', 'yj14': 'YJ14-MAABE', 'yahk14': 'YAHK14',
        'ac17': 'AC17', 'bsw07_msp': 'BSW07-MSP', 'cgw15': 'CGW15', 'waters11': 'Waters11',
    }[request.param]
    return result


def valid_inputs(case, message=None, operator='and'):
    if message is None:
        message = case.group.random(GT)
    policy = f' {operator} '.join(case.attrs)
    ct = case.encrypt(message, case.attrs if case.kp else policy)
    key = case.keygen(policy if case.kp else case.attrs)
    return message, ct, key


def test_reported_policy_swap_rejected(case):
    msg = case.group.random(GT)
    original = ' and '.join(case.attrs)
    if case.kp:
        key = case.keygen(original)
        ct = case.encrypt(msg, case.attrs[:1])
        assert case.decrypt(ct, key) is False
        key['policy'] = ' or '.join(case.attrs)
    else:
        ct = case.encrypt(msg, original)
        key = case.keygen(case.attrs[:1])
        # Preserve each scheme's ordinary unsatisfied-policy API.
        try:
            denied = case.decrypt(ct, key)
        except Exception as exc:
            assert str(exc) in ("Don't have the required attributes for decryption!",
                                "You don't have the required attributes for decryption!")
        else:
            assert denied is False or denied is None
        ct[case.policy_field] = case.policy(' or '.join(case.attrs))
    with pytest.raises(InvalidCiphertext):
        case.decrypt(ct, key)


def test_serialized_roundtrip(case):
    msg, ct, key = valid_inputs(case)
    restored_ct = bytesToObject(objectToBytes(ct, case.group), case.group)
    restored_key = bytesToObject(objectToBytes(key, case.group), case.group)
    assert case.decrypt(restored_ct, restored_key) == msg
    # Canonical authentication context must not depend on dictionary order.
    assert case.decrypt(dict(reversed(list(restored_ct.items()))), restored_key) == msg


def test_missing_authentication_rejected(case):
    _, ct, key = valid_inputs(case)
    del ct[AUTH_FIELD]
    with pytest.raises(InvalidCiphertext):
        case.decrypt(ct, key)


@pytest.mark.parametrize('field', ['nonce', 'payload'])
def test_modified_authentication_rejected(case, field):
    _, ct, key = valid_inputs(case)
    data = bytearray(base64.b64decode(ct[AUTH_FIELD][field]))
    data[-1] ^= 1
    ct[AUTH_FIELD][field] = base64.b64encode(data).decode('ascii')
    with pytest.raises(InvalidCiphertext):
        case.decrypt(ct, key)


def test_transplanted_payload_rejected(case):
    msg, ct, key = valid_inputs(case)
    _, other, _ = valid_inputs(case, message=msg)
    ct[AUTH_FIELD] = other[AUTH_FIELD]
    with pytest.raises(InvalidCiphertext):
        case.decrypt(ct, key)


def test_unused_share_tampering_rejected(case):
    msg = case.group.random(GT)
    policy = ' or '.join(case.attrs)
    ct = case.encrypt(msg, case.attrs if case.kp else policy)
    key = case.keygen(case.attrs[0] if case.kp else case.attrs[:1])
    assert case.decrypt(ct, key) == msg
    # Delete no labels and leave the selected branch alone: the full context
    # must catch this even though reconstruction still recovers the right key.
    field = ct[case.share_field]
    first, second = case.attrs
    assert field[second] != field[first]
    field[second] = field[first]
    with pytest.raises(InvalidCiphertext):
        case.decrypt(ct, key)


def test_known_identity_plaintext_still_authenticated(case):
    msg, ct, key = valid_inputs(case, message=case.group.init(GT, 1))
    assert case.decrypt(ct, key) == msg
    # An attacker who knows the plaintext cannot use it as the payload key.
    from charm.toolbox.abeintegrity import seal_ciphertext
    forged = {k: v for k, v in ct.items() if k != AUTH_FIELD}
    mutable = ('C', 'DS') if case.domain == 'YJ14-MAABE' else ()
    seal_ciphertext(case.group, case.domain, msg, msg, forged, mutable_fields=mutable)
    with pytest.raises(InvalidCiphertext):
        case.decrypt(forged, key)


def test_original_bsw07_serialized_policy_attack():
    case = make_case('bsw07')
    msg = case.group.random(GT)
    ct = case.encrypt(msg, '1 and 2')
    key = case.keygen(['1'])
    data = zlib.decompress(base64.b64decode(objectToBytes(ct, case.group)))
    assert b'"str:1 and 2"' in data
    data = data.replace(b'"str:1 and 2"', b'"str:1 or 2"')
    tampered = bytesToObject(base64.b64encode(zlib.compress(data)), case.group)
    with pytest.raises(InvalidCiphertext):
        case.decrypt(tampered, key)


def test_equivalent_cp_policy_change_is_authenticated():
    case = make_case('bsw07')
    msg, ct, key = valid_inputs(case)
    # Reconstruction is identical, so this specifically verifies AAD binding.
    ct['policy'] = '(' + ct['policy'] + ')'
    with pytest.raises(InvalidCiphertext):
        case.decrypt(ct, key)
