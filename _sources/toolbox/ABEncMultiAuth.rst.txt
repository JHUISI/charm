ABEncMultiAuth - Multi-Authority Attribute-Based Encryption
===========================================================

.. module:: charm.toolbox.ABEncMultiAuth
   :synopsis: Base class for Multi-Authority Attribute-Based Encryption schemes

This module provides the base class for implementing Multi-Authority Attribute-Based
Encryption (MA-ABE) schemes in the Charm cryptographic library.

Overview
--------

Multi-Authority ABE extends standard ABE to settings where attributes are managed by
multiple independent authorities rather than a single trusted party. Each authority
independently generates secret keys for attributes under its control, and users can
combine keys from different authorities to satisfy access policies.

This decentralized approach eliminates the single point of failure and trust inherent
in traditional ABE schemes, making it suitable for scenarios where no single entity
should have complete control over all attributes.

**Key Characteristics:**

- **Decentralized Trust**: No single authority has complete control over the system.
  Compromising one authority doesn't compromise the entire system.

- **Independent Authorities**: Each authority manages its own set of attributes and
  can join or leave the system without affecting other authorities.

- **Cross-Domain Attributes**: Users can obtain attribute keys from multiple authorities
  and combine them to satisfy complex access policies spanning multiple domains.

Security Properties
-------------------

MA-ABE schemes provide the following security guarantees:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Security Property
     - Description
   * - **Decentralization**
     - No single authority has complete control; the system remains secure even if
       some authorities are compromised (up to a threshold in some schemes).
   * - **Collusion Resistance**
     - Users from different authorities cannot combine their keys to gain unauthorized
       access. Even if users collude, they can only decrypt if their combined attributes
       legitimately satisfy the access policy.
   * - **IND-CPA Security**
     - Standard confidentiality against chosen-plaintext attacks. Ciphertexts reveal
       nothing about the plaintext to unauthorized users.
   * - **Authority Corruption Resistance**
     - Security holds even if some authorities are compromised, as long as the
       corrupted authorities don't control all attributes needed for decryption.

Typical Use Cases
-----------------

1. **Cross-Organizational Data Sharing**

   Multiple organizations (hospitals, insurance companies, research labs) each manage
   their own attributes but need to share encrypted data. A hospital encrypts patient
   records with a policy like ``(Hospital_A:Doctor AND Insurance_B:Approved) OR Research_C:IRB_Certified``.

   .. code-block:: python

       # Each authority sets up independently
       (auth1_sk, auth1_pk) = dabe.authsetup(gp, ['DOCTOR', 'NURSE'])
       (auth2_sk, auth2_pk) = dabe.authsetup(gp, ['APPROVED', 'PENDING'])

       # User gets keys from multiple authorities
       dabe.keygen(gp, auth1_sk, 'DOCTOR', user_id, user_keys)
       dabe.keygen(gp, auth2_sk, 'APPROVED', user_id, user_keys)

2. **Federated Identity Systems**

   Users authenticate attributes from different identity providers (university,
   employer, government) to access resources. Each provider acts as an independent
   attribute authority.

3. **Smart City Infrastructure**

   Different government departments (transportation, utilities, emergency services)
   manage separate attribute domains for citizen access control to city services
   and data.

Example Schemes
---------------

The following MA-ABE implementations are available in Charm:

**Decentralized ABE:**

- :mod:`charm.schemes.abenc.dabe_aw11` - **Dabe**: The Lewko-Waters Decentralized
  ABE scheme supporting multiple independent authorities.

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup, GT
    from charm.schemes.abenc.dabe_aw11 import Dabe

    group = PairingGroup('SS512')
    dabe = Dabe(group)

    # Global setup (one-time)
    public_parameters = dabe.setup()

    # Authority setup (each authority does this independently)
    auth_attrs = ['ONE', 'TWO', 'THREE', 'FOUR']
    (master_secret_key, master_public_key) = dabe.authsetup(public_parameters, auth_attrs)

    # User key generation
    user_id = "bob"
    secret_keys = {}
    usr_attrs = ['THREE', 'ONE', 'TWO']
    for attr in usr_attrs:
        dabe.keygen(public_parameters, master_secret_key, attr, user_id, secret_keys)

    # Encryption with policy
    msg = group.random(GT)
    policy = '((one or three) and (TWO or FOUR))'
    cipher_text = dabe.encrypt(public_parameters, master_public_key, msg, policy)

    # Decryption
    decrypted_msg = dabe.decrypt(public_parameters, secret_keys, cipher_text)
    assert decrypted_msg == msg

**Other MA-ABE Schemes:**

- :mod:`charm.schemes.abenc.abenc_maabe_rw15` - Rouselakis-Waters MA-ABE
- :mod:`charm.schemes.abenc.abenc_maabe_yj14` - Yang-Jia MA-ABE variant

API Reference
-------------

.. automodule:: ABEncMultiAuth
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.ABEnc` - Single-authority ABE base class
- :mod:`charm.toolbox.ABEnumeric` - Numeric attribute encoding for ABE policies
- :mod:`charm.toolbox.secretutil` - Secret sharing utilities used in ABE constructions
