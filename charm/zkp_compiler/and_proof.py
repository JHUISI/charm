"""
AND Composition for Zero-Knowledge Proofs.

This module provides AND composition functionality that allows proving multiple
statements simultaneously using a shared challenge.

=============================================================================
WHAT AND COMPOSITION PROVES
=============================================================================
AND composition proves: "Statement A AND Statement B AND ... AND Statement N"

Given multiple statements (e.g., Schnorr proofs, DLEQ proofs, representation proofs),
AND composition allows a prover to demonstrate knowledge of all corresponding
witnesses in a single, compact proof.

=============================================================================
HOW IT WORKS
=============================================================================
The key insight is that Sigma protocols (Schnorr, DLEQ, representation) can be
composed using a SHARED CHALLENGE:

1. Generate random commitments for each sub-proof independently
2. Compute a SINGLE shared challenge by hashing ALL commitments together
3. Compute responses for each sub-proof using the shared challenge
4. Verification checks all sub-proofs against the same shared challenge

This is more efficient than running independent proofs because:
- Only one challenge hash computation is needed
- The shared challenge binds all sub-proofs together cryptographically
- The total proof size is smaller than independent proofs

=============================================================================
SECURITY PROPERTIES
=============================================================================
1. Soundness: An adversary cannot forge a proof without knowing ALL witnesses.
   The shared challenge ensures that all statements must be proven simultaneously.

2. Zero-Knowledge: The simulator can produce transcripts indistinguishable from
   real proofs by simulating each sub-proof with the shared challenge.

3. Composability: AND composition preserves the security properties of the
   underlying Sigma protocols.

=============================================================================
USE CASES
=============================================================================
1. Multi-Attribute Proofs: Prove knowledge of multiple hidden attributes in a
   credential system (e.g., "I know age AND name AND address").

2. Compound Statements: Prove complex statements combining different proof types
   (e.g., "I know x such that h1 = g^x AND I know y such that h2 = g^y").

3. Efficient Batching: Combine multiple proofs into a single verification.

4. Anonymous Credentials: Prove multiple properties about a credential holder.

Example:
    >>> from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
    >>> from charm.zkp_compiler.and_proof import ANDProof
    >>>
    >>> group = PairingGroup('SS512')
    >>> g = group.random(G1)
    >>> x, y = group.random(ZR), group.random(ZR)
    >>> h1, h2 = g ** x, g ** y
    >>>
    >>> # Prove knowledge of x AND y such that h1 = g^x AND h2 = g^y
    >>> statements = [
    ...     {'type': 'schnorr', 'params': {'g': g, 'h': h1, 'x': x}},
    ...     {'type': 'schnorr', 'params': {'g': g, 'h': h2, 'x': y}},
    ... ]
    >>> proof = ANDProof.prove_non_interactive(group, statements)
    >>>
    >>> # For verification, use public statements (without secrets)
    >>> statements_public = [
    ...     {'type': 'schnorr', 'params': {'g': g, 'h': h1}},
    ...     {'type': 'schnorr', 'params': {'g': g, 'h': h2}},
    ... ]
    >>> valid = ANDProof.verify_non_interactive(group, statements_public, proof)
    >>> assert valid
"""

from typing import List, Any, Dict

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.zkp_compiler.schnorr_proof import SchnorrProof, Proof
from charm.zkp_compiler.dleq_proof import DLEQProof, DLEQProofData
from charm.zkp_compiler.representation_proof import RepresentationProof, RepresentationProofData
import logging

logger = logging.getLogger(__name__)


class ANDProofData:
    """Container for AND proof data with multiple sub-proofs."""

    def __init__(self, sub_proofs: List[Dict[str, Any]], shared_challenge: Any, proof_type: str = 'and') -> None:
        """
        Initialize an AND proof.

        Args:
            sub_proofs: List of individual proof data objects (commitments and responses)
            shared_challenge: The common challenge used for all proofs
            proof_type: Type identifier for the proof
        """
        self.sub_proofs = sub_proofs
        self.shared_challenge = shared_challenge
        self.proof_type = proof_type


class ANDProof:
    """
    AND Composition for Zero-Knowledge Proofs.

    Allows proving multiple statements simultaneously with a shared challenge.
    Supports combining Schnorr, DLEQ, and Representation proofs.

    Example:
        >>> group = PairingGroup('SS512')
        >>> g = group.random(G1)
        >>> x, y = group.random(ZR), group.random(ZR)
        >>> h1, h2 = g ** x, g ** y
        >>>
        >>> statements = [
        ...     {'type': 'schnorr', 'params': {'g': g, 'h': h1, 'x': x}},
        ...     {'type': 'schnorr', 'params': {'g': g, 'h': h2, 'x': y}},
        ... ]
        >>> proof = ANDProof.prove_non_interactive(group, statements)
        >>>
        >>> statements_public = [
        ...     {'type': 'schnorr', 'params': {'g': g, 'h': h1}},
        ...     {'type': 'schnorr', 'params': {'g': g, 'h': h2}},
        ... ]
        >>> valid = ANDProof.verify_non_interactive(group, statements_public, proof)
    """

    @classmethod
    def _generate_commitment(cls, group, statement):
        """
        Generate random commitment for a single statement.

        Returns tuple of (commitment_data, random_values) where commitment_data
        contains the public commitment(s) and random_values contains the secret
        randomness for computing responses.
        """
        stmt_type = statement['type']
        params = statement['params']

        if stmt_type == 'schnorr':
            r = group.random(ZR)
            commitment = params['g'] ** r
            return {'type': 'schnorr', 'commitment': commitment}, {'r': r}

        elif stmt_type == 'dleq':
            r = group.random(ZR)
            commitment1 = params['g1'] ** r
            commitment2 = params['g2'] ** r
            return {
                'type': 'dleq',
                'commitment1': commitment1,
                'commitment2': commitment2
            }, {'r': r}

        elif stmt_type == 'representation':
            generators = params['generators']
            r_values = [group.random(ZR) for _ in range(len(generators))]
            commitment = generators[0] ** r_values[0]
            for i in range(1, len(generators)):
                commitment = commitment * (generators[i] ** r_values[i])
            return {
                'type': 'representation',
                'commitment': commitment
            }, {'r_values': r_values}

        else:
            raise ValueError(f"Unsupported statement type: {stmt_type}")

    @classmethod
    def _compute_shared_challenge(cls, group, statements, commitments):
        """
        Compute shared Fiat-Shamir challenge from all public values and commitments.

        Args:
            group: The pairing group
            statements: List of statement dictionaries
            commitments: List of commitment data dictionaries

        Returns:
            Shared challenge as element of ZR
        """
        data = b''

        # Hash all public values and commitments in order
        for i, (stmt, commit) in enumerate(zip(statements, commitments)):
            stmt_type = stmt['type']
            params = stmt['params']

            if stmt_type == 'schnorr':
                data += objectToBytes(params['g'], group)
                data += objectToBytes(params['h'], group)
                data += objectToBytes(commit['commitment'], group)

            elif stmt_type == 'dleq':
                data += objectToBytes(params['g1'], group)
                data += objectToBytes(params['h1'], group)
                data += objectToBytes(params['g2'], group)
                data += objectToBytes(params['h2'], group)
                data += objectToBytes(commit['commitment1'], group)
                data += objectToBytes(commit['commitment2'], group)

            elif stmt_type == 'representation':
                for g in params['generators']:
                    data += objectToBytes(g, group)
                data += objectToBytes(params['h'], group)
                data += objectToBytes(commit['commitment'], group)

        return group.hash(data, ZR)

    @classmethod
    def _compute_response(cls, group, statement, random_values, challenge):
        """
        Compute response for a single statement given challenge.

        Args:
            group: The pairing group
            statement: Statement dictionary with type and params
            random_values: Random values used for commitment
            challenge: The shared challenge

        Returns:
            Response value(s) for this statement
        """
        stmt_type = statement['type']
        params = statement['params']

        if stmt_type == 'schnorr':
            # z = r + c*x
            return random_values['r'] + challenge * params['x']

        elif stmt_type == 'dleq':
            # z = r + c*x
            return random_values['r'] + challenge * params['x']

        elif stmt_type == 'representation':
            # zi = ri + c*xi for each witness
            responses = []
            for i, xi in enumerate(params['witnesses']):
                z_i = random_values['r_values'][i] + challenge * xi
                responses.append(z_i)
            return responses

        else:
            raise ValueError(f"Unsupported statement type: {stmt_type}")

    @classmethod
    def prove_non_interactive(cls, group: PairingGroup, statements: List[Dict[str, Any]]) -> 'ANDProofData':
        """
        Generate non-interactive AND proof using Fiat-Shamir heuristic.

        Args:
            group: The pairing group
            statements: List of statement dictionaries, each with:
                - 'type': 'schnorr', 'dleq', or 'representation'
                - 'params': Dict with required parameters for that proof type
                    - schnorr: {'g': generator, 'h': public_value, 'x': secret}
                    - dleq: {'g1': gen1, 'h1': pub1, 'g2': gen2, 'h2': pub2, 'x': secret}
                    - representation: {'generators': [g1,...], 'h': public, 'witnesses': [x1,...]}

        Returns:
            ANDProofData object containing sub-proofs and shared challenge
        """
        if not statements:
            raise ValueError("At least one statement is required")

        # Step 1: Generate commitments for all statements
        commitments = []
        random_values_list = []
        for stmt in statements:
            commit_data, rand_vals = cls._generate_commitment(group, stmt)
            commitments.append(commit_data)
            random_values_list.append(rand_vals)

        # Step 2: Compute shared challenge from all commitments
        shared_challenge = cls._compute_shared_challenge(group, statements, commitments)

        # Step 3: Compute responses for each statement using shared challenge
        sub_proofs = []
        for i, stmt in enumerate(statements):
            response = cls._compute_response(
                group, stmt, random_values_list[i], shared_challenge
            )
            sub_proof = {
                'type': stmt['type'],
                'commitment': commitments[i],
                'response': response
            }
            sub_proofs.append(sub_proof)

        logger.debug("Generated AND proof with %d sub-proofs", len(statements))
        return ANDProofData(
            sub_proofs=sub_proofs,
            shared_challenge=shared_challenge,
            proof_type='and'
        )

    @classmethod
    def _verify_sub_proof(cls, group, statement, sub_proof, challenge):
        """
        Verify a single sub-proof against the shared challenge.

        Args:
            group: The pairing group
            statement: Statement dictionary with type and public params
            sub_proof: Sub-proof dictionary with commitment and response
            challenge: The shared challenge

        Returns:
            True if sub-proof is valid, False otherwise
        """
        stmt_type = statement['type']
        params = statement['params']
        commitment = sub_proof['commitment']
        response = sub_proof['response']

        if stmt_type == 'schnorr':
            # Check: g^z == commitment * h^c
            lhs = params['g'] ** response
            rhs = commitment['commitment'] * (params['h'] ** challenge)
            return lhs == rhs

        elif stmt_type == 'dleq':
            # Check: g1^z == u1 * h1^c AND g2^z == u2 * h2^c
            lhs1 = params['g1'] ** response
            rhs1 = commitment['commitment1'] * (params['h1'] ** challenge)
            check1 = lhs1 == rhs1

            lhs2 = params['g2'] ** response
            rhs2 = commitment['commitment2'] * (params['h2'] ** challenge)
            check2 = lhs2 == rhs2

            return check1 and check2

        elif stmt_type == 'representation':
            # Check: g1^z1 * g2^z2 * ... * gn^zn == commitment * h^c
            generators = params['generators']
            n = len(generators)

            if len(response) != n:
                return False

            lhs = generators[0] ** response[0]
            for i in range(1, n):
                lhs = lhs * (generators[i] ** response[i])

            rhs = commitment['commitment'] * (params['h'] ** challenge)
            return lhs == rhs

        else:
            logger.warning("Unknown statement type in verification: %s", stmt_type)
            return False

    @classmethod
    def verify_non_interactive(cls, group: PairingGroup, statements: List[Dict[str, Any]], proof: 'ANDProofData') -> bool:
        """
        Verify non-interactive AND proof.

        Args:
            group: The pairing group
            statements: List of statement dictionaries with public parameters only
                - schnorr: {'g': generator, 'h': public_value}
                - dleq: {'g1': gen1, 'h1': pub1, 'g2': gen2, 'h2': pub2}
                - representation: {'generators': [g1,...], 'h': public_value}
            proof: ANDProofData object containing sub-proofs and shared challenge

        Returns:
            True if all sub-proofs are valid, False otherwise

        Security Notes:
            - Validates proof structure before verification
            - Verifies shared challenge consistency across all sub-proofs
            - Recomputes Fiat-Shamir challenge for consistency
        """
        # Security: Validate proof structure
        required_attrs = ['sub_proofs', 'shared_challenge']
        for attr in required_attrs:
            if not hasattr(proof, attr):
                logger.warning("Invalid AND proof structure: missing '%s'. Ensure proof was created with ANDProof.prove_non_interactive()", attr)
                return False

        if len(statements) != len(proof.sub_proofs):
            logger.debug(
                "Statement count (%d) doesn't match sub-proof count (%d)",
                len(statements), len(proof.sub_proofs)
            )
            return False

        # Reconstruct commitments list for challenge verification
        commitments = [sp['commitment'] for sp in proof.sub_proofs]

        # Recompute shared challenge
        expected_challenge = cls._compute_shared_challenge(group, statements, commitments)

        # Verify challenge matches
        if expected_challenge != proof.shared_challenge:
            logger.debug("Shared challenge mismatch in AND proof verification")
            return False

        # Verify each sub-proof
        for i, (stmt, sub_proof) in enumerate(zip(statements, proof.sub_proofs)):
            if stmt['type'] != sub_proof['type']:
                logger.debug(
                    "Statement type mismatch at index %d: expected %s, got %s",
                    i, stmt['type'], sub_proof['type']
                )
                return False

            if not cls._verify_sub_proof(group, stmt, sub_proof, proof.shared_challenge):
                logger.debug("Sub-proof %d verification failed", i)
                return False

        logger.debug("AND proof verification succeeded for %d sub-proofs", len(statements))
        return True

    @classmethod
    def serialize_proof(cls, proof: 'ANDProofData', group: PairingGroup) -> bytes:
        """
        Serialize AND proof to bytes using Charm utilities.

        Args:
            proof: ANDProofData object to serialize
            group: The pairing group

        Returns:
            Bytes representation of the proof
        """
        proof_dict = {
            'sub_proofs': proof.sub_proofs,
            'shared_challenge': proof.shared_challenge,
            'proof_type': proof.proof_type
        }
        return objectToBytes(proof_dict, group)

    @classmethod
    def deserialize_proof(cls, data: bytes, group: PairingGroup) -> 'ANDProofData':
        """
        Deserialize bytes to AND proof.

        Args:
            data: Bytes to deserialize
            group: The pairing group

        Returns:
            ANDProofData object
        """
        proof_dict = bytesToObject(data, group)
        return ANDProofData(
            sub_proofs=proof_dict['sub_proofs'],
            shared_challenge=proof_dict['shared_challenge'],
            proof_type=proof_dict.get('proof_type', 'and')
        )
