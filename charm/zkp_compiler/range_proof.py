"""
Range Proof implementation using bit decomposition.

This module provides a Zero-Knowledge Range Proof that proves a committed
value lies within a range [0, 2^n) without revealing the value itself.

=== What This Proves ===
Given a Pedersen commitment C = g^v * h^r, the range proof proves that the
committed value v is in the range [0, 2^n) without revealing v or r.

=== Bit Decomposition Approach ===
This implementation uses bit decomposition with O(n) proof size where n is
the number of bits in the range. The approach works as follows:

1. Decompose the value v into n bits: v = b0 + 2*b1 + 4*b2 + ... + 2^(n-1)*b_{n-1}
2. For each bit bi:
   - Generate random ri
   - Create bit commitment: Ci = g^bi * h^ri
   - Create OR proof that bi ∈ {0, 1}:
     Prove (Ci = h^ri) OR (Ci = g * h^ri)
3. Prove that the weighted sum of bit commitments equals the original commitment:
   - Product of Ci^(2^i) should equal C (with appropriate randomness adjustment)

=== Security Properties ===
- Zero-Knowledge: Verifier learns nothing about v except that v ∈ [0, 2^n)
- Soundness: Prover cannot convince verifier of a false statement (except with
  negligible probability)
- Completeness: Honest prover with valid v always convinces verifier

=== Use Cases ===
1. Confidential Transactions: Prove transaction amounts are non-negative
2. Age Verification: Prove age >= 18 without revealing exact age
3. Voting: Prove vote value is in valid range (e.g., 0 or 1)
4. Auctions: Prove bid is within allowed range
5. Credit Scoring: Prove score is above threshold without revealing exact score

=== Limitations ===
This bit decomposition approach has O(n) proof size where n is the number of
bits. For logarithmic proof size, consider Bulletproofs which achieve O(log n)
proof size using inner product arguments.

Usage Example:
    >>> group = PairingGroup('BN254')
    >>> g, h = group.random(G1), group.random(G1)
    >>> 
    >>> # Prove value is in range [0, 2^8) = [0, 256)
    >>> value = 42
    >>> randomness = group.random(ZR)
    >>> commitment = RangeProof.create_pedersen_commitment(group, g, h, value, randomness)
    >>> proof = RangeProof.prove(group, g, h, value, randomness, num_bits=8)
    >>> valid = RangeProof.verify(group, g, h, commitment, proof)
    >>> assert valid
"""

from typing import Any, List, Dict

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.core.engine.util import objectToBytes, bytesToObject
import logging

logger = logging.getLogger(__name__)


class RangeProofData:
    """Container for Range Proof data.

    Holds all components of a range proof including bit commitments,
    bit proofs (OR proofs), and the sum proof.
    """

    def __init__(self, bit_commitments: List[Any], bit_proofs: List[Dict[str, Any]], sum_proof: Dict[str, Any], num_bits: int, proof_type: str = 'range') -> None:
        """
        Initialize a range proof.

        Args:
            bit_commitments: List of commitments to each bit [C0, C1, ..., C_{n-1}]
            bit_proofs: List of OR proofs proving each bit is 0 or 1
            sum_proof: Proof that sum of bits equals the committed value
            num_bits: Number of bits in the range (range is [0, 2^num_bits))
            proof_type: Type identifier for the proof
        """
        self.bit_commitments = bit_commitments
        self.bit_proofs = bit_proofs
        self.sum_proof = sum_proof
        self.num_bits = num_bits
        self.proof_type = proof_type


class RangeProof:
    """
    Zero-Knowledge Range Proof using Bit Decomposition.

    Proves that a Pedersen commitment C = g^v * h^r commits to a value v
    in the range [0, 2^n) without revealing v.

    The proof consists of:
    1. n bit commitments Ci = g^bi * h^ri
    2. n OR proofs showing each bi ∈ {0, 1}
    3. A sum proof showing that sum(2^i * bi) = v
    """

    @classmethod
    def create_pedersen_commitment(cls, group, g, h, value, randomness):
        """
        Create a Pedersen commitment C = g^v * h^r.

        Args:
            group: The pairing group
            g: First generator (for value)
            h: Second generator (for randomness)
            value: The value to commit to (integer or ZR element)
            randomness: The randomness r (ZR element)

        Returns:
            Pedersen commitment C = g^v * h^r
        """
        if isinstance(value, int):
            v = group.init(ZR, value)
        else:
            v = value
        return (g ** v) * (h ** randomness)

    @classmethod
    def _create_bit_or_proof(cls, group, g, h, bit_commitment, bit, bit_randomness):
        """
        Create simplified OR proof that bit_commitment commits to 0 or 1.

        Proves: (Ci = h^ri AND bi=0) OR (Ci = g * h^ri AND bi=1)

        This uses a simplified Sigma-OR protocol (Cramer-Damgård-Schoenmakers).
        """
        # Generate random values for the proof
        if bit == 0:
            # We know bi = 0, so Ci = h^ri
            # Real proof for branch 0, simulate branch 1
            r0 = group.random(ZR)
            a0 = h ** r0  # Real commitment for branch 0

            # Simulate branch 1 (pretend Ci = g * h^ri but we don't know ri)
            c1 = group.random(ZR)
            z1 = group.random(ZR)
            # a1 = g^z1 * h^z1 / (Ci/g)^c1 = g^z1 * h^z1 * g^c1 / Ci^c1
            Ci_over_g = bit_commitment * (g ** (-group.init(ZR, 1)))
            a1 = (h ** z1) * (Ci_over_g ** (-c1))

            # Compute overall challenge
            data = (objectToBytes(bit_commitment, group) +
                    objectToBytes(a0, group) + objectToBytes(a1, group))
            c = group.hash(data, ZR)

            # c0 = c - c1
            c0 = c - c1
            # z0 = r0 + c0 * ri
            z0 = r0 + c0 * bit_randomness
        else:
            # We know bi = 1, so Ci = g * h^ri
            # Simulate branch 0, real proof for branch 1
            c0 = group.random(ZR)
            z0 = group.random(ZR)
            # a0 = h^z0 / Ci^c0
            a0 = (h ** z0) * (bit_commitment ** (-c0))

            # Real proof for branch 1
            r1 = group.random(ZR)
            Ci_over_g = bit_commitment * (g ** (-group.init(ZR, 1)))
            a1 = h ** r1  # Real commitment for branch 1

            # Compute overall challenge
            data = (objectToBytes(bit_commitment, group) +
                    objectToBytes(a0, group) + objectToBytes(a1, group))
            c = group.hash(data, ZR)

            # c1 = c - c0
            c1 = c - c0
            # z1 = r1 + c1 * ri
            z1 = r1 + c1 * bit_randomness

        return {
            'a0': a0, 'a1': a1,
            'c0': c0, 'c1': c1,
            'z0': z0, 'z1': z1
        }

    @classmethod
    def _verify_bit_or_proof(cls, group, g, h, bit_commitment, proof):
        """
        Verify OR proof that bit_commitment commits to 0 or 1.

        Returns:
            True if proof is valid, False otherwise
        """
        a0, a1 = proof['a0'], proof['a1']
        c0, c1 = proof['c0'], proof['c1']
        z0, z1 = proof['z0'], proof['z1']

        # Recompute challenge
        data = (objectToBytes(bit_commitment, group) +
                objectToBytes(a0, group) + objectToBytes(a1, group))
        c = group.hash(data, ZR)

        # Verify c = c0 + c1
        if c != c0 + c1:
            return False

        # Verify branch 0: h^z0 == a0 * Ci^c0 (if bi = 0, Ci = h^ri)
        lhs0 = h ** z0
        rhs0 = a0 * (bit_commitment ** c0)
        if lhs0 != rhs0:
            return False

        # Verify branch 1: h^z1 == a1 * (Ci/g)^c1 (if bi = 1, Ci = g * h^ri)
        Ci_over_g = bit_commitment * (g ** (-group.init(ZR, 1)))
        lhs1 = h ** z1
        rhs1 = a1 * (Ci_over_g ** c1)
        if lhs1 != rhs1:
            return False

        return True

    @classmethod
    def prove(cls, group: PairingGroup, g: Any, h: Any, value: int, randomness: Any, num_bits: int = 32) -> 'RangeProofData':
        """
        Generate a range proof that value is in [0, 2^num_bits).

        Args:
            group: The pairing group
            g: First generator for Pedersen commitment
            h: Second generator for Pedersen commitment
            value: The secret value to prove is in range (integer)
            randomness: The randomness used in the original commitment
            num_bits: Number of bits defining the range [0, 2^num_bits)

        Returns:
            RangeProofData object containing the complete proof

        Raises:
            ValueError: If value is not in the valid range
        """
        # Validate value is in range
        if not isinstance(value, int):
            raise ValueError("Value must be an integer")
        if value < 0 or value >= (1 << num_bits):
            raise ValueError(f"Value {value} not in range [0, 2^{num_bits})")

        # Step 1: Decompose value into bits
        bits = [(value >> i) & 1 for i in range(num_bits)]

        # Step 2: Generate random values for bit commitments
        # We need: sum(2^i * ri) = r (original randomness)
        # So we pick random r0, r1, ..., r_{n-2} and compute r_{n-1}
        bit_randomness = [group.random(ZR) for _ in range(num_bits - 1)]

        # Compute last randomness so weighted sum equals original randomness
        # r = sum(2^i * ri), so r_{n-1} = (r - sum(2^i * ri for i < n-1)) / 2^{n-1}
        partial_sum = group.init(ZR, 0)
        for i in range(num_bits - 1):
            weight = group.init(ZR, 1 << i)
            partial_sum = partial_sum + weight * bit_randomness[i]

        last_weight = group.init(ZR, 1 << (num_bits - 1))
        last_randomness = (randomness - partial_sum) * (last_weight ** (-1))
        bit_randomness.append(last_randomness)

        # Step 3: Create bit commitments Ci = g^bi * h^ri
        bit_commitments = []
        for i in range(num_bits):
            bi = group.init(ZR, bits[i])
            Ci = (g ** bi) * (h ** bit_randomness[i])
            bit_commitments.append(Ci)

        # Step 4: Create OR proofs for each bit
        bit_proofs = []
        for i in range(num_bits):
            proof = cls._create_bit_or_proof(
                group, g, h, bit_commitments[i], bits[i], bit_randomness[i]
            )
            bit_proofs.append(proof)

        # Step 5: Create sum proof (commitment consistency)
        # Product of Ci^(2^i) should equal C = g^v * h^r
        # This is implicitly verified by checking bit OR proofs and the
        # commitment structure, so we include a signature/hash for binding
        sum_data = b''
        for i, Ci in enumerate(bit_commitments):
            sum_data += objectToBytes(Ci, group)
        sum_proof = {
            'binding_hash': group.hash(sum_data, ZR)
        }

        logger.debug("Generated range proof for %d bits", num_bits)
        return RangeProofData(
            bit_commitments=bit_commitments,
            bit_proofs=bit_proofs,
            sum_proof=sum_proof,
            num_bits=num_bits,
            proof_type='range'
        )

    @classmethod
    def verify(cls, group: PairingGroup, g: Any, h: Any, commitment: Any, proof: 'RangeProofData') -> bool:
        """
        Verify a range proof.

        Checks that the commitment C commits to a value in [0, 2^num_bits).

        Args:
            group: The pairing group
            g: First generator for Pedersen commitment
            h: Second generator for Pedersen commitment
            commitment: The Pedersen commitment C = g^v * h^r
            proof: RangeProofData object containing the proof

        Returns:
            True if proof is valid, False otherwise

        Security Notes:
            - Validates proof structure before verification
            - Verifies each bit commitment and OR proof
            - Checks commitment reconstruction for consistency
        """
        # Security: Validate proof structure
        required_attrs = ['num_bits', 'bit_commitments', 'bit_proofs']
        for attr in required_attrs:
            if not hasattr(proof, attr):
                logger.warning("Invalid Range proof structure: missing '%s'. Ensure proof was created with RangeProof.prove()", attr)
                return False

        num_bits = proof.num_bits

        # Validate proof structure
        if len(proof.bit_commitments) != num_bits:
            logger.debug("Invalid number of bit commitments")
            return False
        if len(proof.bit_proofs) != num_bits:
            logger.debug("Invalid number of bit proofs")
            return False

        # Step 1: Verify each bit OR proof
        for i in range(num_bits):
            if not cls._verify_bit_or_proof(
                group, g, h, proof.bit_commitments[i], proof.bit_proofs[i]
            ):
                logger.debug("Bit OR proof %d failed", i)
                return False

        # Step 2: Verify that weighted product of bit commitments equals C
        # Product of Ci^(2^i) should equal C
        # This works because: prod(Ci^(2^i)) = prod((g^bi * h^ri)^(2^i))
        #                                    = g^(sum(2^i * bi)) * h^(sum(2^i * ri))
        #                                    = g^v * h^r = C
        reconstructed = None
        for i in range(num_bits):
            weight = group.init(ZR, 1 << i)
            weighted_commitment = proof.bit_commitments[i] ** weight
            if reconstructed is None:
                reconstructed = weighted_commitment
            else:
                reconstructed = reconstructed * weighted_commitment

        if reconstructed != commitment:
            logger.debug("Commitment reconstruction failed")
            return False

        # Step 3: Verify sum proof binding hash
        sum_data = b''
        for Ci in proof.bit_commitments:
            sum_data += objectToBytes(Ci, group)
        expected_hash = group.hash(sum_data, ZR)
        if proof.sum_proof.get('binding_hash') != expected_hash:
            logger.debug("Sum proof binding hash mismatch")
            return False

        logger.debug("Range proof verification successful")
        return True

    @classmethod
    def serialize_proof(cls, proof: 'RangeProofData', group: PairingGroup) -> bytes:
        """
        Serialize proof to bytes using Charm utilities.

        Args:
            proof: RangeProofData object to serialize
            group: The pairing group

        Returns:
            Bytes representation of the proof
        """
        proof_dict = {
            'bit_commitments': proof.bit_commitments,
            'bit_proofs': proof.bit_proofs,
            'sum_proof': proof.sum_proof,
            'num_bits': proof.num_bits,
            'proof_type': proof.proof_type
        }
        return objectToBytes(proof_dict, group)

    @classmethod
    def deserialize_proof(cls, data: bytes, group: PairingGroup) -> 'RangeProofData':
        """
        Deserialize bytes to proof.

        Args:
            data: Bytes to deserialize
            group: The pairing group

        Returns:
            RangeProofData object
        """
        proof_dict = bytesToObject(data, group)
        return RangeProofData(
            bit_commitments=proof_dict['bit_commitments'],
            bit_proofs=proof_dict['bit_proofs'],
            sum_proof=proof_dict['sum_proof'],
            num_bits=proof_dict['num_bits'],
            proof_type=proof_dict.get('proof_type', 'range')
        )

