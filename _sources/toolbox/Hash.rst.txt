Hash - Hash Functions
======================

.. module:: charm.toolbox.Hash
   :synopsis: Base class for hash functions and chameleon hashes

This module provides the base class for implementing hash functions in the
Charm cryptographic library, including standard cryptographic hashes and
chameleon (trapdoor) hash functions.

Overview
--------

Hash functions are fundamental cryptographic primitives that map arbitrary-length
inputs to fixed-length outputs. In Charm, hash functions are used extensively
for hashing to group elements, creating challenges in Sigma protocols, and
building more complex cryptographic schemes.

**Types of Hash Functions:**

- **Standard Hash**: One-way function mapping inputs to fixed-length digests
  (SHA-256, SHA-1, etc.)
- **Hash-to-Group**: Maps inputs to elements of cryptographic groups (G1, G2, ZR)
- **Chameleon Hash**: Trapdoor hash where collisions can be found with a secret key

**Core Interface:**

- **paramgen**: Generate hash function parameters (for keyed hashes)
- **hash**: Compute the hash of an input

**Hash-to-Group Functions:**

Charm's pairing groups provide built-in hash-to-group functionality:

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2

    group = PairingGroup('BN254')

    # Hash string to different group elements
    h_zr = group.hash("message", ZR)   # Hash to scalar
    h_g1 = group.hash("message", G1)   # Hash to G1 element
    h_g2 = group.hash("message", G2)   # Hash to G2 element

Security Properties
-------------------

Hash functions in Charm provide the following security properties:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Security Property
     - Description
   * - **Preimage Resistance**
     - Given h(x), computationally infeasible to find x.
   * - **Second Preimage Resistance**
     - Given x, computationally infeasible to find x' ≠ x with h(x) = h(x').
   * - **Collision Resistance**
     - Computationally infeasible to find any x, x' with h(x) = h(x').
   * - **Random Oracle Model**
     - Hash-to-group functions are modeled as random oracles in security proofs.

**Chameleon Hash Properties:**

- **Collision Resistance** (without trapdoor): Standard collision resistance
- **Trapdoor Collisions**: With secret key, can find collisions efficiently
- Used in: Chameleon signatures, sanitizable signatures, redactable blockchains

Typical Use Cases
-----------------

1. **Fiat-Shamir Transform**

   Convert interactive proofs to non-interactive by hashing the transcript
   to generate the challenge:

   .. code-block:: python

       from charm.toolbox.pairinggroup import PairingGroup, ZR, G1

       group = PairingGroup('BN254')

       # In Sigma protocol, compute challenge as hash of commitment
       g = group.random(G1)
       commitment = group.random(G1)  # Prover's commitment
       statement = group.random(G1)   # Public statement

       # Hash commitment and statement to get challenge
       challenge = group.hash((commitment, statement), ZR)

2. **Identity-Based Cryptography**

   Hash identity strings to group elements for IBE/IBS schemes:

   .. code-block:: python

       from charm.toolbox.pairinggroup import PairingGroup, G1

       group = PairingGroup('BN254')

       # Hash identity to group element
       identity = "alice@example.com"
       Q_id = group.hash(identity, G1)

3. **Waters Hash (Standard Model)**

   The Waters hash provides a way to hash in the standard model (without
   random oracles):

   .. code-block:: python

       from charm.toolbox.pairinggroup import PairingGroup
       from charm.toolbox.hash_module import Waters

       group = PairingGroup('SS512')
       waters = Waters(group, length=8, bits=32)

       # Hash identity to vector of group elements
       identity_vector = waters.hash("user@email.com")

Example Schemes
---------------

The following hash-related implementations are available in Charm:

**Chameleon Hash Functions:**

- :mod:`charm.schemes.chamhash_adm05` - **ChamHash_Adm05**: Ateniese-de Medeiros
  chameleon hash based on discrete log
- :mod:`charm.schemes.chamhash_rsa_hw09` - **ChamHash_HW09**: RSA-based
  chameleon hash

.. code-block:: python

    from charm.schemes.chamhash_adm05 import ChamHash_Adm05

    # Safe primes for discrete log setting
    p = 167310082623265876967652539498945156209924585408181852857484498916636831089523896269659556772606682793456669468408268261520215771560029946473055962146621276476194152790472269234259814818903769785028852381312813315223424388631877055814056675290408483235555012310350302524908076372405437952325709925178621721403
    q = 83655041311632938483826269749472578104962292704090926428742249458318415544761948134829778386303341396728334734204134130760107885780014973236527981073310638238097076395236134617129907409451884892514426190656406657611712194315938527907028337645204241617777506155175151262454038186202718976162854962589310860701

    cham_hash = ChamHash_Adm05(p, q)
    (pk, sk) = cham_hash.paramgen()

    # Hash a message
    msg = "Hello world"
    (hash_val, r, s) = cham_hash.hash(pk, msg)

    # Find collision (with secret key)
    new_msg = "Different message"
    (new_hash, new_r, new_s) = cham_hash.find_collision(pk, sk, hash_val, new_msg)
    assert hash_val == new_hash  # Same hash, different message!

**Hash Module Utilities:**

- :mod:`charm.toolbox.hash_module` - **Hash**: General hash utilities
- :mod:`charm.toolbox.hash_module` - **Waters**: Waters hash for standard model

API Reference
-------------

.. automodule:: Hash
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.pairinggroup` - Pairing groups with hash-to-group
- :mod:`charm.toolbox.ecgroup` - EC groups with hash functions
- :mod:`charm.toolbox.hash_module` - Hash utilities and Waters hash
- :mod:`charm.toolbox.sigmaprotocol` - Sigma protocols using hash for Fiat-Shamir
