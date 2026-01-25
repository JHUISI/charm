Commit - Commitment Schemes
============================

.. module:: charm.toolbox.Commit
   :synopsis: Base class for Commitment schemes

This module provides the base class for implementing Commitment schemes in the
Charm cryptographic library.

Overview
--------

A commitment scheme allows a party to commit to a chosen value while keeping it
hidden from others, with the ability to reveal the committed value later. The
scheme ensures that once committed, the value cannot be changed (binding), and
the commitment itself reveals nothing about the value (hiding).

Commitment schemes are fundamental building blocks in cryptographic protocols,
particularly in zero-knowledge proofs, secure multiparty computation, and
verifiable secret sharing.

**Core Algorithms:**

- **Setup**: Generate public parameters for the commitment scheme
- **Commit**: Create a commitment to a value, outputting the commitment and
  decommitment (opening) information
- **Decommit**: Verify that a commitment opens to a claimed value using the
  decommitment information

**Types of Commitments:**

- **Perfectly Hiding**: Information-theoretically impossible to determine the
  committed value (e.g., Pedersen commitment)
- **Perfectly Binding**: Information-theoretically impossible to open to a
  different value
- Note: No scheme can be both perfectly hiding and perfectly binding

Security Properties
-------------------

Commitment schemes provide two fundamental security guarantees:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Security Property
     - Description
   * - **Hiding**
     - The commitment reveals nothing about the committed value. Can be
       computational (secure against PPT adversaries) or perfect/statistical
       (information-theoretic).
   * - **Binding**
     - Once committed, the committer cannot open the commitment to a different
       value. Can be computational or perfect/statistical.
   * - **Equivocability**
     - (Optional) With a trapdoor, can open to any value. Useful for
       simulation in zero-knowledge proofs.
   * - **Extractability**
     - (Optional) With a trapdoor, can extract the committed value from any
       valid commitment. Useful for proving soundness.

**Trade-offs:**

- Pedersen: Perfectly hiding, computationally binding (DL assumption)
- Groth-Sahai: Can be configured for either hiding or binding mode

Typical Use Cases
-----------------

1. **Zero-Knowledge Proofs**

   Commit to values in the first round of a sigma protocol, then reveal
   the commitment during verification. The hiding property ensures the
   verifier learns nothing prematurely.

   .. code-block:: python

       # Prover commits to random value r
       (commitment, decommit) = cm.commit(pk, r)

       # Send commitment to verifier, receive challenge c
       # Compute response s = r + c * secret

       # Verifier checks commitment and response
       cm.decommit(pk, commitment, decommit, r)

2. **Coin Flipping Protocols**

   Two parties can fairly generate a random bit: Alice commits to her bit,
   Bob sends his bit, then Alice opens her commitment. The result is the XOR
   of both bits - neither party can bias the outcome.

3. **Sealed-Bid Auctions**

   Bidders commit to their bids before the auction. After all commitments are
   submitted, bids are revealed. This prevents bid manipulation based on
   seeing other bids.

Example Schemes
---------------

The following commitment implementations are available in Charm:

**Pedersen Commitment:**

- :mod:`charm.schemes.commit.commit_pedersen92` - **CM_Ped92**: Classic Pedersen
  commitment, perfectly hiding and computationally binding.

.. code-block:: python

    from charm.toolbox.ecgroup import ECGroup, ZR
    from charm.schemes.commit.commit_pedersen92 import CM_Ped92

    # Setup
    group = ECGroup(410)  # NIST P-256 curve
    cm = CM_Ped92(group)
    pk = cm.setup()

    # Commit to a value
    msg = group.random(ZR)
    (commitment, decommit) = cm.commit(pk, msg)

    # Later: verify the decommitment
    is_valid = cm.decommit(pk, commitment, decommit, msg)
    assert is_valid == True

**Groth-Sahai Commitment:**

- :mod:`charm.schemes.commit.commit_gs08` - **Commitment_GS08**: Groth-Sahai
  commitment in bilinear groups, configurable for binding or hiding mode.

.. code-block:: python

    from charm.toolbox.pairinggroup import PairingGroup, G1
    from charm.schemes.commit.commit_gs08 import Commitment_GS08

    group = PairingGroup('SS512')
    cm = Commitment_GS08(group)

    # Setup in binding mode (default)
    pk = cm.setup(commitType='binding')

    # Commit to group element
    msg = group.random(G1)
    (commitment, decommit) = cm.commit(pk, msg)

    # Verify
    assert cm.decommit(pk, commitment, decommit, msg) == True

API Reference
-------------

.. automodule:: Commit
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.ZKProof` - Zero-knowledge proofs using commitments
- :mod:`charm.toolbox.sigmaprotocol` - Sigma protocols with commitment phase
- :mod:`charm.toolbox.secretshare` - Secret sharing (related primitive)
