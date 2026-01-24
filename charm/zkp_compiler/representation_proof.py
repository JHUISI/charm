"""
Knowledge of Representation Zero-Knowledge Proof implementation.

This module provides a direct implementation of the Knowledge of Representation
ZKP protocol for proving knowledge of multiple discrete logarithms simultaneously.

=== What This Proves ===
The Representation proof proves: "I know (x1, x2, ..., xn) such that 
h = g1^x1 * g2^x2 * ... * gn^xn" without revealing any of the xi values.

This is a generalization of Schnorr's proof to multiple bases. While Schnorr
proves knowledge of a single discrete log, representation proofs prove knowledge
of multiple discrete logs whose weighted combination (in the exponent) produces
a given public value.

=== Mathematical Basis ===
Given:
    - Public generators: g1, g2, ..., gn (in group G)
    - Public value: h = g1^x1 * g2^x2 * ... * gn^xn
    - Secret witnesses: x1, x2, ..., xn (in Zr)

The protocol works because:
    1. Prover commits to random values r1, r2, ..., rn via u = g1^r1 * g2^r2 * ... * gn^rn
    2. Given challenge c, prover computes zi = ri + c*xi for each i
    3. Verification checks: g1^z1 * g2^z2 * ... * gn^zn == u * h^c
    
    This works because:
    g1^z1 * g2^z2 * ... * gn^zn 
    = g1^(r1+c*x1) * g2^(r2+c*x2) * ... * gn^(rn+c*xn)
    = (g1^r1 * g2^r2 * ... * gn^rn) * (g1^x1 * g2^x2 * ... * gn^xn)^c
    = u * h^c

=== Security Properties ===
- Zero-Knowledge: The verifier learns nothing about xi beyond validity of the proof
- Soundness: A prover who doesn't know the witnesses cannot produce a valid proof
  (except with negligible probability)
- Completeness: An honest prover with valid witnesses always convinces the verifier

=== Use Cases ===
1. Pedersen Commitments: Prove knowledge of (v, r) for C = g^v * h^r (n=2)
2. Anonymous Credentials: Prove possession of multiple hidden attributes
3. Multi-Attribute Proofs: Prove knowledge of several values in a single proof
4. Range Proofs: Often built on top of representation proofs
5. Voting Schemes: Prove ballot is well-formed without revealing vote

Usage Examples:
    # Interactive mode (see class docstrings for full examples)
    prover = RepresentationProof.Prover(witnesses, group)
    verifier = RepresentationProof.Verifier(group)
    commitment = prover.create_commitment(generators)
    challenge = verifier.create_challenge()
    responses = prover.create_response(challenge)
    valid = verifier.verify(generators, h, commitment, responses)
    
    # Non-interactive mode
    proof = RepresentationProof.prove_non_interactive(group, generators, h, witnesses)
    valid = RepresentationProof.verify_non_interactive(group, generators, h, proof)
"""

from typing import List, Any

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.core.engine.util import objectToBytes, bytesToObject
import logging

logger = logging.getLogger(__name__)


class RepresentationProofData:
    """Container for Representation proof data.
    
    Holds the commitment, challenge, and list of responses for a
    knowledge of representation proof.
    """

    def __init__(self, commitment: Any, challenge: Any, responses: List[Any], proof_type: str = 'representation') -> None:
        """
        Initialize a representation proof.

        Args:
            commitment: The prover's commitment (u = g1^r1 * g2^r2 * ... * gn^rn)
            challenge: The challenge value (c)
            responses: List of response values [z1, z2, ..., zn] where zi = ri + c*xi
            proof_type: Type identifier for the proof
        """
        self.commitment = commitment
        self.challenge = challenge
        self.responses = responses
        self.proof_type = proof_type


class RepresentationProof:
    """
    Knowledge of Representation Zero-Knowledge Proof.

    Proves knowledge of (x1, x2, ..., xn) such that h = g1^x1 * g2^x2 * ... * gn^xn
    without revealing any xi.

    This is a generalization of Schnorr's proof that enables proving knowledge
    of multiple discrete logarithms simultaneously. It forms the basis for
    many practical cryptographic protocols including Pedersen commitment
    openings and anonymous credential systems.

    Supports both interactive and non-interactive (Fiat-Shamir) modes.

    Example (Non-Interactive):
        >>> group = PairingGroup('BN254')
        >>> # Setup: two generators and two witnesses
        >>> g1, g2 = group.random(G1), group.random(G1)
        >>> x1, x2 = group.random(ZR), group.random(ZR)
        >>> h = (g1 ** x1) * (g2 ** x2)  # Public value
        >>> 
        >>> # Prove knowledge of x1, x2
        >>> proof = RepresentationProof.prove_non_interactive(
        ...     group, [g1, g2], h, [x1, x2])
        >>> 
        >>> # Verify the proof
        >>> valid = RepresentationProof.verify_non_interactive(
        ...     group, [g1, g2], h, proof)
        >>> assert valid

    Example (Interactive):
        >>> group = PairingGroup('BN254')
        >>> g1, g2 = group.random(G1), group.random(G1)
        >>> x1, x2 = group.random(ZR), group.random(ZR)
        >>> h = (g1 ** x1) * (g2 ** x2)
        >>> 
        >>> # Interactive protocol
        >>> prover = RepresentationProof.Prover([x1, x2], group)
        >>> verifier = RepresentationProof.Verifier(group)
        >>> 
        >>> commitment = prover.create_commitment([g1, g2])
        >>> challenge = verifier.create_challenge()
        >>> responses = prover.create_response(challenge)
        >>> valid = verifier.verify([g1, g2], h, commitment, responses)
    """

    class Prover:
        """Prover for Representation protocol.
        
        The prover knows the secret witnesses (x1, x2, ..., xn) and wants
        to prove this knowledge without revealing the actual values.
        """

        def __init__(self, witnesses, group):
            """
            Initialize prover with secret witnesses.

            Args:
                witnesses: List of secret discrete log values [x1, x2, ..., xn]
                group: The pairing group object
            """
            self._r_values = None  # Random commitment values (private)
            self.group = group
            self._witnesses = witnesses  # Secrets (private)
            self._n = len(witnesses)  # Number of witnesses

        def create_commitment(self, generators):
            """
            Create prover's commitment: u = g1^r1 * g2^r2 * ... * gn^rn.

            Args:
                generators: List of generator elements [g1, g2, ..., gn]

            Returns:
                The commitment u = prod(gi^ri)
                
            Raises:
                ValueError: If number of generators doesn't match number of witnesses
            """
            if len(generators) != self._n:
                raise ValueError(
                    f"Number of generators ({len(generators)}) must match "
                    f"number of witnesses ({self._n})"
                )

            # Generate random values r1, r2, ..., rn
            self._r_values = [self.group.random(ZR) for _ in range(self._n)]

            # Compute commitment u = g1^r1 * g2^r2 * ... * gn^rn
            u = generators[0] ** self._r_values[0]
            for i in range(1, self._n):
                u = u * (generators[i] ** self._r_values[i])

            logger.debug("Prover created commitment for %d witnesses", self._n)
            return u

        def create_response(self, challenge):
            """
            Create responses to verifier's challenge: zi = ri + c*xi for each i.

            Args:
                challenge: The challenge value c from verifier

            Returns:
                List of responses [z1, z2, ..., zn] where zi = ri + c*xi

            Raises:
                ValueError: If create_commitment was not called first
            """
            if self._r_values is None:
                raise ValueError("Must call create_commitment before create_response")

            # Compute zi = ri + c*xi for each witness
            responses = []
            for i in range(self._n):
                z_i = self._r_values[i] + challenge * self._witnesses[i]
                responses.append(z_i)

            logger.debug("Prover created %d responses", self._n)
            return responses

    class Verifier:
        """Verifier for Representation protocol.

        The verifier checks the proof without learning the secret witnesses.
        """

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

        def verify(self, generators, h, commitment, responses):
            """
            Verify proof: g1^z1 * g2^z2 * ... * gn^zn == u * h^c.

            Args:
                generators: List of generator elements [g1, g2, ..., gn]
                h: The public value h = g1^x1 * g2^x2 * ... * gn^xn
                commitment: The prover's commitment u
                responses: List of prover's responses [z1, z2, ..., zn]

            Returns:
                True if proof is valid, False otherwise

            Raises:
                ValueError: If create_challenge was not called first
                ValueError: If number of generators doesn't match number of responses
            """
            if self._c is None:
                raise ValueError("Must call create_challenge before verify")

            if len(generators) != len(responses):
                raise ValueError(
                    f"Number of generators ({len(generators)}) must match "
                    f"number of responses ({len(responses)})"
                )

            n = len(generators)

            # Compute LHS: g1^z1 * g2^z2 * ... * gn^zn
            lhs = generators[0] ** responses[0]
            for i in range(1, n):
                lhs = lhs * (generators[i] ** responses[i])

            # Compute RHS: u * h^c
            rhs = commitment * (h ** self._c)

            result = lhs == rhs
            logger.debug("Verification result: %s", result)
            return result

    @classmethod
    def _compute_challenge_hash(cls, group, generators, h, commitment):
        """
        Compute Fiat-Shamir challenge as hash of public values.

        The challenge is computed as H(g1 || g2 || ... || gn || h || u)
        where || denotes concatenation of serialized elements.

        Args:
            group: The pairing group
            generators: List of generators [g1, g2, ..., gn]
            h: Public value h = g1^x1 * g2^x2 * ... * gn^xn
            commitment: The commitment u

        Returns:
            Challenge c as element of ZR
        """
        # Serialize all generators
        data = b''
        for g in generators:
            data += objectToBytes(g, group)

        # Add h and commitment
        data += objectToBytes(h, group)
        data += objectToBytes(commitment, group)

        return group.hash(data, ZR)

    @classmethod
    def prove_non_interactive(cls, group: PairingGroup, generators: List[Any], h: Any, witnesses: List[Any]) -> 'RepresentationProofData':
        """
        Generate non-interactive proof using Fiat-Shamir heuristic.

        Creates a proof that the prover knows witnesses (x1, x2, ..., xn)
        such that h = g1^x1 * g2^x2 * ... * gn^xn.

        Args:
            group: The pairing group
            generators: List of generator elements [g1, g2, ..., gn]
            h: The public value h = g1^x1 * g2^x2 * ... * gn^xn
            witnesses: List of secret discrete log values [x1, x2, ..., xn]

        Returns:
            RepresentationProofData object containing commitment, challenge, and responses

        Raises:
            ValueError: If number of generators doesn't match number of witnesses
        """
        n = len(generators)
        if len(witnesses) != n:
            raise ValueError(
                f"Number of generators ({n}) must match number of witnesses ({len(witnesses)})"
            )

        # 1. Generate random values r1, r2, ..., rn
        r_values = [group.random(ZR) for _ in range(n)]

        # 2. Compute commitment u = g1^r1 * g2^r2 * ... * gn^rn
        commitment = generators[0] ** r_values[0]
        for i in range(1, n):
            commitment = commitment * (generators[i] ** r_values[i])

        # 3. Compute challenge c = hash(g1, g2, ..., gn, h, u)
        challenge = cls._compute_challenge_hash(group, generators, h, commitment)

        # 4. Compute responses zi = ri + c*xi for each i
        responses = []
        for i in range(n):
            z_i = r_values[i] + challenge * witnesses[i]
            responses.append(z_i)

        logger.debug("Generated non-interactive representation proof for %d witnesses", n)
        return RepresentationProofData(
            commitment=commitment,
            challenge=challenge,
            responses=responses,
            proof_type='representation'
        )

    @classmethod
    def verify_non_interactive(cls, group: PairingGroup, generators: List[Any], h: Any, proof: 'RepresentationProofData') -> bool:
        """
        Verify non-interactive representation proof.

        Checks that the prover knows witnesses (x1, x2, ..., xn) such that
        h = g1^x1 * g2^x2 * ... * gn^xn.

        Args:
            group: The pairing group
            generators: List of generator elements [g1, g2, ..., gn]
            h: The public value h = g1^x1 * g2^x2 * ... * gn^xn
            proof: RepresentationProofData object containing commitment, challenge, responses

        Returns:
            True if proof is valid, False otherwise

        Security Notes:
            - Validates proof structure before verification
            - Checks for identity element attacks
            - Recomputes Fiat-Shamir challenge for consistency
        """
        # Security: Validate proof structure
        required_attrs = ['commitment', 'challenge', 'responses']
        for attr in required_attrs:
            if not hasattr(proof, attr):
                logger.warning("Invalid Representation proof structure: missing '%s'. Ensure proof was created with RepresentationProof.prove_non_interactive()", attr)
                return False

        # Security: Check for identity element (potential attack vector)
        try:
            identity = group.init(G1, 1)
            if proof.commitment == identity:
                logger.warning("Security: Representation proof commitment is identity element")
                return False
        except Exception:
            pass  # Some groups may not support identity check

        n = len(generators)

        # Validate proof structure
        if len(proof.responses) != n:
            logger.debug(
                "Proof response count (%d) doesn't match generator count (%d)",
                len(proof.responses), n
            )
            return False

        # Recompute challenge c = hash(g1, g2, ..., gn, h, commitment)
        expected_challenge = cls._compute_challenge_hash(group, generators, h, proof.commitment)

        # Verify challenge matches (Fiat-Shamir consistency check)
        if expected_challenge != proof.challenge:
            logger.debug("Challenge mismatch in non-interactive verification")
            return False

        # Check: g1^z1 * g2^z2 * ... * gn^zn == commitment * h^c
        # LHS: g1^z1 * g2^z2 * ... * gn^zn
        lhs = generators[0] ** proof.responses[0]
        for i in range(1, n):
            lhs = lhs * (generators[i] ** proof.responses[i])

        # RHS: commitment * h^c
        rhs = proof.commitment * (h ** proof.challenge)

        result = lhs == rhs
        logger.debug("Non-interactive verification result: %s", result)
        return result

    @classmethod
    def serialize_proof(cls, proof: 'RepresentationProofData', group: PairingGroup) -> bytes:
        """
        Serialize proof to bytes using Charm utilities.

        Args:
            proof: RepresentationProofData object to serialize
            group: The pairing group

        Returns:
            Bytes representation of the proof
        """
        proof_dict = {
            'commitment': proof.commitment,
            'challenge': proof.challenge,
            'responses': proof.responses,
            'proof_type': proof.proof_type
        }
        return objectToBytes(proof_dict, group)

    @classmethod
    def deserialize_proof(cls, data: bytes, group: PairingGroup) -> 'RepresentationProofData':
        """
        Deserialize bytes to proof.

        Args:
            data: Bytes to deserialize
            group: The pairing group

        Returns:
            RepresentationProofData object
        """
        proof_dict = bytesToObject(data, group)
        return RepresentationProofData(
            commitment=proof_dict['commitment'],
            challenge=proof_dict['challenge'],
            responses=proof_dict['responses'],
            proof_type=proof_dict.get('proof_type', 'representation')
        )
