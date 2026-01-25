"""
OR Composition for Zero-Knowledge Proofs (CDS94).

This module implements the Cramer-Damgård-Schoenmakers (CDS94) technique for
composing zero-knowledge proofs with OR logic.

What OR Composition Proves:
    Proves "I know the discrete log of h1 OR I know the discrete log of h2"
    without revealing WHICH statement the prover actually knows. This is a
    disjunctive proof of knowledge.

The CDS94 Technique:
    The key insight is that for the statement the prover does NOT know, they
    can simulate a valid-looking proof by choosing the challenge and response
    first, then computing a fake commitment. For the known statement, they
    create a real proof.

    1. KNOWN statement (e.g., h1 = g^x, prover knows x):
       - Generate random r, compute u1 = g^r (real commitment)

    2. UNKNOWN statement (e.g., h2, prover doesn't know its DL):
       - Simulate: pick random c2, z2
       - Compute u2 = g^z2 * h2^(-c2) (fake commitment that will verify)

    3. Challenge splitting: c = c1 + c2 (mod q)
       - Compute main challenge: c = H(g, h1, h2, u1, u2)
       - Set c1 = c - c2 (ensures c1 + c2 = c)

    4. Real response: z1 = r + c1*x

    5. Output: (u1, u2, c1, c2, z1, z2)

Security Properties:
    - Witness Indistinguishability: A verifier cannot tell which branch the
      prover actually knows, even with unbounded computational power.
    - Soundness: A prover who knows neither discrete log cannot produce a
      valid proof (except with negligible probability).
    - Zero-Knowledge: The proof reveals nothing beyond the OR statement.

Use Cases:
    - Anonymous Credentials: Prove membership in group A OR group B
    - Voting Systems: Prove vote is for candidate A OR candidate B
    - Deniable Authentication: Prove identity while maintaining deniability
    - Ring Signatures: Prove one of several public keys is yours

Example:
    >>> from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
    >>> group = PairingGroup('SS512')
    >>> g = group.random(G1)
    >>> x = group.random(ZR)
    >>> h1 = g ** x  # Prover knows DL of h1
    >>> h2 = g ** group.random(ZR)  # Prover does NOT know DL of h2
    >>>
    >>> # Prove knowledge of x such that h1 = g^x OR h2 = g^x (without revealing which)
    >>> # Prover knows x for h1
    >>> proof = ORProof.prove_non_interactive(group, g, h1, h2, x, which=0)
    >>> valid = ORProof.verify_non_interactive(group, g, h1, h2, proof)
"""

from typing import Any

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.core.engine.util import objectToBytes, bytesToObject
import logging

logger = logging.getLogger(__name__)


class ORProofData:
    """Container for OR proof data."""

    def __init__(self, commitment1: Any, commitment2: Any, challenge1: Any, challenge2: Any,
                 response1: Any, response2: Any, proof_type: str = 'or') -> None:
        """
        Initialize an OR proof.

        Args:
            commitment1: Commitment for first branch (u1)
            commitment2: Commitment for second branch (u2)
            challenge1: Challenge for first branch (c1)
            challenge2: Challenge for second branch (c2)
            response1: Response for first branch (z1)
            response2: Response for second branch (z2)
            proof_type: Type identifier for the proof
        """
        self.commitment1 = commitment1
        self.commitment2 = commitment2
        self.challenge1 = challenge1
        self.challenge2 = challenge2
        self.response1 = response1
        self.response2 = response2
        self.proof_type = proof_type


class ORProof:
    """
    OR Composition of Schnorr Proofs using CDS94.

    Proves knowledge of discrete log for h1 = g^x OR h2 = g^x without
    revealing which one the prover actually knows.
    """

    @classmethod
    def _compute_challenge_hash(cls, group, g, h1, h2, u1, u2):
        """
        Compute Fiat-Shamir challenge as hash of all public values.

        Args:
            group: The pairing group
            g: Generator
            h1: First public value
            h2: Second public value
            u1: First commitment
            u2: Second commitment

        Returns:
            Challenge c as element of ZR
        """
        data = (objectToBytes(g, group) + objectToBytes(h1, group) +
                objectToBytes(h2, group) + objectToBytes(u1, group) +
                objectToBytes(u2, group))
        return group.hash(data, ZR)

    @classmethod
    def prove_non_interactive(cls, group: PairingGroup, g: Any, h1: Any, h2: Any, x: Any, which: int) -> 'ORProofData':
        """
        Generate non-interactive OR proof using CDS94 technique.

        Proves knowledge of x such that h1 = g^x OR h2 = g^x.

        Args:
            group: The pairing group
            g: The generator element
            h1: First public value
            h2: Second public value
            x: The secret discrete log (for h1 if which=0, for h2 if which=1)
            which: 0 if prover knows x for h1, 1 if prover knows x for h2

        Returns:
            ORProofData object containing commitments, challenges, and responses
        """
        if which not in (0, 1):
            raise ValueError("which must be 0 or 1")

        if which == 0:
            # Prover knows DL of h1, simulates proof for h2
            # Real proof for h1
            r = group.random(ZR)
            u1 = g ** r

            # Simulate proof for h2: pick c2, z2, compute u2
            c2 = group.random(ZR)
            z2 = group.random(ZR)
            # u2 = g^z2 * h2^(-c2) so that g^z2 = u2 * h2^c2
            u2 = (g ** z2) * (h2 ** (-c2))

            # Compute main challenge
            c = cls._compute_challenge_hash(group, g, h1, h2, u1, u2)

            # Split challenge: c1 = c - c2
            c1 = c - c2

            # Real response: z1 = r + c1*x
            z1 = r + c1 * x

        else:  # which == 1
            # Prover knows DL of h2, simulates proof for h1
            # Simulate proof for h1: pick c1, z1, compute u1
            c1 = group.random(ZR)
            z1 = group.random(ZR)
            # u1 = g^z1 * h1^(-c1) so that g^z1 = u1 * h1^c1
            u1 = (g ** z1) * (h1 ** (-c1))

            # Real proof for h2
            r = group.random(ZR)
            u2 = g ** r

            # Compute main challenge
            c = cls._compute_challenge_hash(group, g, h1, h2, u1, u2)

            # Split challenge: c2 = c - c1
            c2 = c - c1

            # Real response: z2 = r + c2*x
            z2 = r + c2 * x

        logger.debug("Generated OR proof (which=%d)", which)
        return ORProofData(
            commitment1=u1, commitment2=u2,
            challenge1=c1, challenge2=c2,
            response1=z1, response2=z2,
            proof_type='or'
        )

    @classmethod
    def verify_non_interactive(cls, group: PairingGroup, g: Any, h1: Any, h2: Any, proof: 'ORProofData') -> bool:
        """
        Verify non-interactive OR proof.

        Verifies that the prover knows the discrete log of h1 OR h2.

        Args:
            group: The pairing group
            g: The generator element
            h1: First public value
            h2: Second public value
            proof: ORProofData object containing commitments, challenges, responses

        Returns:
            True if proof is valid, False otherwise

        Security Notes:
            - Validates proof structure before verification
            - Checks for identity element attacks
            - Recomputes Fiat-Shamir challenge for consistency
        """
        # Security: Validate proof structure
        required_attrs = ['commitment1', 'commitment2', 'challenge1', 'challenge2', 'response1', 'response2']
        for attr in required_attrs:
            if not hasattr(proof, attr):
                logger.warning("Invalid OR proof structure: missing '%s'. Ensure proof was created with ORProof.prove_non_interactive()", attr)
                return False

        # Security: Check for identity element (potential attack vector)
        try:
            identity = group.init(G1, 1)
            if proof.commitment1 == identity or proof.commitment2 == identity:
                logger.warning("Security: OR proof commitment is identity element")
                return False
        except Exception:
            pass  # Some groups may not support identity check

        # Recompute main challenge: c = H(g, h1, h2, u1, u2)
        expected_c = cls._compute_challenge_hash(
            group, g, h1, h2, proof.commitment1, proof.commitment2
        )

        # Check c1 + c2 = c (challenge splitting)
        actual_c = proof.challenge1 + proof.challenge2
        if expected_c != actual_c:
            logger.debug("Challenge sum mismatch in OR verification")
            return False

        # Check first branch: g^z1 = u1 * h1^c1
        lhs1 = g ** proof.response1
        rhs1 = proof.commitment1 * (h1 ** proof.challenge1)
        if lhs1 != rhs1:
            logger.debug("First branch verification failed")
            return False

        # Check second branch: g^z2 = u2 * h2^c2
        lhs2 = g ** proof.response2
        rhs2 = proof.commitment2 * (h2 ** proof.challenge2)
        if lhs2 != rhs2:
            logger.debug("Second branch verification failed")
            return False

        logger.debug("OR proof verification succeeded")
        return True

    @classmethod
    def serialize_proof(cls, proof: 'ORProofData', group: PairingGroup) -> bytes:
        """
        Serialize OR proof to bytes using Charm utilities.

        Args:
            proof: ORProofData object to serialize
            group: The pairing group

        Returns:
            Bytes representation of the proof
        """
        proof_dict = {
            'commitment1': proof.commitment1,
            'commitment2': proof.commitment2,
            'challenge1': proof.challenge1,
            'challenge2': proof.challenge2,
            'response1': proof.response1,
            'response2': proof.response2,
            'proof_type': proof.proof_type
        }
        return objectToBytes(proof_dict, group)

    @classmethod
    def deserialize_proof(cls, data: bytes, group: PairingGroup) -> 'ORProofData':
        """
        Deserialize bytes to OR proof.

        Args:
            data: Bytes to deserialize
            group: The pairing group

        Returns:
            ORProofData object
        """
        proof_dict = bytesToObject(data, group)
        return ORProofData(
            commitment1=proof_dict['commitment1'],
            commitment2=proof_dict['commitment2'],
            challenge1=proof_dict['challenge1'],
            challenge2=proof_dict['challenge2'],
            response1=proof_dict['response1'],
            response2=proof_dict['response2'],
            proof_type=proof_dict.get('proof_type', 'or')
        )
