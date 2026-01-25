ABEnc - Attribute-Based Encryption
===================================

.. module:: charm.toolbox.ABEnc
   :synopsis: Base class for Attribute-Based Encryption schemes

This module provides the base class for implementing Attribute-Based Encryption (ABE)
schemes in the Charm cryptographic library.

Overview
--------

Attribute-Based Encryption (ABE) is an advanced public-key encryption paradigm where
ciphertexts and keys are associated with sets of attributes or access policies rather
than specific identities. Decryption is only possible when a user's attribute set
satisfies the access structure embedded in either the ciphertext (Ciphertext-Policy ABE)
or the key (Key-Policy ABE).

ABE enables fine-grained access control over encrypted data, allowing data owners to
specify complex access policies without needing to know the specific identities of
authorized users in advance.

**Variants:**

- **Ciphertext-Policy ABE (CP-ABE)**: The access policy is embedded in the ciphertext,
  and user keys are associated with attribute sets. A user can decrypt if their
  attributes satisfy the ciphertext's policy.

- **Key-Policy ABE (KP-ABE)**: The access policy is embedded in the user's key, and
  ciphertexts are associated with attribute sets. A user can decrypt if the ciphertext's
  attributes satisfy their key's policy.

Security Properties
-------------------

ABE schemes in Charm support the following security definitions:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Security Definition
     - Description
   * - ``IND_AB_CPA``
     - Indistinguishability under Chosen-Plaintext Attack for attribute-based settings.
       An adversary cannot distinguish between encryptions of two messages of their choice.
   * - ``IND_AB_CCA``
     - Indistinguishability under Chosen-Ciphertext Attack. Provides security even when
       the adversary can obtain decryptions of ciphertexts other than the challenge.
   * - ``sIND_AB_CPA``
     - Selective security variant where the adversary commits to the challenge
       attributes/policy before seeing public parameters.
   * - ``sIND_AB_CCA``
     - Selective CCA security combining selective-ID with chosen-ciphertext attacks.

**Additional Security Guarantees:**

- **Collusion Resistance**: Multiple users cannot combine their keys to decrypt
  ciphertexts they couldn't individually access. This is a fundamental property
  that distinguishes ABE from simpler broadcast encryption schemes.

- **Attribute Privacy** (in some schemes): The ciphertext does not reveal which
  attributes were used in the access policy.

Typical Use Cases
-----------------

1. **Fine-grained Access Control in Cloud Storage**

   Encrypt files so only users with certain role attributes can decrypt. For example,
   a policy like ``(Manager AND Engineering) OR (Director)`` allows access only to
   engineering managers or any director.

   .. code-block:: python

       policy = '((MANAGER and ENGINEERING) or DIRECTOR)'
       cipher_text = cpabe.encrypt(master_public_key, msg, policy)

2. **Healthcare Record Sharing**

   Allow only authorized medical staff with specific credentials to access patient
   records. Policies can encode requirements like ``Doctor AND (Cardiology OR Emergency)``.

3. **Broadcast Encryption**

   Encrypt content once and allow decryption by any user meeting attribute requirements,
   without needing to know the specific recipients in advance.

Example Schemes
---------------

The following concrete ABE implementations are available in Charm:

**CP-ABE (Ciphertext-Policy ABE):**

- :mod:`charm.schemes.abenc.abenc_bsw07` - **CPabe_BSW07**: The Bethencourt-Sahai-Waters
  scheme from IEEE S&P 2007. Supports arbitrary access policies as Boolean formulas.

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup, GT
    from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07

    group = PairingGroup('SS512')
    cpabe = CPabe_BSW07(group)

    # Setup
    (master_public_key, master_key) = cpabe.setup()

    # Key generation for user with attributes
    attributes = ['ONE', 'TWO', 'THREE']
    secret_key = cpabe.keygen(master_public_key, master_key, attributes)

    # Encryption with access policy
    msg = group.random(GT)
    access_policy = '((four or three) and (three or one))'
    cipher_text = cpabe.encrypt(master_public_key, msg, access_policy)

    # Decryption (succeeds if attributes satisfy policy)
    decrypted_msg = cpabe.decrypt(master_public_key, secret_key, cipher_text)
    assert msg == decrypted_msg

- :mod:`charm.schemes.abenc.abenc_waters09` - **CPabe09**: Waters' CP-ABE scheme from 2009.

**KP-ABE (Key-Policy ABE):**

- :mod:`charm.schemes.abenc.abenc_lsw08` - **KPabe**: The Lewko-Sahai-Waters KP-ABE scheme.

- :mod:`charm.schemes.abenc.abenc_yct14` - **EKPabe**: Extended KP-ABE with additional features.

API Reference
-------------

.. automodule:: ABEnc
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.ABEncMultiAuth` - Multi-Authority ABE for decentralized settings
- :mod:`charm.toolbox.ABEnumeric` - Numeric attribute encoding for ABE policies
- :mod:`charm.toolbox.secretutil` - Secret sharing utilities used in ABE constructions
