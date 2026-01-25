PKSig - Public-Key Signatures
==============================

.. module:: charm.toolbox.PKSig
   :synopsis: Base class for Public-Key Signature schemes

This module provides the base class for implementing Public-Key Signature (digital
signature) schemes in the Charm cryptographic library.

Overview
--------

Public-Key Signatures (digital signatures) allow a signer to generate a signature
on a message using their private key, which anyone can verify using the corresponding
public key. Signatures provide three fundamental security properties:

- **Authentication**: Proof that the message originated from the claimed signer
- **Integrity**: Assurance that the message wasn't modified after signing
- **Non-repudiation**: The signer cannot deny having signed the message

**Core Algorithms:**

- **KeyGen**: Generate a public/private key pair
- **Sign**: Create a signature on a message using the private key
- **Verify**: Check if a signature is valid for a message and public key

**Common Constructions:**

- **RSA Signatures**: Based on the RSA problem
- **DSA/ECDSA**: Based on discrete logarithm in prime/elliptic curve groups
- **Schnorr**: Efficient DL-based signatures, basis for many modern schemes
- **BLS**: Short signatures from bilinear pairings

Security Properties
-------------------

PKSig schemes in Charm support the following security definitions:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Security Definition
     - Description
   * - ``EU_CMA``
     - Existential Unforgeability under Chosen Message Attack. The standard
       security notion. An adversary with access to a signing oracle cannot
       produce a valid signature on any new message.
   * - ``wEU_CMA``
     - Weak existential unforgeability. A relaxed notion that may allow
       re-randomization of existing signatures or other forms of malleability.
   * - ``sEU_CMA``
     - Strong existential unforgeability. Even producing a different valid
       signature on an already-signed message counts as a forgery. Required
       for some applications like preventing signature replay.

**Underlying Assumptions:**

- **DL** (Discrete Logarithm) - Schnorr, DSA
- **RSA** - RSA signatures
- **CDH/DDH** - Various pairing-based signatures
- **Lattice assumptions** - Post-quantum signatures

Typical Use Cases
-----------------

1. **Code Signing**

   Software vendors sign executables and packages to prove authenticity and
   integrity. Users verify signatures before installation to ensure software
   hasn't been tampered with.

   .. code-block:: python

       # Developer signs the software
       software_hash = hash(executable_bytes)
       signature = pksig.sign(public_key, secret_key, software_hash)

       # User verifies before installing
       is_authentic = pksig.verify(vendor_public_key, signature, software_hash)
       if is_authentic:
           install(executable_bytes)

2. **Document Signing**

   Legal contracts, certificates, and official documents with cryptographic
   authentication. Provides legally binding digital signatures in many
   jurisdictions.

3. **Blockchain Transactions**

   Users sign transactions to authorize transfers of digital assets. The
   signature proves ownership of the sending account without revealing
   the private key.

Example Schemes
---------------

The following PKSig implementations are available in Charm:

**Schnorr Signatures:**

- :mod:`charm.schemes.pksig.pksig_schnorr91` - **SchnorrSig**: Classic Schnorr
  signature scheme based on discrete logarithm.

.. code-block:: python

    from charm.core.math.integer import integer
    from charm.schemes.pksig.pksig_schnorr91 import SchnorrSig

    # Setup with safe primes
    p = integer(156816585111264668689583680968857341596876961491501655859473581156994765485015490912709775771877391134974110808285244016265856659644360836326566918061490651852930016078015163968109160397122004869749553669499102243382571334855815358562585736488447912605222780091120196023676916968821094827532746274593222577067)
    q = integer(78408292555632334344791840484428670798438480745750827929736790578497382742507745456354887885938695567487055404142622008132928329822180418163283459030745325926465008039007581984054580198561002434874776834749551121691285667427907679281292868244223956302611390045560098011838458484410547413766373137296611288533)

    pksig = SchnorrSig()
    pksig.params(p, q)

    # Key generation
    (public_key, secret_key) = pksig.keygen()

    # Sign
    msg = "hello world."
    signature = pksig.sign(public_key, secret_key, msg)

    # Verify
    is_valid = pksig.verify(public_key, signature, msg)
    assert is_valid == True

**Other PKSig Schemes:**

- :mod:`charm.schemes.pksig.pksig_dsa` - **DSA**: Digital Signature Algorithm
- :mod:`charm.schemes.pksig.pksig_ecdsa` - **ECDSA**: Elliptic Curve DSA
- :mod:`charm.schemes.pksig.pksig_bls04` - **BLS01**: Short BLS signatures
- :mod:`charm.schemes.pksig.pksig_cl03` - **Sig_CL03**: Camenisch-Lysyanskaya signatures
- :mod:`charm.schemes.pksig.pksig_waters` - **WatersSig**: Waters signatures
- :mod:`charm.schemes.pksig.pksig_rsa_hw09` - RSA-based signatures

**Adapters:**

- :mod:`charm.adapters.pksig_adapt_naor01` - Convert IBE schemes to signatures

API Reference
-------------

.. automodule:: PKSig
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.PKEnc` - Public-key encryption
- :mod:`charm.toolbox.IBSig` - Identity-based signatures
- :mod:`charm.toolbox.integergroup` - Integer groups for DL-based signatures
- :mod:`charm.toolbox.ecgroup` - Elliptic curve groups for ECDSA
