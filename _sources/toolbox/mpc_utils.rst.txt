
mpc_utils - MPC Utility Functions
=========================================

Overview
--------

The ``mpc_utils`` module provides common utility functions for multi-party computation
(MPC) protocols in the Charm cryptographic library. These utilities support byte/integer
conversions, bit decomposition for OT-based protocols, and Pedersen commitments for
hiding values during secure computation.

This module serves as a foundational building block for threshold ECDSA implementations
like DKLS23, providing consistent data handling across all MPC components.

Key Features
------------

* **Byte/Integer Conversion**: Consistent big-endian conversion between integers and bytes
* **Bit Decomposition**: LSB-first bit extraction for oblivious transfer protocols
* **Pedersen Commitments**: Information-theoretically hiding, computationally binding commitments
* **Homomorphic Properties**: Commitments support additive homomorphism for secure aggregation
* **Elliptic Curve Support**: Works with any DDH-hard elliptic curve group

Use Cases
---------

* **Oblivious Transfer**: Bit decomposition enables OT-based MtA conversion
* **Zero-Knowledge Proofs**: Pedersen commitments provide hiding for ZK protocols
* **Secure Aggregation**: Homomorphic commitment addition for distributed protocols
* **Protocol Serialization**: Consistent byte encoding for network transmission

Example Usage
-------------

**Byte/Integer Conversion:**

.. code-block:: python

    from charm.toolbox.mpc_utils import int_to_bytes, bytes_to_int

    # Convert integer to fixed-length bytes (big-endian)
    data = int_to_bytes(256, length=4)  # b'\x00\x00\x01\x00'

    # Convert back to integer
    value = bytes_to_int(data)  # 256

**Bit Decomposition:**

.. code-block:: python

    from charm.toolbox.mpc_utils import bit_decompose, bits_to_int

    # Decompose value into bits (LSB first)
    bits = bit_decompose(value=5, order=2**256, num_bits=4)  # [1, 0, 1, 0]

    # Reconstruct from bits
    reconstructed = bits_to_int(bits, order=2**256)  # 5

**Pedersen Commitments:**

.. code-block:: python

    from charm.toolbox.ecgroup import ECGroup, ZR
    from charm.toolbox.eccurve import secp256k1
    from charm.toolbox.mpc_utils import PedersenCommitment

    group = ECGroup(secp256k1)
    pc = PedersenCommitment(group)
    pc.setup()

    # Commit to a value
    value = group.random(ZR)
    commitment, randomness = pc.commit(value)

    # Verify the commitment opens correctly
    is_valid = pc.open(commitment, value, randomness)  # True

    # Homomorphic addition of commitments
    c1, r1 = pc.commit(group.init(ZR, 10))
    c2, r2 = pc.commit(group.init(ZR, 20))
    c_sum = pc.add(c1, c2)  # Commits to 30

Related Modules
---------------

* :doc:`mta` - Uses bit decomposition for MtA protocol
* :doc:`threshold_sharing` - Uses Pedersen commitments in Pedersen VSS
* :doc:`broadcast` - Broadcast primitives for MPC

API Reference
-------------

.. automodule:: mpc_utils
    :show-inheritance:
    :members:
    :undoc-members:
