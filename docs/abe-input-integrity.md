# ABE ciphertext integrity and policy validation

The 11 implementations below now use an authenticated GT-message format.
Their `encrypt` and `decrypt` signatures are unchanged, but their ciphertext
format is incompatible with older releases. Decryption never returns a recovered
GT message unless its authentication tag verifies.

| Implementation | Authenticated scheme domain |
| --- | --- |
| `abenc_bsw07.CPabe_BSW07` | BSW07-SecretUtil |
| `bsw07.BSW07` | BSW07-MSP |
| `abenc_lsw08.KPabe` | LSW08 |
| `abenc_waters09.CPabe09` | Waters09 |
| `dabe_aw11.Dabe` | AW11 |
| `abenc_maabe_rw15.MaabeRW15` | RW15 |
| `abenc_maabe_yj14.MAABE` | YJ14-MAABE |
| `abenc_unmcpabe_yahk14.CPABE_YAHK14` | YAHK14 |
| `ac17.AC17CPABE` | AC17 |
| `cgw15.CGW15CPABE` | CGW15 |
| `waters11.Waters11` | Waters11 |

Other ABE implementations have not automatically acquired this protection.
The existing hybrid adapters continue to work with the listed implementations.

## Authenticated payload construction

Each encryption samples a fresh random GT session key. The original ABE
formula encrypts that key, while AES-256-GCM encrypts the serialized application
GT message. HKDF-SHA256 derives the AES key from the serialized session key,
using a fixed protocol salt and a distinct scheme identifier as `info`.
The KDF follows [RFC 5869](https://www.rfc-editor.org/rfc/rfc5869.html);
AES-GCM uses the existing OpenSSL-backed Charm extension with a 12-byte random
nonce and 16-byte authentication tag. See [NIST SP 800-38D](https://doi.org/10.6028/NIST.SP.800-38D)
for the authenticated-encryption primitive.

The ciphertext contains `_abe_auth` with exactly `version`, `nonce`, and
`payload`. Version 1 is mandatory; nonce and authenticated payload are base64
strings. There is no optional authentication flag or legacy fallback.

The associated data covers the format version, scheme domain, and canonical
serialization of the ABE ciphertext, including its policy or attribute list.
Dictionary order does not matter; policy strings are bound exactly, while
`BinNode` policies use their serialized tree representation. The encrypted
payload is not included in associated data because GCM already authenticates it.

Decryption reconstructs the candidate session key, verifies GCM, and only then
deserializes and returns the original GT message. A wrong reconstructed key,
modified policy, altered payload, or transplanted payload raises
`charm.toolbox.abeintegrity.InvalidCiphertext`, a `ValueError` subclass.
Knowing or guessing the application message does not reveal the independent
session key used for authentication.

### Revocation and key-policy boundaries

YJ14 MAABE's proxy update modifies `C` and `DS` without knowing the session key.
These two collections are excluded from associated data to preserve that
operation; its policy and other fields remain authenticated. Changes to these
collections that invalidate reconstruction fail GCM verification. This is not
an assurance that every change to an unused proxy-update share is detectable.
Updated, authorized users still decrypt; a revoked user whose old key produces
a wrong session key now receives `InvalidCiphertext`.

LSW08 has its policy in the user's secret key, not the ciphertext. Its ciphertext
attribute list and shares are authenticated. The reported `and` to `or` key
mutation reconstructs the wrong session key and is rejected by GCM. This does
not authenticate the provenance of a secret key or forbid transformations that
preserve its ability to recover the correct session key; provision secret keys
through a trusted channel.

This is an authenticated-message extension to the original ABE implementations,
not a formal claim that arbitrary CPA-secure ABE schemes have become CCA-secure.
It does not authenticate the sender: anyone with the public parameters can
create a new ciphertext. Applications needing sender identity or replay
protection must provide those separately.

## Compatibility and failure behavior

- Old ciphertexts without `_abe_auth`, stripped envelopes, and unknown versions
  raise `InvalidCiphertext`. Adding an envelope marker cannot upgrade a legacy
  ciphertext; legacy data needs to be recovered in its trusted existing system
  and encrypted again with the updated implementation.
- Upgrade readers before writing the new format. Old readers cannot interpret
  the authenticated application payload correctly.
- Existing public parameters and secret keys remain usable for new ciphertexts.
- Ordinary unsatisfied policies retain each scheme's existing `False`, `None`,
  or exception behavior. YAHK14 now returns `False` instead of the GT identity,
  because the identity could itself be a valid application message.
- Boolean policy/share mismatches still raise `ValueError` before reconstruction.
  TBPRE retains its structural term-count and share-multiplier checks; it is not
  one of the authenticated implementations listed above.

## Parser and serialization fixes

Policies must parse completely. Trailing parentheses, dangling operators, and
operator keywords used as attributes are rejected. Underscores with nonnumeric
suffixes are valid attribute text; a final `_digits` suffix remains reserved
for share indexing.

YJ14 MAABE, DAC-MACS, and YAHK14 distinguish indexed ciphertext leaves from
unindexed user/authority attributes. Revocation updates all matching leaves.
Policy trees serialize with a `policy:` tag and reconstruct through the parser,
without pickle. Serialization itself does not authenticate arbitrary objects.
`@Input` propagates exceptions instead of printing them and returning `None`.

## Validation

The supplied `bugs/*.py` scripts are preserved unchanged and intentionally
assert the old behavior. Their assertions are now expected to fail. Corrected
expectations and positive round trips are covered in the normal suite:

- `charm/test/toolbox/test_policy_regressions.py`
- `charm/test/toolbox/test_abeintegrity.py`
- `charm/test/schemes/abenc/test_policy_roundtrips.py`
- `charm/test/schemes/abenc/test_policy_share_validation.py`
- `charm/test/schemes/abenc/test_ciphertext_integrity.py`

The tests include all 11 reported policy swaps and the serialized BSW07 attack,
serialization of ciphertexts and keys, missing or altered authentication data,
payload transplants, unused-share changes, known identity messages, domain
separation, a published HKDF test vector, and authorized/revoked-user behavior.
Run `python3 -m pytest charm/test/` for the complete suite.
