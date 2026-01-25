symcrypto - Symmetric Cryptography
===================================

.. module:: charm.toolbox.symcrypto
   :synopsis: Symmetric encryption and authenticated encryption abstractions

This module provides symmetric cryptography abstractions in the Charm cryptographic
library, including authenticated encryption (AEAD) and message authentication.

Overview
--------

Symmetric cryptography uses the same secret key for both encryption and decryption.
This module provides high-level abstractions for symmetric encryption that are
commonly used in hybrid encryption schemes, where an asymmetric scheme encrypts
a session key that is then used for efficient bulk encryption.

**Main Classes:**

- **SymmetricCryptoAbstraction**: Basic symmetric encryption using AES-CBC with
  PKCS7 padding
- **AuthenticatedCryptoAbstraction**: Authenticated encryption providing both
  confidentiality and integrity (AEAD)
- **MessageAuthenticator**: HMAC-based message authentication

**How It Works:**

1. A symmetric key is derived (often from a group element via hashing)
2. Messages are encrypted using AES in CBC mode with random IV
3. For authenticated encryption, an HMAC is computed over the ciphertext
4. The IV and ciphertext are encoded in JSON format for easy serialization

Security Properties
-------------------

The symmetric encryption classes provide the following security guarantees:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Security Property
     - Description
   * - **IND-CPA**
     - Indistinguishability under chosen-plaintext attack. Ciphertexts reveal
       nothing about which plaintext was encrypted (via random IV).
   * - **IND-CCA2**
     - AuthenticatedCryptoAbstraction provides chosen-ciphertext security.
       Adversaries cannot create valid ciphertexts without the key.
   * - **INT-CTXT**
     - Integrity of ciphertexts. Any modification to the ciphertext is detected
       during decryption (for AuthenticatedCryptoAbstraction).
   * - **AEAD**
     - Authenticated Encryption with Associated Data. Supports binding
       additional context data to the ciphertext without encrypting it.

**Underlying Primitives:**

- **AES-128-CBC**: Block cipher in CBC mode with random IV
- **HMAC-SHA256**: Message authentication code for integrity
- **PKCS7**: Padding scheme for block alignment

Typical Use Cases
-----------------

1. **Hybrid Encryption**

   Combine asymmetric encryption (for key transport) with symmetric encryption
   (for data). The asymmetric scheme encrypts a random session key, which is
   used with symcrypto for efficient bulk encryption.

   .. code-block:: python

       from charm.toolbox.pairinggroup import PairingGroup, GT, extract_key
       from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction

       group = PairingGroup('SS512')

       # Session key from group element (e.g., ABE decryption result)
       session_element = group.random(GT)
       sym_key = extract_key(session_element)

       # Encrypt large data with symmetric key
       cipher = AuthenticatedCryptoAbstraction(sym_key)
       ciphertext = cipher.encrypt(b"Large document contents...")

       # Decrypt
       plaintext = cipher.decrypt(ciphertext)

2. **Authenticated Channel**

   After key agreement, use authenticated encryption to protect messages
   against both eavesdropping and tampering.

   .. code-block:: python

       from hashlib import sha256
       from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction

       # Derive key from shared secret
       shared_secret = b"key_from_DH_exchange"
       key = sha256(shared_secret).digest()

       cipher = AuthenticatedCryptoAbstraction(key)

       # Encrypt with associated data (e.g., message counter)
       ad = b"msg_id:12345"
       ct = cipher.encrypt("Secret message", associatedData=ad)

       # Decrypt (must provide same associated data)
       pt = cipher.decrypt(ct, associatedData=ad)

3. **Message Authentication**

   Authenticate messages without encryption when confidentiality is not needed
   but integrity is required.

   .. code-block:: python

       from charm.toolbox.symcrypto import MessageAuthenticator
       from charm.toolbox.pairinggroup import PairingGroup, GT, extract_key

       group = PairingGroup('SS512')
       key = extract_key(group.random(GT))

       mac = MessageAuthenticator(key)
       authenticated_msg = mac.mac("Important announcement")

       # Verify integrity
       is_authentic = mac.verify(authenticated_msg)

Example Usage
-------------

**Basic Authenticated Encryption:**

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup, GT
    from charm.core.math.pairing import hashPair as sha2
    from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction

    # Setup - derive key from group element
    group = PairingGroup('SS512')
    element = group.random(GT)
    key = sha2(element)  # 32-byte key

    # Create cipher
    cipher = AuthenticatedCryptoAbstraction(key)

    # Encrypt
    plaintext = b"Hello, World!"
    ciphertext = cipher.encrypt(plaintext)

    # Decrypt
    recovered = cipher.decrypt(ciphertext)
    assert recovered == plaintext

**With Associated Data (AEAD):**

.. code-block:: python

    from hashlib import sha256
    from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction

    key = sha256(b'secret key').digest()
    cipher = AuthenticatedCryptoAbstraction(key)

    # Associated data is authenticated but not encrypted
    header = b'\\x01\\x02\\x03\\x04'  # e.g., protocol header
    ct = cipher.encrypt('Payload data', associatedData=header)

    # Must provide correct associated data to decrypt
    pt = cipher.decrypt(ct, associatedData=header)

    # Wrong associated data causes verification failure
    try:
        cipher.decrypt(ct, associatedData=b'wrong')
    except ValueError as e:
        print("Tampered or wrong context!")

API Reference
-------------

.. automodule:: symcrypto
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.PKEnc` - Public-key encryption (for hybrid schemes)
- :mod:`charm.toolbox.ABEnc` - Attribute-based encryption using symcrypto
- :mod:`charm.toolbox.paddingschemes` - Padding schemes (PKCS7, OAEP)
- :mod:`charm.toolbox.securerandom` - Secure random number generation
