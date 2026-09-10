"""Envelope downgrade rejection and independent KDF known-answer coverage."""
import base64

import pytest

from charm.toolbox.abeintegrity import (
    AUTH_FIELD, InvalidCiphertext, _hkdf_sha256,
    require_authenticated_ciphertext, seal_ciphertext, open_ciphertext,
)
from charm.toolbox.pairinggroup import PairingGroup, GT


def test_hkdf_rfc5869_case1_first_block():
    # RFC 5869 Appendix A.1, first 32 octets of the published 42-octet OKM.
    key = _hkdf_sha256(bytes.fromhex('0b' * 22), bytes(range(13)), bytes(range(240, 250)))
    assert key.hex() == '3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf'


@pytest.mark.parametrize('mutation', [
    'missing', 'none', 'version0', 'version2', 'version_bool', 'extra',
    'no_nonce', 'bad_base64', 'short_nonce', 'short_tag', 'nonce_bytes',
])
def test_invalid_envelope_rejected(mutation):
    envelope = {'version': 1, 'nonce': base64.b64encode(b'n' * 12).decode(),
                'payload': base64.b64encode(b't' * 16).decode()}
    ct = {AUTH_FIELD: envelope}
    if mutation == 'missing':
        ct = {}
    elif mutation == 'none':
        ct[AUTH_FIELD] = None
    elif mutation.startswith('version'):
        envelope['version'] = {'version0': 0, 'version2': 2, 'version_bool': True}[mutation]
    elif mutation == 'extra':
        envelope['allow_legacy'] = True
    elif mutation == 'no_nonce':
        del envelope['nonce']
    elif mutation == 'bad_base64':
        envelope['payload'] = '!!!!'
    elif mutation == 'short_nonce':
        envelope['nonce'] = base64.b64encode(b'n' * 11).decode()
    elif mutation == 'short_tag':
        envelope['payload'] = base64.b64encode(b't' * 15).decode()
    elif mutation == 'nonce_bytes':
        envelope['nonce'] = envelope['nonce'].encode()
    with pytest.raises(InvalidCiphertext):
        require_authenticated_ciphertext(ct)


def test_domain_separation_and_wrong_key():
    group = PairingGroup('BN254')
    key, msg = group.random(GT), group.random(GT)
    ct = seal_ciphertext(group, 'test-scheme', key, msg, {'policy': 'A'})
    assert open_ciphertext(group, 'test-scheme', key, ct) == msg
    with pytest.raises(InvalidCiphertext):
        open_ciphertext(group, 'other-scheme', key, ct)
    with pytest.raises(InvalidCiphertext):
        open_ciphertext(group, 'test-scheme', group.random(GT), ct)
