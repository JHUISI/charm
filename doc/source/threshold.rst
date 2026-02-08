.. _threshold:

Threshold ECDSA
===============

.. module:: charm.schemes.threshold
   :synopsis: Threshold ECDSA signature schemes

Overview
--------

Threshold ECDSA enables *t-of-n* distributed signing, where any *t* parties out of *n*
can collaboratively produce a valid ECDSA signature without any single party ever
holding the complete private key. This is essential for:

- **Cryptocurrency wallets** — Multi-signature security for Bitcoin, Ethereum, XRPL
- **Key management** — Distributed custody without single points of failure
- **Regulatory compliance** — Separation of duties for signing authority

Charm provides three production-ready threshold ECDSA implementations:

- **GG18** — Classic Paillier-based scheme (Gennaro & Goldfeder 2018)
- **CGGMP21** — UC-secure with identifiable aborts (Canetti et al. 2021)
- **DKLS23** — Non-interactive presigning with OT-based MtA (Doerner et al. 2023)

All schemes support **secp256k1** (Bitcoin, XRPL) and other elliptic curves.

Scheme Comparison
-----------------

.. list-table:: Threshold ECDSA Scheme Comparison
   :header-rows: 1
   :widths: 25 25 25 25

   * - Feature
     - GG18
     - CGGMP21
     - DKLS23
   * - **Security Model**
     - ROM (Random Oracle)
     - UC (Composable)
     - ROM (Random Oracle)
   * - **Assumption**
     - DCR + ROM
     - DCR + Strong RSA
     - DDH + ROM
   * - **DKG Rounds**
     - 3
     - 3
     - 3
   * - **Signing Rounds**
     - 4 (interactive)
     - 3 presign + 1 sign
     - 3 presign + 1 sign
   * - **Presigning**
     - ❌ No
     - ✅ Yes
     - ✅ Yes
   * - **Identifiable Aborts**
     - ❌ No
     - ✅ Yes
     - ❌ No
   * - **MtA Protocol**
     - Paillier-based
     - Paillier-based
     - OT-based
   * - **Best For**
     - Simple deployments
     - High security needs
     - Low-latency signing

**When to use each scheme:**

- **GG18**: Simple threshold signing without presigning requirements
- **CGGMP21**: When you need UC security, identifiable aborts, or proactive refresh
- **DKLS23**: When you need fast online signing with pre-computed presignatures

Quick Start
-----------

**GG18 (2-of-3 threshold signing):**

.. code-block:: python

    from charm.toolbox.ecgroup import ECGroup
    from charm.toolbox.eccurve import secp256k1
    from charm.schemes.threshold import GG18

    group = ECGroup(secp256k1)
    gg18 = GG18(group, threshold=2, num_parties=3)

    # Distributed key generation (3 rounds)
    key_shares, public_key = gg18.keygen()

    # Interactive signing with 2 parties (4 rounds)
    message = b"Bitcoin transaction hash"
    signature = gg18.sign(key_shares[:2], message)

    # Standard ECDSA verification
    assert gg18.verify(public_key, message, signature)

**CGGMP21 with presigning:**

.. code-block:: python

    from charm.schemes.threshold import CGGMP21

    cggmp = CGGMP21(group, threshold=2, num_parties=3)
    key_shares, public_key = cggmp.keygen()

    # Presigning (can be done offline, 3 rounds)
    presignatures = cggmp.presign(key_shares[:2])

    # Fast online signing (1 round)
    message = b"XRPL payment transaction"
    signature = cggmp.sign(key_shares[:2], message, presignatures)

    assert cggmp.verify(public_key, message, signature)

**DKLS23 with XRPL integration:**

.. code-block:: python

    from charm.schemes.threshold import DKLS23
    from charm.schemes.threshold.xrpl_wallet import (
        XRPLThresholdWallet, XRPLClient
    )

    dkls = DKLS23(group, threshold=2, num_parties=3)
    key_shares, public_key = dkls.keygen()

    # Create XRPL wallet from threshold public key
    wallet = XRPLThresholdWallet(group, public_key)
    client = XRPLClient(is_testnet=True)

    # See examples/xrpl_memo_demo.py for complete flow

GG18 Protocol Details
---------------------

**Reference:** `Gennaro & Goldfeder 2018 <https://eprint.iacr.org/2019/114.pdf>`_

GG18 is a classic threshold ECDSA scheme using Paillier encryption for the
Multiplicative-to-Additive (MtA) protocol. It provides a straightforward
implementation without presigning.

**Key Features:**

- **Paillier-based MtA**: Secure multiplication using homomorphic encryption
- **Feldman VSS**: Verifiable secret sharing for key distribution
- **Interactive Signing**: 4-round protocol for signature generation

**Protocol Phases:**

1. **Distributed Key Generation (3 rounds)**

   - Round 1: Commit to secret shares
   - Round 2: Reveal commitments, distribute Feldman VSS shares
   - Round 3: Verify shares, compute public key X = g^x

2. **Interactive Signing (4 rounds)**

   - Round 1: Generate k_i, γ_i; broadcast commitments
   - Round 2: MtA for k*γ and k*x products
   - Round 3: Reveal δ_i, compute R = g^{1/k}
   - Round 4: Compute and combine signature shares s_i

**Security:** ROM (Random Oracle Model) with DCR assumption.

CGGMP21 Protocol Details
------------------------

**Reference:** `Canetti et al. 2021 <https://eprint.iacr.org/2021/060>`_

CGGMP21 provides UC-secure threshold ECDSA with identifiable aborts. If a party
misbehaves, the protocol can identify the malicious party with cryptographic proof.

**Key Features:**

- **UC Security**: Composable security in the Universal Composability framework
- **Identifiable Aborts**: Malicious parties are identified with evidence
- **Presigning**: Offline computation for fast online signing
- **Ring-Pedersen Parameters**: Used for ZK proofs (Π^{log}, Π^{aff-g}, Π^{mul})

**Protocol Phases:**

1. **Distributed Key Generation (3 rounds)**
   - Uses Pedersen VSS for verifiable secret sharing
   - Generates Ring-Pedersen parameters for ZK proofs
   - All parties compute consistent public key X = g^x

2. **Presigning (3 rounds, optional)**
   - Round 1: Generate k_i, γ_i; Paillier encrypt k_i
   - Round 2: MtA with ZK proofs for k*γ and k*x
   - Round 3: Compute δ_i, verify proofs, output presignature

3. **Online Signing (1 round)**
   - Use presignature to compute signature share
   - Combine shares for final signature

**Identifiable Aborts:**

.. code-block:: python

    from charm.schemes.threshold.cggmp21_sign import SecurityAbort

    try:
        signature = cggmp.sign(key_shares[:2], message, presigs)
    except SecurityAbort as e:
        print(f"Malicious party: {e.party_id}")
        print(f"Evidence: {e.evidence}")

DKLS23 Protocol Details
-----------------------

**Reference:** `Doerner et al. 2023 <https://eprint.iacr.org/2023/765>`_

DKLS23 uses OT-based (Oblivious Transfer) MtA instead of Paillier encryption,
providing efficient presigning with non-interactive online signing.

**Key Features:**

- **OT-based MtA**: Uses Silent OT for efficient multiplication
- **Non-interactive Presigning**: Presignatures can be computed independently
- **Fast Online Phase**: Single round for signature generation

**Protocol Phases:**

1. **Distributed Key Generation (3 rounds)**
   - Similar to GG18 with Feldman VSS
   - Outputs key shares and public key

2. **Presigning (3 rounds)**
   - Uses OT extension for MtA protocol
   - Generates presignature (R, k-share, χ-share)

3. **Online Signing (1 round)**
   - Compute signature share from presignature
   - Combine for final ECDSA signature

API Reference
-------------

GG18
^^^^

.. py:class:: GG18(group, threshold, num_parties)

   GG18 threshold ECDSA scheme.

   :param group: ECGroup instance (e.g., secp256k1)
   :param threshold: Minimum parties required to sign (t)
   :param num_parties: Total number of parties (n)

   .. py:method:: keygen()

      Perform distributed key generation.

      :returns: Tuple of (key_shares, public_key)

   .. py:method:: sign(key_shares, message)

      Generate threshold signature (interactive, 4 rounds).

      :param key_shares: List of t key shares
      :param message: Message bytes to sign
      :returns: ThresholdSignature object

   .. py:method:: verify(public_key, message, signature)

      Verify ECDSA signature.

      :returns: True if valid, False otherwise

CGGMP21
^^^^^^^

.. py:class:: CGGMP21(group, threshold, num_parties)

   CGGMP21 UC-secure threshold ECDSA with identifiable aborts.

   :param group: ECGroup instance
   :param threshold: Minimum parties required (t)
   :param num_parties: Total parties (n)

   .. py:method:: keygen()

      Perform DKG with Pedersen VSS.

      :returns: Tuple of (key_shares, public_key)

   .. py:method:: presign(key_shares)

      Generate presignatures (offline, 3 rounds).

      :param key_shares: List of t key shares
      :returns: List of presignature objects

   .. py:method:: sign(key_shares, message, presignatures=None)

      Generate signature. Uses presignatures if provided.

      :param key_shares: List of t key shares
      :param message: Message bytes
      :param presignatures: Optional presignatures from presign()
      :returns: ThresholdSignature object
      :raises SecurityAbort: If malicious behavior detected

DKLS23
^^^^^^

.. py:class:: DKLS23(group, threshold, num_parties)

   DKLS23 threshold ECDSA with OT-based MtA.

   :param group: ECGroup instance
   :param threshold: Minimum parties required (t)
   :param num_parties: Total parties (n)

   .. py:method:: keygen()

      Perform distributed key generation.

      :returns: Tuple of (key_shares, public_key)

   .. py:method:: presign(key_shares)

      Generate presignatures using Silent OT.

      :returns: List of presignature objects

   .. py:method:: sign(key_shares, message, presignatures)

      Generate signature from presignatures.

      :returns: ThresholdSignature object

References
----------

- **GG18**: R. Gennaro and S. Goldfeder, "Fast Multiparty Threshold ECDSA with Fast
  Trustless Setup," ACM CCS 2018. `ePrint 2019/114 <https://eprint.iacr.org/2019/114.pdf>`_

- **CGGMP21**: R. Canetti, R. Gennaro, S. Goldfeder, N. Makriyannis, and U. Peled,
  "UC Non-Interactive, Proactive, Threshold ECDSA with Identifiable Aborts,"
  ACM CCS 2020. `ePrint 2021/060 <https://eprint.iacr.org/2021/060>`_

- **DKLS23**: J. Doerner, Y. Kondi, E. Lee, and A. Shelat, "Threshold ECDSA in
  Three Rounds," IEEE S&P 2023. `ePrint 2023/765 <https://eprint.iacr.org/2023/765>`_

See Also
--------

- :doc:`schemes` — All implemented cryptographic schemes
- :doc:`zkp_compiler` — ZKP compiler (used by CGGMP21)
- ``examples/xrpl_memo_demo.py`` — XRPL testnet integration example

