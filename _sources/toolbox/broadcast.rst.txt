
broadcast - Echo Broadcast Protocol
=========================================

Overview
--------

The ``broadcast`` module implements Bracha's reliable broadcast protocol for
Byzantine fault tolerant message delivery in multi-party computation (MPC) protocols.
This is a critical component for ensuring consistency in distributed cryptographic
protocols like DKLS23 threshold ECDSA.

The echo broadcast protocol ensures that if any honest party accepts a message from
a sender, all honest parties accept the same message. This prevents **equivocation attacks**
where a malicious sender attempts to send different messages to different recipients.

Key Features
------------

* **Byzantine Fault Tolerance**: Tolerates up to f = (n-1)/3 Byzantine (malicious) parties
* **Consistency Guarantee**: All honest parties receive identical messages from each sender
* **Equivocation Detection**: Detects and reports when a sender sends conflicting messages
* **Hash-Based Verification**: Uses SHA-256 for efficient message comparison across parties
* **Flexible Message Types**: Supports bytes, dictionaries, and any serializable Python objects

Use Cases
---------

* **Distributed Key Generation (DKG)**: Ensures all parties receive consistent commitments
  during the DKLS23 DKG protocol
* **Threshold Signature Protocols**: Verifies broadcast consistency in presigning rounds
* **Secure Multi-Party Computation**: General-purpose broadcast for any MPC protocol
  requiring agreement on messages

Example Usage
-------------

.. code-block:: python

    from charm.toolbox.broadcast import EchoBroadcast

    # Initialize for 5 parties with default fault tolerance
    broadcast = EchoBroadcast(num_parties=5)

    # Party 1 creates a broadcast message
    msg = broadcast.create_broadcast_message(party_id=1, message={'value': 42})

    # Other parties process echoes and verify consistency
    echo_state = {}
    for verifier_id in [1, 2, 3, 4, 5]:
        echo_state = broadcast.process_echo(
            verifier_id=verifier_id,
            sender_id=1,
            msg_hash=msg['hash'],
            echo_state=echo_state
        )

    # Verify all parties received consistent messages
    is_consistent = broadcast.verify_consistency(echo_state)  # Returns True

Related Modules
---------------

* :doc:`threshold_sharing` - Threshold secret sharing used in DKG
* :doc:`mpc_utils` - Common MPC utility functions
* :doc:`mta` - Multiplicative-to-Additive conversion for threshold ECDSA

API Reference
-------------

.. automodule:: broadcast
    :show-inheritance:
    :members:
    :undoc-members:
