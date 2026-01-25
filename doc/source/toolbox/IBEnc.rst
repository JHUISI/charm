IBEnc - Identity-Based Encryption
==================================

.. module:: charm.toolbox.IBEnc
   :synopsis: Base class for Identity-Based Encryption schemes

This module provides the base class for implementing Identity-Based Encryption (IBE)
schemes in the Charm cryptographic library.

Overview
--------

Identity-Based Encryption allows a sender to encrypt messages using any arbitrary
string (such as an email address, phone number, or username) as the public key,
without requiring prior distribution of public keys or certificates. A trusted
authority called the Private Key Generator (PKG) generates private keys for users
based on their identities.

IBE simplifies key management by eliminating the need for a Public Key Infrastructure
(PKI) with certificates. Anyone can encrypt a message to a recipient using only their
identity string and the system's public parameters.

**How IBE Works:**

1. **Setup**: The PKG generates master public parameters and a master secret key.
2. **Extract**: When a user needs their private key, they authenticate to the PKG,
   which uses the master secret to generate a private key for their identity.
3. **Encrypt**: Anyone can encrypt using the recipient's identity string and public parameters.
4. **Decrypt**: Only the holder of the identity's private key can decrypt.

Security Properties
-------------------

IBE schemes in Charm support the following security definitions:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Security Definition
     - Description
   * - ``IND_ID_CPA``
     - Indistinguishability under adaptive chosen-identity, chosen-plaintext attack.
       The adversary can adaptively choose target identities after seeing public parameters.
   * - ``IND_sID_CPA``
     - Selective-ID security where the adversary commits to the target identity before
       seeing public parameters. Weaker but often more efficient.
   * - ``IND_ID_CCA``
     - Chosen-ciphertext security with adaptive identity selection. Provides
       non-malleability of ciphertexts.
   * - ``IND_sID_CCA``
     - Selective-ID with chosen-ciphertext security.
   * - ``IND_ID_CCA2``
     - Adaptive CCA2 security, the strongest standard notion for IBE.

**Underlying Assumptions:**

Security typically relies on assumptions in bilinear groups such as:

- **BDH** (Bilinear Diffie-Hellman)
- **DBDH** (Decisional BDH)
- **DLIN** (Decisional Linear)

Typical Use Cases
-----------------

1. **Secure Email Without PKI**

   Send encrypted email to anyone using their email address as the public key,
   even if they haven't set up encryption keys yet. The recipient can later
   obtain their private key from the PKG to decrypt.

   .. code-block:: python

       # Sender encrypts to recipient's email
       recipient_id = 'alice@example.com'
       cipher_text = ibe.encrypt(master_public_key, recipient_id, message)

       # Recipient gets private key from PKG (after authentication)
       private_key = ibe.extract(master_secret_key, recipient_id)

       # Recipient decrypts
       plaintext = ibe.decrypt(master_public_key, private_key, cipher_text)

2. **Revocable Encryption**

   Use time-period concatenated with identity for automatic key expiration.
   For example, ``alice@example.com||2024-Q1`` creates keys that are only valid
   for Q1 2024.

3. **Offline Encryption**

   Encrypt to users who may not exist yet or haven't registered with the system.
   The PKG can generate their private key when they eventually join.

Example Schemes
---------------

The following IBE implementations are available in Charm:

**Classic IBE:**

- :mod:`charm.schemes.ibenc.ibenc_bf01` - **IBE_BonehFranklin**: The foundational
  Boneh-Franklin IBE scheme from 2001, the first practical IBE construction.

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup
    from charm.schemes.ibenc.ibenc_bf01 import IBE_BonehFranklin

    group = PairingGroup('MNT224', secparam=1024)
    ibe = IBE_BonehFranklin(group)

    # Setup
    (master_public_key, master_secret_key) = ibe.setup()

    # Extract private key for identity
    ID = 'user@email.com'
    private_key = ibe.extract(master_secret_key, ID)

    # Encrypt to identity
    msg = b"hello world!!!!!"
    cipher_text = ibe.encrypt(master_public_key, ID, msg)

    # Decrypt
    decrypted = ibe.decrypt(master_public_key, private_key, cipher_text)
    assert decrypted == msg

**Advanced IBE Schemes:**

- :mod:`charm.schemes.ibenc.ibenc_waters05` - Waters IBE (2005)
- :mod:`charm.schemes.ibenc.ibenc_waters09` - **DSE09**: Waters Dual System Encryption,
  fully secure IBE under simple assumptions
- :mod:`charm.schemes.ibenc.ibenc_bb03` - Boneh-Boyen IBE
- :mod:`charm.schemes.ibenc.ibenc_lsw08` - Lewko-Sahai-Waters IBE

**Hierarchical IBE:**

- :mod:`charm.schemes.hibenc.hibenc_bb04` - Boneh-Boyen HIBE
- :mod:`charm.schemes.hibenc.hibenc_lew11` - Lewko-Waters HIBE

API Reference
-------------

.. automodule:: IBEnc
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.IBSig` - Identity-Based Signatures
- :mod:`charm.toolbox.PKEnc` - Traditional public-key encryption
- :mod:`charm.toolbox.Hash` - Hash functions used in IBE constructions
