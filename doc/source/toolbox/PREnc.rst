PREnc - Proxy Re-Encryption
============================

.. module:: charm.toolbox.PREnc
   :synopsis: Base class for Proxy Re-Encryption schemes

This module provides the base class for implementing Proxy Re-Encryption (PRE)
schemes in the Charm cryptographic library.

Overview
--------

Proxy Re-Encryption allows a semi-trusted proxy to transform ciphertexts encrypted
under one public key into ciphertexts decryptable under a different public key,
**without the proxy learning the underlying plaintext**. The original key holder
(delegator) generates a "re-encryption key" that enables this transformation.

PRE is useful for secure delegation of decryption rights without sharing private
keys or re-encrypting data from scratch.

**Core Algorithms:**

- **Setup**: Generate global system parameters
- **KeyGen**: Generate public/private key pairs for users
- **Encrypt**: Encrypt a message under a user's public key
- **Decrypt**: Decrypt a ciphertext using the corresponding private key
- **ReKeyGen**: Generate a re-encryption key from user A to user B
- **ReEncrypt**: Transform a ciphertext for A into a ciphertext for B

**Types of PRE:**

- **Unidirectional**: Re-encryption keys work in one direction only (A→B doesn't imply B→A)
- **Bidirectional**: Re-encryption works in both directions
- **Single-hop**: Ciphertexts can only be re-encrypted once
- **Multi-hop**: Ciphertexts can be re-encrypted multiple times

Security Properties
-------------------

PRE schemes provide the following security guarantees:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Security Property
     - Description
   * - **Unidirectionality**
     - Re-encryption keys work in one direction only. Having a key to transform
       A's ciphertexts to B doesn't allow transforming B's ciphertexts to A.
   * - **Non-interactivity**
     - The delegator can create re-encryption keys without involving the delegatee.
       User B doesn't need to participate in creating the A→B re-encryption key.
   * - **Proxy Invisibility**
     - Re-encrypted ciphertexts may be indistinguishable from fresh encryptions
       (in some schemes).
   * - **Collusion Resistance**
     - The proxy and delegatee together cannot recover the delegator's secret key.
       Even colluding, they can only decrypt ciphertexts they're authorized for.
   * - **IND-CPA / IND-CCA**
     - Standard confidentiality for both original and re-encrypted ciphertexts.

Typical Use Cases
-----------------

1. **Encrypted Email Forwarding**

   Forward encrypted emails to delegates without decrypting them. Alice can
   authorize a proxy to transform emails encrypted to her into emails Bob can
   decrypt, without the proxy reading the emails.

   .. code-block:: python

       # Alice creates re-encryption key for Bob
       rk_alice_to_bob = pre.rekeygen(params, pk_alice, sk_alice, pk_bob, sk_bob)

       # Proxy transforms ciphertext (without learning plaintext)
       ct_for_bob = pre.re_encrypt(params, rk_alice_to_bob, ct_for_alice)

       # Bob decrypts
       plaintext = pre.decrypt(params, sk_bob, ct_for_bob)

2. **Secure Cloud Storage Delegation**

   Share access to encrypted files stored in the cloud by allowing the cloud
   provider to re-encrypt for authorized users. The cloud never sees plaintext
   but can facilitate sharing.

3. **Key Rotation**

   Transparently update encryption keys by re-encrypting stored data without
   decryption. When rotating keys, generate a re-encryption key from old to
   new key and have the storage system re-encrypt all data.

Example Schemes
---------------

The following PRE implementations are available in Charm:

**AFGH Proxy Re-Encryption:**

- :mod:`charm.schemes.prenc.pre_afgh06` - **AFGH06**: The Ateniese-Fu-Green-Hohenberger
  unidirectional proxy re-encryption scheme.

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
    from charm.schemes.prenc.pre_afgh06 import AFGH06

    groupObj = PairingGroup('SS512')
    pre = AFGH06(groupObj)

    # Setup
    params = pre.setup()

    # Generate keys for Alice and Bob
    (pk_a, sk_a) = pre.keygen(params)
    (pk_b, sk_b) = pre.keygen(params)

    # Alice encrypts a message
    msg = groupObj.random(GT)
    c_a = pre.encrypt(params, pk_a, msg)

    # Alice creates re-encryption key for Bob
    rk = pre.rekeygen(params, pk_a, sk_a, pk_b, sk_b)

    # Proxy re-encrypts (doesn't learn msg)
    c_b = pre.re_encrypt(params, rk, c_a)

    # Bob decrypts
    decrypted = pre.decrypt(params, sk_b, c_b)
    assert msg == decrypted

**Other PRE Schemes:**

- :mod:`charm.schemes.prenc.pre_bbs98` - BBS proxy re-encryption
- :mod:`charm.schemes.prenc.pre_nal16` - NAL16 proxy re-encryption

API Reference
-------------

.. automodule:: PREnc
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.PKEnc` - Standard public-key encryption
- :mod:`charm.toolbox.ABEnc` - Attribute-based encryption (alternative delegation model)
- :mod:`charm.toolbox.pairinggroup` - Pairing groups used in PRE constructions
