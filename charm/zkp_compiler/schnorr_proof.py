"""
Schnorr's Zero-Knowledge Proof implementation without exec().

This module provides a direct implementation of Schnorr's ZKP protocol
for proving knowledge of discrete logarithm.
"""

from typing import Any

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.core.engine.util import objectToBytes, bytesToObject
import logging

logger = logging.getLogger(__name__)


class Proof:
    """Simple container for ZKP proof data."""

    def __init__(self, commitment: Any, challenge: Any, response: Any, proof_type: str = 'schnorr') -> None:
        """
        Initialize a proof.

        Args:
            commitment: The prover's commitment (u = g^r)
            challenge: The challenge value (c)
            response: The response value (z = r + c*x)
            proof_type: Type identifier for the proof
        """
        self.commitment = commitment
        self.challenge = challenge
        self.response = response
        self.proof_type = proof_type


class SchnorrProof:
    """
    Schnorr's Zero-Knowledge Proof of Knowledge of Discrete Logarithm.

    Proves knowledge of x such that h = g^x without revealing x.

    Supports both interactive and non-interactive (Fiat-Shamir) modes.
    """

    class Prover:
        """Prover for Schnorr protocol."""

        def __init__(self, secret_x, group):
            """
            Initialize prover with secret x.

            Args:
                secret_x: The secret discrete log value
                group: The pairing group object
            """
            self._r = None  # Random commitment value (private)
            self.group = group
            self._x = secret_x  # Secret (private)

        def create_commitment(self, g):
            """
            Create prover's commitment: u = g^r.

            Args:
                g: The generator element

            Returns:
                The commitment u = g^r
            """
            self._r = self.group.random(ZR)
            u = g ** self._r
            logger.debug("Prover created commitment")
            return u

        def create_response(self, challenge):
            """
            Create response to verifier's challenge: z = r + c*x.

            Args:
                challenge: The challenge value c from verifier

            Returns:
                The response z = r + c*x
            """
            if self._r is None:
                raise ValueError("Must call create_commitment before create_response")
            z = self._r + challenge * self._x
            logger.debug("Prover created response")
            return z

    class Verifier:
        """Verifier for Schnorr protocol."""

        def __init__(self, group):
            """
            Initialize verifier.

            Args:
                group: The pairing group object
            """
            self.group = group
            self._c = None  # Challenge (stored for verification)

        def create_challenge(self):
            """
            Create random challenge c.

            Returns:
                Random challenge c in ZR
            """
            self._c = self.group.random(ZR)
            logger.debug("Verifier created challenge")
            return self._c

        def verify(self, g, h, commitment, response):
            """
            Verify proof: g^z == u * h^c.

            Args:
                g: The generator element
                h: The public value h = g^x
                commitment: The prover's commitment u
                response: The prover's response z

            Returns:
                True if proof is valid, False otherwise
            """
            if self._c is None:
                raise ValueError("Must call create_challenge before verify")
            lhs = g ** response
            rhs = commitment * (h ** self._c)
            result = lhs == rhs
            logger.debug("Verification result: %s", result)
            return result

    @classmethod
    def _compute_challenge_hash(cls, group, g, h, commitment):
        """
        Compute Fiat-Shamir challenge as hash of public values.

        Args:
            group: The pairing group
            g: Generator
            h: Public value h = g^x
            commitment: The commitment u = g^r

        Returns:
            Challenge c as element of ZR
        """
        # Serialize elements and concatenate for hashing
        data = objectToBytes(g, group) + objectToBytes(h, group) + objectToBytes(commitment, group)
        return group.hash(data, ZR)

    @classmethod
    def prove_non_interactive(cls, group: PairingGroup, g: Any, h: Any, x: Any) -> Proof:
        """
        Generate non-interactive proof using Fiat-Shamir heuristic.

        Args:
            group: The pairing group
            g: The generator element
            h: The public value h = g^x
            x: The secret discrete log

        Returns:
            Proof object containing commitment, challenge, and response
        """
        # 1. Generate random r
        r = group.random(ZR)

        # 2. Compute commitment u = g^r
        commitment = g ** r

        # 3. Compute challenge c = hash(g, h, u)
        challenge = cls._compute_challenge_hash(group, g, h, commitment)

        # 4. Compute response z = r + c*x
        response = r + challenge * x

        logger.debug("Generated non-interactive proof")
        return Proof(commitment=commitment, challenge=challenge, response=response, proof_type='schnorr')

    @classmethod
    def verify_non_interactive(cls, group: PairingGroup, g: Any, h: Any, proof: Proof) -> bool:
        """
        Verify non-interactive proof.

        Args:
            group: The pairing group
            g: The generator element
            h: The public value h = g^x
            proof: Proof object containing commitment, challenge, and response

        Returns:
            True if proof is valid, False otherwise

        Security Notes:
            - Validates proof structure before verification
            - Checks for identity element attacks
            - Recomputes Fiat-Shamir challenge for consistency
        """
        # Security: Validate proof structure
        required_attrs = ['commitment', 'challenge', 'response']
        for attr in required_attrs:
            if not hasattr(proof, attr):
                logger.warning("Invalid Schnorr proof structure: missing '%s'. Ensure proof was created with SchnorrProof.prove_non_interactive()", attr)
                return False

        # Security: Check for identity element (potential attack vector)
        # The identity element would make the verification equation trivially true
        try:
            identity = group.init(G1, 1)
            if proof.commitment == identity:
                logger.warning("Security: Schnorr proof commitment is identity element (possible attack). Proof rejected.")
                return False
        except Exception:
            pass  # Some groups may not support identity check

        # Recompute challenge c = hash(g, h, commitment)
        expected_challenge = cls._compute_challenge_hash(group, g, h, proof.commitment)

        # Verify challenge matches
        if expected_challenge != proof.challenge:
            logger.debug("Challenge mismatch in non-interactive verification")
            return False

        # Check g^z == commitment * h^c
        lhs = g ** proof.response
        rhs = proof.commitment * (h ** proof.challenge)
        result = lhs == rhs
        logger.debug("Non-interactive verification result: %s", result)
        return result

    @classmethod
    def serialize_proof(cls, proof: Proof, group: PairingGroup) -> bytes:
        """
        Serialize proof to bytes using Charm utilities.

        Args:
            proof: Proof object to serialize
            group: The pairing group

        Returns:
            Bytes representation of the proof
        """
        proof_dict = {
            'commitment': proof.commitment,
            'challenge': proof.challenge,
            'response': proof.response,
            'proof_type': proof.proof_type
        }
        return objectToBytes(proof_dict, group)

    @classmethod
    def deserialize_proof(cls, data: bytes, group: PairingGroup) -> Proof:
        """
        Deserialize bytes to proof.

        Args:
            data: Bytes to deserialize
            group: The pairing group

        Returns:
            Proof object
        """
        proof_dict = bytesToObject(data, group)
        return Proof(
            commitment=proof_dict['commitment'],
            challenge=proof_dict['challenge'],
            response=proof_dict['response'],
            proof_type=proof_dict.get('proof_type', 'schnorr')
        )

