secretshare - Secret Sharing Schemes
=====================================

.. module:: charm.toolbox.secretshare
   :synopsis: Secret sharing implementation using Shamir's scheme

This module provides secret sharing functionality in the Charm cryptographic
library, implementing Shamir's (k,n)-threshold secret sharing scheme.

Overview
--------

Secret sharing allows a secret to be split into multiple shares such that only
a threshold number of shares can reconstruct the secret. With Shamir's (k,n)
scheme, a secret is divided into n shares, and any k shares are sufficient to
recover the secret, while k-1 or fewer shares reveal nothing.

The scheme works by encoding the secret as the constant term of a random
polynomial of degree k-1, then evaluating this polynomial at n distinct points
to generate shares. Lagrange interpolation recovers the polynomial (and thus
the secret) from any k points.

**Core Algorithms:**

- **genShares**: Generate n shares of a secret with threshold k
- **recoverCoefficients**: Compute Lagrange interpolation coefficients
- **recoverSecret**: Reconstruct the secret from k or more shares

**Key Properties:**

- **Perfect Secrecy**: Any k-1 shares reveal absolutely no information about
  the secret (information-theoretically secure)
- **Threshold Access**: Exactly k shares needed - no more, no less
- **Efficient**: Computation is linear in the number of shares

Security Properties
-------------------

Secret sharing provides the following security guarantees:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Security Property
     - Description
   * - **Perfect Secrecy**
     - With fewer than k shares, the secret is information-theoretically
       hidden. All possible secrets are equally likely given k-1 shares.
   * - **Threshold Reconstruction**
     - Any k shares are sufficient to uniquely determine the secret.
       The reconstruction is deterministic and always succeeds.
   * - **Share Independence**
     - Each share reveals nothing about other shares or the secret
       when considered in isolation.
   * - **Verifiability**
     - (With extensions) Participants can verify their shares are consistent
       without revealing them. See Feldman VSS or Pedersen VSS.

Typical Use Cases
-----------------

1. **Distributed Key Management**

   Split a master key across multiple servers or administrators. The key can
   only be recovered when a threshold of parties cooperate, protecting against
   single points of failure or compromise.

   .. code-block:: python

       from charm.toolbox.secretshare import SecretShare
       from charm.toolbox.pairinggroup import PairingGroup, ZR

       group = PairingGroup('SS512')
       ss = SecretShare(group, verbose=False)

       # Split master key into 5 shares, threshold 3
       master_key = group.random(ZR)
       shares = ss.genShares(master_key, k=3, n=5)

       # Distribute shares[1] through shares[5] to different parties
       # shares[0] is the original secret (for verification)

2. **Attribute-Based Encryption**

   ABE schemes use secret sharing internally to implement access policies.
   AND gates use (2,2) sharing, OR gates use (1,2) sharing, and more complex
   policies combine these primitives.

3. **Multiparty Computation**

   Parties secret-share their inputs, perform computation on shares, and
   combine results. This enables computation on private data without
   revealing individual inputs.

Example Usage
-------------

The following example demonstrates Shamir secret sharing:

**Basic Secret Sharing:**

.. code-block:: python

    from charm.toolbox.secretshare import SecretShare
    from charm.toolbox.pairinggroup import PairingGroup, ZR

    # Setup
    group = PairingGroup('SS512')
    ss = SecretShare(group, verbose=False)

    # Define threshold parameters
    k = 3  # Threshold: minimum shares needed
    n = 5  # Total number of shares

    # Create a secret
    secret = group.random(ZR)

    # Generate shares
    shares = ss.genShares(secret, k, n)
    # shares[0] is the secret, shares[1..n] are the actual shares

    # Reconstruct from any k shares (e.g., shares 1, 2, 3)
    subset = {
        group.init(ZR, 1): shares[1],
        group.init(ZR, 2): shares[2],
        group.init(ZR, 3): shares[3]
    }

    recovered = ss.recoverSecret(subset)
    assert secret == recovered, "Secret recovery failed!"

**Using SecretUtil for ABE Policies:**

The :mod:`charm.toolbox.secretutil` module extends secret sharing for
policy-based access control:

.. code-block:: python

    from charm.toolbox.secretutil import SecretUtil
    from charm.toolbox.pairinggroup import PairingGroup, ZR

    group = PairingGroup('SS512')
    util = SecretUtil(group, verbose=False)

    # Create access policy tree
    policy = util.createPolicy("(A and B) or C")

    # Share secret according to policy
    secret = group.random(ZR)
    shares = util.calculateSharesDict(secret, policy)

    # Recover with satisfying attributes
    attributes = ['A', 'B']  # Satisfies (A and B)
    pruned = util.prune(policy, attributes)
    coeffs = util.getCoefficients(policy)

API Reference
-------------

.. automodule:: secretshare
    :show-inheritance:
    :members:
    :undoc-members:

See Also
--------

- :mod:`charm.toolbox.secretutil` - Secret sharing utilities for policy trees
- :mod:`charm.toolbox.msp` - Monotone Span Programs for LSSS
- :mod:`charm.toolbox.ABEnc` - ABE schemes using secret sharing
- :mod:`charm.toolbox.policytree` - Policy tree data structures
