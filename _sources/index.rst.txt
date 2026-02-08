.. Charm-Crypto documentation master file

Charm-Crypto
============

**A framework for rapidly prototyping advanced cryptographic schemes**

.. image:: https://img.shields.io/pypi/v/charm-crypto-framework.svg
   :target: https://pypi.org/project/charm-crypto-framework/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/charm-crypto-framework.svg
   :target: https://pypi.org/project/charm-crypto-framework/
   :alt: Python versions

.. image:: https://img.shields.io/github/license/JHUISI/charm.svg
   :target: https://github.com/JHUISI/charm/blob/dev/LICENSE.txt
   :alt: License

Charm is a Python framework for rapidly prototyping cryptographic schemes and protocols.
It was designed from the ground up to minimize development time and code complexity
while promoting the reuse of components.

**Key Features:**

- **Pairing-based cryptography** — BN254, BLS12-381, MNT curves via PBC library
- **Elliptic curve groups** — NIST curves, secp256k1, Curve25519 via OpenSSL
- **Integer groups** — RSA, DSA, safe primes for classical schemes
- **50+ implemented schemes** — ABE, IBE, signatures, commitments, and more
- **Threshold ECDSA / MPC** — GG18, CGGMP21, DKLS23 for distributed signing (Bitcoin, XRPL)
- **ZKP compiler** — Schnorr proofs, Σ-protocols, AND/OR compositions
- **Serialization** — Convert group elements to bytes for storage/transmission

Quick Start
-----------

Install from PyPI::

    pip install charm-crypto-framework

**BLS Signatures** (used in Ethereum 2.0):

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup, G1
    from charm.schemes.pksig.pksig_bls04 import BLS01

    group = PairingGroup('BN254')
    bls = BLS01(group)

    # Generate keys
    (public_key, secret_key) = bls.keygen()

    # Sign and verify
    message = "Hello, Charm!"
    signature = bls.sign(secret_key['x'], message)
    assert bls.verify(public_key, signature, message)

**Attribute-Based Encryption**:

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup, GT
    from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07

    group = PairingGroup('SS512')
    cpabe = CPabe_BSW07(group)

    # Setup and key generation
    (master_public, master_secret) = cpabe.setup()
    user_key = cpabe.keygen(master_public, master_secret,
                           ['ADMIN', 'DEPARTMENT-A'])

    # Encrypt with policy, decrypt with attributes
    message = group.random(GT)
    policy = '(ADMIN or MANAGER) and DEPARTMENT-A'
    ciphertext = cpabe.encrypt(master_public, message, policy)
    decrypted = cpabe.decrypt(master_public, user_key, ciphertext)

**Threshold ECDSA** (MPC-based signing for Bitcoin/XRPL):

.. code-block:: python

    from charm.toolbox.ecgroup import ECGroup
    from charm.toolbox.eccurve import secp256k1
    from charm.schemes.threshold import GG18, CGGMP21, DKLS23

    group = ECGroup(secp256k1)

    # GG18: Classic threshold ECDSA (2-of-3)
    gg18 = GG18(group, threshold=2, num_parties=3)
    key_shares, public_key = gg18.keygen()
    signature = gg18.sign(key_shares[:2], b"transaction")
    assert gg18.verify(public_key, b"transaction", signature)

    # CGGMP21: UC-secure with identifiable aborts
    cggmp = CGGMP21(group, threshold=2, num_parties=3)
    key_shares, public_key = cggmp.keygen()
    presigs = cggmp.presign(key_shares[:2])  # Offline
    signature = cggmp.sign(key_shares[:2], b"tx", presigs)  # Online

See :doc:`threshold` for detailed documentation and API reference.

Getting Started
---------------

.. toctree::
   :maxdepth: 2

   install_source
   tutorial

User Guide
----------

.. toctree::
   :maxdepth: 1

   cryptographers
   developers

Schemes & API Reference
-----------------------

.. toctree::
   :maxdepth: 1

   schemes
   threshold
   test_vectors
   adapters
   toolbox
   zkp_compiler

Testing
-------

.. toctree::
   :maxdepth: 1

   test_schemes
   test_toolbox

Release Notes
-------------

.. toctree::
   :maxdepth: 2

   release_notes

Links
-----

- **Source Code**: `GitHub <https://github.com/JHUISI/charm>`_
- **Package**: `PyPI <https://pypi.org/project/charm-crypto-framework/>`_
- **Issues**: `Bug Tracker <https://github.com/JHUISI/charm/issues>`_

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

