'''
Echo Broadcast Protocol Implementation

Implements Bracha's reliable broadcast protocol for Byzantine fault tolerance.
Ensures all honest parties receive the same message from each sender.

| Based on: Bracha's Reliable Broadcast (1987)
| Reference: "Asynchronous Byzantine Agreement Protocols" - Gabriel Bracha
|
| Used in: DKLS23 Threshold ECDSA DKG for broadcast consistency verification

:Authors: Elton de Souza
:Date:    01/2026
'''

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union

PartyId = int

# Module logger
logger = logging.getLogger(__name__)


class EchoBroadcast:
    """
    Echo broadcast protocol for Byzantine fault tolerant message delivery.

    Ensures that if any honest party accepts a message from a sender,
    all honest parties accept the same message (consistency).

    This implements echo broadcast verification as used in distributed
    key generation (DKG) protocols to prevent equivocation attacks where
    a malicious sender sends different messages to different recipients.

    Attributes:
        n: Number of parties in the protocol
        f: Byzantine fault threshold (default: (n-1)//3)

    Example:
        >>> broadcast = EchoBroadcast(num_parties=5)
        >>> msg = broadcast.create_broadcast_message(1, {'value': 42})
        >>> 'sender_id' in msg and 'hash' in msg
        True
    """

    def __init__(self, num_parties: int, fault_threshold: Optional[int] = None):
        """
        Initialize echo broadcast with party count and fault threshold.

        Parameters
        ----------
        num_parties : int
            Total number of parties in the protocol
        fault_threshold : int, optional
            Maximum number of Byzantine (faulty) parties tolerated.
            Defaults to (num_parties - 1) // 3 for optimal Byzantine tolerance.
        """
        if num_parties < 1:
            raise ValueError("num_parties must be at least 1")

        self.n = num_parties
        self.f = fault_threshold if fault_threshold is not None else (num_parties - 1) // 3

        if self.f < 0:
            raise ValueError("fault_threshold must be non-negative")

    def compute_message_hash(self, message: Any) -> bytes:
        """
        Compute hash of a message for echo comparison.

        Parameters
        ----------
        message : Any
            The message to hash. Can be bytes, dict, or any serializable type.

        Returns
        -------
        bytes
            SHA-256 hash of the message
        """
        if isinstance(message, bytes):
            data = message
        elif isinstance(message, dict):
            # Serialize dict to bytes deterministically
            data = json.dumps(message, sort_keys=True, default=str).encode()
        else:
            data = str(message).encode()

        return hashlib.sha256(data).digest()

    def create_broadcast_message(self, party_id: int, message: Any) -> Dict[str, Any]:
        """
        Create a broadcast message with its hash for echo verification.

        Parameters
        ----------
        party_id : int
            The sender's party identifier
        message : Any
            The message content to broadcast

        Returns
        -------
        dict
            Broadcast message containing:
            - sender_id: The sender's party ID
            - message: The original message content
            - hash: SHA-256 hash of the message
        """
        msg_hash = self.compute_message_hash(message)
        return {
            'sender_id': party_id,
            'message': message,
            'hash': msg_hash
        }

    def process_echo(
        self,
        verifier_id: int,
        sender_id: int,
        msg_hash: bytes,
        echo_state: Optional[Dict[int, Dict[int, bytes]]] = None
    ) -> Dict[int, Dict[int, bytes]]:
        """
        Process an echo from another party.

        Records what message hash a verifier claims to have received from a sender.

        Parameters
        ----------
        verifier_id : int
            ID of the party reporting what they received
        sender_id : int
            ID of the original sender
        msg_hash : bytes
            Hash of the message the verifier claims to have received
        echo_state : dict, optional
            Current echo state to update. If None, creates new state.

        Returns
        -------
        dict
            Updated echo state: {verifier_id: {sender_id: msg_hash}}
        """
        if echo_state is None:
            echo_state = {}
        if verifier_id not in echo_state:
            echo_state[verifier_id] = {}
        echo_state[verifier_id][sender_id] = msg_hash
        return echo_state

    def verify_consistency(self, echo_msgs: Dict[int, Dict[int, bytes]]) -> bool:
        """
        Verify all parties received consistent messages from each sender.

        Checks that for each sender, all verifiers report the same message hash.
        If any sender sent different messages to different recipients (equivocation),
        raises ValueError with details about the inconsistency.

        Parameters
        ----------
        echo_msgs : dict
            Echo state mapping {verifier_id: {sender_id: msg_hash}}

        Returns
        -------
        bool
            True if all messages are consistent

        Raises
        ------
        ValueError
            If broadcast inconsistency is detected, with details about which
            sender sent different messages to different recipients

        Example:
            >>> broadcast = EchoBroadcast(num_parties=3)
            >>> # All parties received same hash from sender 1
            >>> echo_msgs = {1: {1: b'hash1'}, 2: {1: b'hash1'}, 3: {1: b'hash1'}}
            >>> broadcast.verify_consistency(echo_msgs)
            True
        """
        if not echo_msgs:
            return True

        # Build a map: sender_id -> {hash -> set of receivers who got that hash}
        sender_to_hashes: Dict[int, Dict[bytes, Set[int]]] = {}

        for verifier_id, received_hashes in echo_msgs.items():
            for sender_id, msg_hash in received_hashes.items():
                if sender_id not in sender_to_hashes:
                    sender_to_hashes[sender_id] = {}

                # Convert hash to bytes if needed
                hash_key = msg_hash if isinstance(msg_hash, bytes) else bytes(msg_hash)

                if hash_key not in sender_to_hashes[sender_id]:
                    sender_to_hashes[sender_id][hash_key] = set()
                sender_to_hashes[sender_id][hash_key].add(verifier_id)

        # Check consistency: each sender should have only one unique hash
        for sender_id, hash_to_receivers in sender_to_hashes.items():
            if len(hash_to_receivers) > 1:
                # Found inconsistency - sender sent different messages
                receivers_by_hash = [
                    f"hash {i+1}: receivers {sorted(receivers)}"
                    for i, (_, receivers) in enumerate(hash_to_receivers.items())
                ]
                raise ValueError(
                    f"Broadcast inconsistency detected: Party {sender_id} sent "
                    f"different messages to different receivers. "
                    f"{'; '.join(receivers_by_hash)}"
                )

        logger.debug("Broadcast consistency verified for %d senders", len(sender_to_hashes))
        return True

