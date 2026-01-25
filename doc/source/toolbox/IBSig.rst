IBSig - Identity-Based Signatures
==================================

.. module:: charm.toolbox.IBSig
   :synopsis: Base class for Identity-Based Signature schemes

This module provides the base class for implementing Identity-Based Signature (IBS)
schemes in the Charm cryptographic library.

Overview
--------

Identity-Based Signatures are the signing counterpart to Identity-Based Encryption.
A signer's public verification key is derived directly from their identity string
(such as an email address), eliminating the need for certificates linking public
keys to identities.

Anyone can verify a signature using just the signer's identity string and the
system's global public parameters, without needing to look up or verify certificates.

**How IBS Works:**

1. **Setup**: A trusted authority generates master public parameters and master secret key.
2. **KeyGen**: The authority generates a signing key for a user based on their identity.
3. **Sign**: The user signs messages using their identity-based signing key.
4. **Verify**: Anyone can verify using the signer's identity and public parameters.

**Advantages over Traditional Signatures:**

- No certificate management or PKI required
- Verification uses only the signer's identity string
- Simplified key distribution and revocation

Security Properties
-------------------

IBS schemes in Charm support the following security definitions:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Security Definition
     - Description
   * - ``EU_CMA``
     - Existential Unforgeability under Chosen Message Attack. The adversary cannot
       forge a valid signature even after obtaining signatures on messages of their
       choice. This is the standard security notion for signatures.
   * - ``wEU_CMA``
     - Weak existential unforgeability. A relaxed notion that may allow certain
       types of signature malleability.
   * - ``sEU_CMA``
     - Strong existential unforgeability. Even producing a new valid signature on
       a previously signed message counts as a forgery.

**Underlying Assumptions:**

Security typically relies on assumptions in bilinear groups such as:

- **CDH** (Computational Diffie-Hellman)
- **co-CDH** (Computational co-Diffie-Hellman in asymmetric pairings)

Typical Use Cases
-----------------

1. **Email Authentication**

   Sign emails using identity-based keys derived from email addresses. Recipients
   can verify signatures without certificate lookup, using only the sender's
   email address.

   .. code-block:: python

       # Signer gets key from authority
       signer_id = 'alice@company.com'
       signing_key = ibs.keygen(master_secret_key, signer_id)

       # Sign a message
       message = b"Quarterly report attached"
       signature = ibs.sign(public_key, signing_key, message)

       # Anyone can verify using just the identity
       is_valid = ibs.verify(public_key, message, signature)

2. **IoT Device Authentication**

   Lightweight signature scheme where device identity (e.g., serial number or
   MAC address) serves as the public key. Verifiers don't need to store
   device certificates.

3. **Audit Logs**

   Sign audit records where verifiers only need the signer's identity string
   to verify. Useful for distributed systems where certificate distribution
   is impractical.

Example Schemes
---------------

The following IBS implementations are available in Charm:

**BLS-based Signatures:**

- :mod:`charm.schemes.pksig.pksig_bls04` - **BLS01**: The Boneh-Lynn-Shacham short
  signature scheme, which can be viewed as an identity-based signature.

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup
    from charm.schemes.pksig.pksig_bls04 import BLS01

    group = PairingGroup('MNT224')
    ib = BLS01(group)

    # Key generation
    (public_key, secret_key) = ib.keygen()

    # Sign messages
    messages = {'a': "hello world!!!", 'b': "test message"}
    signature = ib.sign(secret_key['x'], messages)

    # Verify
    is_valid = ib.verify(public_key, signature, messages)
    assert is_valid == True

**Other IBS Schemes:**

- :mod:`charm.schemes.pksig.pksig_hess` - Hess identity-based signature
- :mod:`charm.schemes.pksig.pksig_waters05` - Waters IBS (derived from IBE)
- :mod:`charm.schemes.pksig.pksig_waters09` - Waters 2009 IBS

API Reference
-------------

.. automodule:: IBSig
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.IBEnc` - Identity-Based Encryption
- :mod:`charm.toolbox.PKSig` - Traditional public-key signatures
- :mod:`charm.adapters.pksig_adapt_naor01` - Adapter to convert IBE to signatures
