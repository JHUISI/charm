
threshold_sharing - Threshold Secret Sharing
============================================

Overview
--------

The ``threshold_sharing`` module implements threshold secret sharing schemes for
distributed cryptographic protocols. It provides both Shamir secret sharing and
verifiable secret sharing (VSS) variants including Feldman VSS and Pedersen VSS.

This module is a core component of the DKLS23 threshold ECDSA implementation,
enabling secure distribution of private keys among multiple parties where any
t-of-n parties can reconstruct the secret or collaboratively sign messages.

Key Features
------------

* **Shamir Secret Sharing**: Classic (t, n) threshold scheme with Lagrange interpolation
* **Feldman VSS**: Verifiable secret sharing with public commitments for share verification
* **Pedersen VSS**: Information-theoretically hiding VSS with blinding factors
* **Share Arithmetic**: Add shares for distributed operations (DKG, refresh)
* **Proactive Security**: Refresh shares without changing the underlying secret
* **Curve Agnostic**: Works with any DDH-hard elliptic curve group

Security Properties
-------------------

* **Threshold Security**: Fewer than t shares reveal nothing about the secret
* **Verifiability** (Feldman/Pedersen): Parties can verify their shares are valid
* **Information-Theoretic Hiding** (Pedersen): Even unbounded adversaries cannot learn the secret from commitments
* **Computational Binding**: Shares cannot be forged under the DLP assumption

Use Cases
---------

* **DKLS23 DKG**: Distribute key shares during distributed key generation
* **Threshold Wallets**: Split cryptocurrency private keys among custodians
* **Key Escrow**: Securely backup keys with threshold recovery
* **Proactive Security**: Periodically refresh shares to limit exposure window

Example Usage
-------------

**Basic Shamir Sharing:**

.. code-block:: python

    from charm.toolbox.ecgroup import ECGroup, ZR
    from charm.toolbox.eccurve import secp256k1
    from charm.toolbox.threshold_sharing import ThresholdSharing

    group = ECGroup(secp256k1)
    ts = ThresholdSharing(group)

    # Create 2-of-3 threshold shares
    secret = group.random(ZR)
    shares = ts.share(secret, threshold=2, num_parties=3)

    # Reconstruct from any 2 shares
    recovered = ts.reconstruct({1: shares[1], 3: shares[3]}, threshold=2)
    assert secret == recovered

**Feldman VSS (Verifiable):**

.. code-block:: python

    from charm.toolbox.ecgroup import ECGroup, ZR, G
    from charm.toolbox.eccurve import secp256k1
    from charm.toolbox.threshold_sharing import ThresholdSharing

    group = ECGroup(secp256k1)
    ts = ThresholdSharing(group)
    g = group.random(G)  # Generator

    # Create shares with verification commitments
    secret = group.random(ZR)
    shares, commitments = ts.share_with_verification(secret, g, threshold=2, num_parties=3)

    # Each party can verify their share
    for party_id in [1, 2, 3]:
        valid = ts.verify_share(party_id, shares[party_id], commitments, g)
        assert valid  # Share is valid

**Pedersen VSS (Information-Theoretically Hiding):**

.. code-block:: python

    from charm.toolbox.threshold_sharing import PedersenVSS

    group = ECGroup(secp256k1)
    pvss = PedersenVSS(group)
    g, h = group.random(G), group.random(G)

    secret = group.random(ZR)
    shares, blindings, commitments = pvss.share_with_blinding(secret, g, h, threshold=2, num_parties=3)

    # Verify with blinding values
    valid = pvss.verify_pedersen_share(1, shares[1], blindings[1], commitments, g, h)
    assert valid

**Share Refresh (Proactive Security):**

.. code-block:: python

    # Refresh shares without changing the secret
    refreshed_shares = ts.refresh_shares(shares, threshold=2)

    # Original secret is still recoverable
    recovered = ts.reconstruct({1: refreshed_shares[1], 2: refreshed_shares[2]}, threshold=2)
    assert secret == recovered

Mathematical Background
-----------------------

**Shamir's Scheme**: Uses polynomial interpolation where the secret is the constant
term of a random polynomial f(x) of degree t-1. Each share is f(i) for party i.
Lagrange interpolation recovers f(0) = secret from any t points.

**Feldman VSS**: Publishes commitments Cⱼ = g^{aⱼ} for polynomial coefficients.
Share verification checks: g^{share_i} = ∏ Cⱼ^{i^j}

**Pedersen VSS**: Uses two generators g, h with unknown discrete log relation.
Commitments Cⱼ = g^{aⱼ} · h^{bⱼ} hide the coefficients information-theoretically.

Related Modules
---------------

* :doc:`mta` - Uses threshold shares in MtA conversion
* :doc:`mpc_utils` - Pedersen commitment utilities
* :doc:`broadcast` - Broadcast for DKG consistency

API Reference
-------------

.. automodule:: threshold_sharing
    :show-inheritance:
    :members:
    :undoc-members:
