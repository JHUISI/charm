Changes in v0.62
=======================

This release introduces production-ready threshold ECDSA implementations supporting
distributed key generation, presigning, and signing protocols for applications like
cryptocurrency wallets, multi-party custody, and decentralized signing services.

New Threshold ECDSA Schemes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Three complete threshold ECDSA implementations have been added to the ``charm.schemes.threshold`` package:

**GG18 (Gennaro-Goldfeder 2018)**

The GG18 protocol implements threshold ECDSA using Paillier-based multiplicative-to-additive (MtA) conversion:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Description
   * - ``gg18_dkg.py``
     - Distributed Key Generation using Feldman VSS
   * - ``gg18_sign.py``
     - Interactive signing protocol (4 rounds)

*Features:* Paillier-based MtA, DCR assumption security, secp256k1 curve support.

**CGGMP21 (Canetti et al. 2021)**

The CGGMP21 protocol provides UC-secure threshold ECDSA with identifiable aborts:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Description
   * - ``cggmp21_proofs.py``
     - Zero-knowledge proofs (Π-enc, Π-log*, Π-aff-g, etc.)
   * - ``cggmp21_dkg.py``
     - Distributed Key Generation with Ring-Pedersen parameters
   * - ``cggmp21_presign.py``
     - Optional presigning for faster online phase
   * - ``cggmp21_sign.py``
     - Signing with identifiable abort support

*Features:* UC-security, identifiable aborts, optional presigning, Ring-Pedersen ZK proofs.

**DKLS23 (Doerner et al. 2023)**

The DKLS23 protocol uses oblivious transfer for efficient threshold signing:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Description
   * - ``dkls23_dkg.py``
     - Distributed Key Generation
   * - ``dkls23_presign.py``
     - Non-interactive presigning
   * - ``dkls23_sign.py``
     - Fast online signing phase

*Features:* OT-based MtA, non-interactive presigning, fast online signing.

New Toolbox Modules
^^^^^^^^^^^^^^^^^^^

Supporting infrastructure has been added to the ``charm.toolbox`` package:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Description
   * - ``mpc_utils.py``
     - MPC utilities for commitment and broadcast protocols
   * - ``mta.py``
     - Abstract Multiplicative-to-Additive protocol interface
   * - ``paillier_mta.py``
     - Paillier-based MtA implementation for GG18/CGGMP21
   * - ``paillier_zkproofs.py``
     - Zero-knowledge proofs for Paillier encryption
   * - ``threshold_sharing.py``
     - Threshold secret sharing (Feldman VSS, Pedersen VSS)
   * - ``broadcast.py``
     - Broadcast channel implementation for MPC protocols

Documentation Improvements
^^^^^^^^^^^^^^^^^^^^^^^^^^

- Added comprehensive threshold ECDSA guide (``threshold.rst``) with:
  - Protocol comparison table (GG18, CGGMP21, DKLS23)
  - Distributed key generation tutorial
  - Signing examples with code samples
  - Security considerations and best practices
- Updated ``schemes.rst`` with Threshold Signatures section
- Updated ``zkp_compiler.rst`` with CGGMP21 reference
- Enhanced README Features section highlighting all cryptographic capabilities

Example Usage
^^^^^^^^^^^^^

**Threshold Signing with CGGMP21:**

.. code-block:: python

    from charm.schemes.threshold.cggmp21_sign import CGGMP21

    # Initialize with t-of-n threshold (e.g., 2-of-3)
    scheme = CGGMP21(t=2, n=3, curve='secp256k1')

    # Distributed key generation
    dkg_outputs = scheme.dkg(party_ids=['P1', 'P2', 'P3'])

    # Sign a message
    message = b"Hello, threshold ECDSA!"
    signature = scheme.sign(message, dkg_outputs, signing_parties=['P1', 'P2'])

    # Verify signature
    assert scheme.verify(message, signature)

Upgrade Notes
^^^^^^^^^^^^^

This release is fully backward compatible with v0.61. No code changes are required
when upgrading. The new threshold ECDSA modules are optional and can be imported
as needed.

**Installation:**

::

    pip install --upgrade charm-crypto-framework

Contributors
^^^^^^^^^^^^

- **J. Ayo Akinyele** - GG18 and CGGMP21 implementations
- **Elton de Souza** - DKLS23 implementation

Thanks to all contributors for making Charm a comprehensive cryptographic toolkit
supporting both traditional schemes (ABE, IBE, signatures) and modern MPC protocols.

