PKEnc - Public-Key Encryption
==============================

.. module:: charm.toolbox.PKEnc
   :synopsis: Base class for Public-Key Encryption schemes

This module provides the base class for implementing Public-Key Encryption (PKE)
schemes in the Charm cryptographic library.

Overview
--------

Public-Key Encryption (also called asymmetric encryption) uses a pair of
mathematically related keys: a public key for encryption and a private key for
decryption. Anyone can encrypt messages using the public key, but only the holder
of the corresponding private key can decrypt them.

PKE is fundamental to modern cryptography, enabling secure communication between
parties who have never met and don't share a secret key in advance.

**Core Algorithms:**

- **ParamGen**: Generate system parameters (optional, for some schemes)
- **KeyGen**: Generate a public/private key pair
- **Encrypt**: Encrypt a message using the recipient's public key
- **Decrypt**: Decrypt a ciphertext using the private key

**Common Constructions:**

- **RSA**: Based on the hardness of factoring large integers
- **ElGamal**: Based on the Decisional Diffie-Hellman (DDH) assumption
- **Paillier**: Additively homomorphic encryption
- **Cramer-Shoup**: First practical IND-CCA2 secure scheme

Security Properties
-------------------

PKE schemes in Charm support the following security definitions:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Security Definition
     - Description
   * - ``OW_CPA``
     - One-Wayness under Chosen-Plaintext Attack. Hard to recover the entire
       plaintext from a ciphertext.
   * - ``OW_CCA1`` / ``OW_CCA``
     - One-Wayness under Chosen-Ciphertext Attack (non-adaptive/adaptive).
   * - ``IND_CPA``
     - Indistinguishability (semantic security) under CPA. Ciphertexts reveal
       nothing about which of two plaintexts was encrypted.
   * - ``IND_CCA1``
     - IND under non-adaptive CCA (lunchtime attack). Adversary can query
       decryption oracle before seeing the challenge.
   * - ``IND_CCA``
     - IND under adaptive CCA (CCA2). The strongest standard notion. Adversary
       can query decryption oracle even after seeing the challenge.
   * - ``NM_CPA`` / ``NM_CCA``
     - Non-Malleability. Cannot modify ciphertexts to create related plaintexts.
   * - ``KA_CPA`` / ``KA_CCA``
     - Key Anonymity. Ciphertext doesn't reveal which public key was used.

**Relationships:**

- IND-CCA2 ⟹ NM-CCA2 ⟹ IND-CCA1 ⟹ IND-CPA
- IND-CCA2 is equivalent to NM-CCA2

Typical Use Cases
-----------------

1. **Key Exchange (Hybrid Encryption)**

   Encrypt a symmetric session key using PKE, then use the session key for
   efficient bulk data encryption. This combines PKE's key management benefits
   with symmetric encryption's speed.

   .. code-block:: python

       from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction

       # Generate ephemeral symmetric key
       session_key = os.urandom(32)

       # Encrypt session key with recipient's public key
       encrypted_key = pke.encrypt(recipient_pk, session_key)

       # Use session key for bulk encryption
       cipher = AuthenticatedCryptoAbstraction(session_key)
       encrypted_data = cipher.encrypt(large_message)

2. **Secure Messaging**

   End-to-end encryption where only the intended recipient can read messages.
   Used in secure email (PGP/GPG), messaging apps, and file sharing.

3. **Digital Envelopes**

   Securely transmit confidential documents to recipients. The document is
   encrypted with a random key, and the key is encrypted with the recipient's
   public key.

Example Schemes
---------------

The following PKE implementations are available in Charm:

**ElGamal Encryption:**

- :mod:`charm.schemes.pkenc.pkenc_elgamal85` - **ElGamal**: Classic ElGamal
  encryption based on DDH assumption.

.. code-block:: python

    from charm.toolbox.eccurve import prime192v2
    from charm.toolbox.ecgroup import ECGroup
    from charm.schemes.pkenc.pkenc_elgamal85 import ElGamal

    groupObj = ECGroup(prime192v2)
    el = ElGamal(groupObj)

    # Key generation
    (public_key, secret_key) = el.keygen()

    # Encryption
    msg = b"hello world!12345678"
    cipher_text = el.encrypt(public_key, msg)

    # Decryption
    decrypted_msg = el.decrypt(public_key, secret_key, cipher_text)
    assert decrypted_msg == msg

**Other PKE Schemes:**

- :mod:`charm.schemes.pkenc.pkenc_cs98` - **CS98**: Cramer-Shoup, IND-CCA2 secure
- :mod:`charm.schemes.pkenc.pkenc_paillier99` - **Paillier**: Additively homomorphic
- :mod:`charm.schemes.pkenc.pkenc_rsa` - **RSA_Enc**: RSA encryption
- :mod:`charm.schemes.pkenc.pkenc_rabin` - **Rabin_Enc**: Rabin encryption

**Adapters:**

- :mod:`charm.adapters.pkenc_adapt_hybrid` - Hybrid encryption adapter

API Reference
-------------

.. automodule:: PKEnc
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.PKSig` - Public-key signatures
- :mod:`charm.toolbox.IBEnc` - Identity-based encryption
- :mod:`charm.toolbox.symcrypto` - Symmetric encryption for hybrid schemes
- :mod:`charm.toolbox.ecgroup` - Elliptic curve groups for PKE
