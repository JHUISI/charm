"""Authenticated GT payloads for the ABE implementations that opt into v1.

ABE encapsulates a fresh random GT key, not the application message. HKDF-SHA256
(RFC 5869) derives an AES-256-GCM key; the original GT message is encrypted with
an authentication tag covering the scheme, format, and encapsulation context.
This extension is not a claim of a generic CPA-to-CCA security transformation.
"""
import base64
import binascii
import hashlib
import hmac
import json
import os

from charm.core.engine.util import serializeObject, to_json
from charm.toolbox.pairinggroup import GT

AUTH_FIELD = '_abe_auth'
_VERSION = 1
_SALT = b'Charm/ABE/GT-payload/HKDF-SHA256/v1'
_ERROR = 'Ciphertext authentication tag is invalid or missing'


class InvalidCiphertext(ValueError):
    """Missing authentication, an unsupported format, or failed authentication."""


def _hkdf_sha256(ikm, salt, info):
    """RFC 5869 Extract + one Expand block (32 bytes for AES-256)."""
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    return hmac.new(prk, info + b'\x01', hashlib.sha256).digest()


def _key(group, secret, scheme):
    return _hkdf_sha256(group.serialize(secret), _SALT, scheme.encode('ascii'))


def _context(group, scheme, ciphertext, mutable_fields):
    # Only explicitly declared proxy-update fields may be omitted. The caller
    # supplies this constant; no ciphertext flag can turn off authentication.
    kem = {k: v for k, v in ciphertext.items()
           if k != AUTH_FIELD and k not in mutable_fields}
    context = {'scheme': scheme, 'version': _VERSION, 'kem': kem}
    return json.dumps(serializeObject(context, group), default=to_json,
                      sort_keys=True, separators=(',', ':')).encode('utf-8')


def require_authenticated_ciphertext(ciphertext):
    """Validate the envelope before policy pruning; never accept a downgrade."""
    try:
        envelope = ciphertext[AUTH_FIELD]
        if (type(envelope) is not dict
                or set(envelope) != {'version', 'nonce', 'payload'}
                or type(envelope['version']) is not int
                or envelope['version'] != _VERSION
                or type(envelope['nonce']) is not str
                or type(envelope['payload']) is not str):
            raise InvalidCiphertext(_ERROR)
        nonce = base64.b64decode(envelope['nonce'], validate=True)
        payload = base64.b64decode(envelope['payload'], validate=True)
        if len(nonce) != 12 or len(payload) < 16:
            raise InvalidCiphertext(_ERROR)
        return nonce, payload
    except (KeyError, TypeError, ValueError, binascii.Error) as exc:
        raise InvalidCiphertext(_ERROR) from exc


def seal_ciphertext(group, scheme, secret, message, ciphertext, mutable_fields=()):
    """Attach the encrypted GT payload to a freshly generated encapsulation."""
    from charm.core.crypto.AES_GCM import encrypt

    if getattr(message, 'type', None) != GT or not group.ismember(message):
        raise TypeError('ABE message must be a GT element in the configured group')
    nonce = os.urandom(12)
    payload = encrypt(_key(group, secret, scheme), group.serialize(message), nonce,
                      aad=_context(group, scheme, ciphertext, mutable_fields))
    ciphertext[AUTH_FIELD] = {
        'version': _VERSION,
        'nonce': base64.b64encode(nonce).decode('ascii'),
        'payload': base64.b64encode(payload).decode('ascii'),
    }
    return ciphertext


def open_ciphertext(group, scheme, secret, ciphertext, mutable_fields=()):
    """Return a GT message only after authentication succeeds."""
    from charm.core.crypto.AES_GCM import decrypt

    nonce, payload = require_authenticated_ciphertext(ciphertext)
    try:
        encoded = decrypt(_key(group, secret, scheme), payload, nonce,
                          aad=_context(group, scheme, ciphertext, mutable_fields))
        message = group.deserialize(encoded)
        if getattr(message, 'type', None) != GT or not group.ismember(message):
            raise InvalidCiphertext(_ERROR)
        return message
    except Exception as exc:
        raise InvalidCiphertext(_ERROR) from exc
