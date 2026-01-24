"""
DLEQ (Discrete Log Equality) Zero-Knowledge Proof implementation.

Also known as the Chaum-Pedersen protocol, this module provides proof of
knowledge that two discrete logarithms are equal without revealing the
secret exponent.

=============================================================================
WHAT DLEQ PROVES
=============================================================================
DLEQ proves: "I know x such that h1 = g1^x AND h2 = g2^x"

This is a proof of equality of discrete logs: the prover demonstrates that
the same secret exponent x was used to compute both h1 (relative to base g1)
and h2 (relative to base g2), without revealing x itself.

=============================================================================
MATHEMATICAL BASIS
=============================================================================
The protocol works as follows:

Interactive Version:
1. Prover picks random r ∈ Zq
2. Prover computes commitments: u1 = g1^r, u2 = g2^r
3. Verifier sends random challenge c ∈ Zq
4. Prover computes response: z = r + c*x (mod q)
5. Verifier accepts if: g1^z == u1 * h1^c AND g2^z == u2 * h2^c

Correctness:
- If prover is honest: g1^z = g1^(r + c*x) = g1^r * g1^(c*x) = u1 * (g1^x)^c = u1 * h1^c ✓
- Same reasoning applies for the second equation with g2 and h2

Soundness:
- A cheating prover who knows x1 ≠ x2 where h1 = g1^x1 and h2 = g2^x2 cannot
  produce a valid response z that satisfies both verification equations
  (except with negligible probability)

=============================================================================
SECURITY PROPERTIES
=============================================================================
1. HVZK (Honest-Verifier Zero-Knowledge):
   - A simulator can produce transcripts indistinguishable from real proofs
   - Simulator: pick random z, c; compute u1 = g1^z * h1^(-c), u2 = g2^z * h2^(-c)
   - This transcript (u1, u2, c, z) is identically distributed to real proofs

2. NIZK (Non-Interactive ZK via Fiat-Shamir):
   - Replace interactive challenge with hash: c = H(g1, h1, g2, h2, u1, u2)
   - Secure in the Random Oracle Model
   - Produces publicly verifiable proofs

3. Special Soundness:
   - Given two accepting transcripts with same commitments but different
     challenges (c, z) and (c', z'), one can extract: x = (z - z') / (c - c')

=============================================================================
USE CASES
=============================================================================
1. Verifiable Random Functions (VRFs):
   - Prove VRF output is correctly computed without revealing secret key

2. ElGamal Re-encryption Proofs:
   - Prove ciphertext was correctly re-randomized

3. Threshold Cryptography:
   - Prove partial decryption shares are correctly computed

4. Voting Systems:
   - Prove vote encryption uses consistent randomness

5. Credential Systems:
   - Prove different presentations derive from same credential

6. Diffie-Hellman Tuple Proofs:
   - Prove (g1, h1, g2, h2) is a valid DH tuple
"""

from typing import Any

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.core.engine.util import objectToBytes, bytesToObject
import logging

logger = logging.getLogger(__name__)


class DLEQProofData:
    """Container for DLEQ proof data with two commitments."""

    def __init__(self, commitment1: Any, commitment2: Any, challenge: Any, response: Any, proof_type: str = 'dleq') -> None:
        """
        Initialize a DLEQ proof.

        Args:
            commitment1: The prover's first commitment (u1 = g1^r)
            commitment2: The prover's second commitment (u2 = g2^r)
            challenge: The challenge value (c)
            response: The response value (z = r + c*x)
            proof_type: Type identifier for the proof
        """
        self.commitment1 = commitment1
        self.commitment2 = commitment2
        self.challenge = challenge
        self.response = response
        self.proof_type = proof_type


class DLEQProof:
    """
    DLEQ (Discrete Log Equality) Zero-Knowledge Proof.

    Proves knowledge of x such that h1 = g1^x AND h2 = g2^x without revealing x.
    Also known as the Chaum-Pedersen protocol.

    Supports both interactive and non-interactive (Fiat-Shamir) modes.

    Example (non-interactive):
        >>> group = PairingGroup('SS512')
        >>> g1 = group.random(G1)
        >>> g2 = group.random(G1)
        >>> x = group.random(ZR)  # Secret exponent
        >>> h1 = g1 ** x
        >>> h2 = g2 ** x
        >>>
        >>> # Prove h1 = g1^x and h2 = g2^x for the same x
        >>> proof = DLEQProof.prove_non_interactive(group, g1, h1, g2, h2, x)
        >>> assert DLEQProof.verify_non_interactive(group, g1, h1, g2, h2, proof)

    Example (interactive):
        >>> prover = DLEQProof.Prover(x, group)
        >>> verifier = DLEQProof.Verifier(group)
        >>>
        >>> # Step 1: Prover creates commitments
        >>> u1, u2 = prover.create_commitment(g1, g2)
        >>>
        >>> # Step 2: Verifier creates challenge
        >>> c = verifier.create_challenge()
        >>>
        >>> # Step 3: Prover creates response
        >>> z = prover.create_response(c)
        >>>
        >>> # Step 4: Verifier checks proof
        >>> assert verifier.verify(g1, h1, g2, h2, u1, u2, z)
    """

    class Prover:
        """Prover for DLEQ protocol."""

        def __init__(self, secret_x, group):
            """
            Initialize prover with secret x.

            Args:
                secret_x: The secret discrete log value (same for both bases)
                group: The pairing group object
            """
            self._r = None  # Random commitment value (private)
            self.group = group
            self._x = secret_x  # Secret (private)

        def create_commitment(self, g1, g2):
            """
            Create prover's commitments: u1 = g1^r, u2 = g2^r.

            Uses the same random r for both commitments to prove
            equality of discrete logs.

            Args:
                g1: The first generator element
                g2: The second generator element

            Returns:
                Tuple (u1, u2) where u1 = g1^r and u2 = g2^r
            """
            self._r = self.group.random(ZR)
            u1 = g1 ** self._r
            u2 = g2 ** self._r
            logger.debug("Prover created DLEQ commitments")
            return u1, u2

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
            logger.debug("Prover created DLEQ response")
            return z

    class Verifier:
        """Verifier for DLEQ protocol."""

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
            logger.debug("Verifier created DLEQ challenge")
            return self._c

        def verify(self, g1, h1, g2, h2, commitment1, commitment2, response):
            """
            Verify DLEQ proof: g1^z == u1 * h1^c AND g2^z == u2 * h2^c.

            Args:
                g1: The first generator element
                h1: The first public value h1 = g1^x
                g2: The second generator element
                h2: The second public value h2 = g2^x
                commitment1: The prover's first commitment u1
                commitment2: The prover's second commitment u2
                response: The prover's response z

            Returns:
                True if proof is valid, False otherwise
            """
            if self._c is None:
                raise ValueError("Must call create_challenge before verify")

            # Check first equation: g1^z == u1 * h1^c
            lhs1 = g1 ** response
            rhs1 = commitment1 * (h1 ** self._c)
            check1 = lhs1 == rhs1

            # Check second equation: g2^z == u2 * h2^c
            lhs2 = g2 ** response
            rhs2 = commitment2 * (h2 ** self._c)
            check2 = lhs2 == rhs2

            result = check1 and check2
            logger.debug("DLEQ verification result: %s (check1=%s, check2=%s)",
                         result, check1, check2)
            return result

    @classmethod
    def _compute_challenge_hash(cls, group, g1, h1, g2, h2, commitment1, commitment2):
        """
        Compute Fiat-Shamir challenge as hash of all public values.

        Args:
            group: The pairing group
            g1: First generator
            h1: First public value h1 = g1^x
            g2: Second generator
            h2: Second public value h2 = g2^x
            commitment1: First commitment u1 = g1^r
            commitment2: Second commitment u2 = g2^r

        Returns:
            Challenge c as element of ZR
        """
        # Serialize all elements and concatenate for hashing
        # Order: g1, h1, g2, h2, u1, u2 (matching protocol description)
        data = (objectToBytes(g1, group) +
                objectToBytes(h1, group) +
                objectToBytes(g2, group) +
                objectToBytes(h2, group) +
                objectToBytes(commitment1, group) +
                objectToBytes(commitment2, group))
        return group.hash(data, ZR)

    @classmethod
    def prove_non_interactive(cls, group: PairingGroup, g1: Any, h1: Any, g2: Any, h2: Any, x: Any) -> DLEQProofData:
        """
        Generate non-interactive DLEQ proof using Fiat-Shamir heuristic.

        Proves knowledge of x such that h1 = g1^x AND h2 = g2^x.

        Args:
            group: The pairing group
            g1: The first generator element
            h1: The first public value h1 = g1^x
            g2: The second generator element
            h2: The second public value h2 = g2^x
            x: The secret discrete log (same for both equations)

        Returns:
            DLEQProofData object containing commitments, challenge, and response
        """
        # 1. Generate random r
        r = group.random(ZR)

        # 2. Compute commitments u1 = g1^r, u2 = g2^r
        commitment1 = g1 ** r
        commitment2 = g2 ** r

        # 3. Compute challenge c = hash(g1, h1, g2, h2, u1, u2)
        challenge = cls._compute_challenge_hash(
            group, g1, h1, g2, h2, commitment1, commitment2)

        # 4. Compute response z = r + c*x
        response = r + challenge * x

        logger.debug("Generated non-interactive DLEQ proof")
        return DLEQProofData(
            commitment1=commitment1,
            commitment2=commitment2,
            challenge=challenge,
            response=response,
            proof_type='dleq'
        )

    @classmethod
    def verify_non_interactive(cls, group: PairingGroup, g1: Any, h1: Any, g2: Any, h2: Any, proof: DLEQProofData) -> bool:
        """
        Verify non-interactive DLEQ proof.

        Args:
            group: The pairing group
            g1: The first generator element
            h1: The first public value h1 = g1^x
            g2: The second generator element
            h2: The second public value h2 = g2^x
            proof: DLEQProofData object containing commitments, challenge, and response

        Returns:
            True if proof is valid, False otherwise

        Security Notes:
            - Validates proof structure before verification
            - Checks for identity element attacks
            - Recomputes Fiat-Shamir challenge for consistency
        """
        # Security: Validate proof structure
        required_attrs = ['commitment1', 'commitment2', 'challenge', 'response']
        for attr in required_attrs:
            if not hasattr(proof, attr):
                logger.warning("Invalid DLEQ proof structure: missing '%s'. Ensure proof was created with DLEQProof.prove_non_interactive()", attr)
                return False

        # Security: Check for identity element (potential attack vector)
        try:
            identity = group.init(G1, 1)
            if proof.commitment1 == identity or proof.commitment2 == identity:
                logger.warning("Security: DLEQ proof commitment is identity element (possible attack). Proof rejected.")
                return False
        except Exception:
            pass  # Some groups may not support identity check

        # Recompute challenge c = hash(g1, h1, g2, h2, u1, u2)
        expected_challenge = cls._compute_challenge_hash(
            group, g1, h1, g2, h2, proof.commitment1, proof.commitment2)

        # Verify challenge matches (Fiat-Shamir consistency check)
        if expected_challenge != proof.challenge:
            logger.debug("Challenge mismatch in non-interactive DLEQ verification")
            return False

        # Check first equation: g1^z == u1 * h1^c
        lhs1 = g1 ** proof.response
        rhs1 = proof.commitment1 * (h1 ** proof.challenge)
        check1 = lhs1 == rhs1

        # Check second equation: g2^z == u2 * h2^c
        lhs2 = g2 ** proof.response
        rhs2 = proof.commitment2 * (h2 ** proof.challenge)
        check2 = lhs2 == rhs2

        result = check1 and check2
        logger.debug("Non-interactive DLEQ verification result: %s (check1=%s, check2=%s)",
                     result, check1, check2)
        return result

    @classmethod
    def serialize_proof(cls, proof: DLEQProofData, group: PairingGroup) -> bytes:
        """
        Serialize DLEQ proof to bytes using Charm utilities.

        Args:
            proof: DLEQProofData object to serialize
            group: The pairing group

        Returns:
            Bytes representation of the proof
        """
        proof_dict = {
            'commitment1': proof.commitment1,
            'commitment2': proof.commitment2,
            'challenge': proof.challenge,
            'response': proof.response,
            'proof_type': proof.proof_type
        }
        return objectToBytes(proof_dict, group)

    @classmethod
    def deserialize_proof(cls, data: bytes, group: PairingGroup) -> DLEQProofData:
        """
        Deserialize bytes to DLEQ proof.

        Args:
            data: Bytes to deserialize
            group: The pairing group

        Returns:
            DLEQProofData object
        """
        proof_dict = bytesToObject(data, group)
        return DLEQProofData(
            commitment1=proof_dict['commitment1'],
            commitment2=proof_dict['commitment2'],
            challenge=proof_dict['challenge'],
            response=proof_dict['response'],
            proof_type=proof_dict.get('proof_type', 'dleq')
        )