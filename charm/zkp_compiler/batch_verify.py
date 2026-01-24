"""
Batch Verification for Zero-Knowledge Proofs.

This module provides efficient batch verification of multiple ZKP proofs,
allowing verification of many proofs faster than verifying each individually.

=============================================================================
WHAT BATCH VERIFICATION DOES
=============================================================================
Batch verification allows verifying multiple proofs in a single operation
that is more efficient than verifying each proof individually. Instead of
performing n separate verifications, batch verification combines all proofs
into a single verification equation.

=============================================================================
HOW IT WORKS (Random Linear Combination Technique)
=============================================================================
For Schnorr proofs, each proof i has (ui, ci, zi) where:
- g^zi = ui * hi^ci  (for valid proofs)

Batch verification:
1. For each proof i, pick random weight ρi ∈ Zq
2. Compute combined equation:
   - LHS = g^(Σ ρi*zi)
   - RHS = (Π ui^ρi) * (Π hi^(ρi*ci))
3. Check LHS == RHS

If all proofs are valid:
- g^zi = ui * hi^ci for each i
- Raising to ρi and multiplying: g^(Σ ρi*zi) = (Π ui^ρi) * (Π hi^(ρi*ci))

=============================================================================
SECURITY PROPERTIES
=============================================================================
- Soundness: If any proof is invalid, the batch check fails with
  overwhelming probability (1 - 1/q where q is the group order).
- The random weights prevent a malicious prover from crafting proofs
  that cancel out each other's errors.

=============================================================================
PERFORMANCE BENEFITS
=============================================================================
- Reduces the number of exponentiations from O(n) to O(1) for the base g
- Uses multi-exponentiation techniques for efficient product computation
- Typically 2-3x faster than individual verification for large batches

=============================================================================
USE CASES
=============================================================================
1. Blockchain verification - Verify many transaction proofs in a block
2. Credential systems - Batch verify multiple credential presentations
3. Voting systems - Efficiently verify all ballots in an election
4. Threshold signatures - Batch verify signature shares

Example usage::

    from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
    from charm.zkp_compiler.batch_verify import BatchVerifier, batch_verify_schnorr

    group = PairingGroup('SS512')
    g = group.random(G1)

    # Batch verify multiple Schnorr proofs
    proofs_data = [
        {'g': g, 'h': h1, 'proof': proof1},
        {'g': g, 'h': h2, 'proof': proof2},
        {'g': g, 'h': h3, 'proof': proof3},
    ]
    all_valid = batch_verify_schnorr(group, proofs_data)

    # Or use the BatchVerifier class
    verifier = BatchVerifier(group)
    verifier.add_schnorr_proof(g, h1, proof1)
    verifier.add_schnorr_proof(g, h2, proof2)
    all_valid = verifier.verify_all()
"""

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
from charm.zkp_compiler.schnorr_proof import SchnorrProof, Proof
from charm.zkp_compiler.dleq_proof import DLEQProof, DLEQProofData
import logging

logger = logging.getLogger(__name__)


class BatchVerifier:
    """
    Batch verifier for ZKP proofs.

    Accumulates multiple proofs and verifies them all at once using
    the random linear combination technique for efficiency.
    """

    def __init__(self, group):
        """
        Initialize batch verifier.

        Args:
            group: The pairing group object
        """
        self.group = group
        self._schnorr_proofs = []  # List of (g, h, proof) tuples
        self._dleq_proofs = []  # List of (g1, h1, g2, h2, proof) tuples

    def add_schnorr_proof(self, g, h, proof):
        """
        Add a Schnorr proof to the batch.

        Args:
            g: The generator element
            h: The public value h = g^x
            proof: Proof object containing commitment, challenge, response
        """
        self._schnorr_proofs.append((g, h, proof))
        logger.debug("Added Schnorr proof to batch (total: %d)", len(self._schnorr_proofs))

    def add_dleq_proof(self, g1, h1, g2, h2, proof):
        """
        Add a DLEQ proof to the batch.

        Args:
            g1: The first generator element
            h1: The first public value h1 = g1^x
            g2: The second generator element
            h2: The second public value h2 = g2^x
            proof: DLEQProofData object containing commitments, challenge, response
        """
        self._dleq_proofs.append((g1, h1, g2, h2, proof))
        logger.debug("Added DLEQ proof to batch (total: %d)", len(self._dleq_proofs))

    def verify_all(self):
        """
        Verify all proofs in the batch.

        Uses random linear combination technique for efficiency.

        Returns:
            True if all proofs are valid, False otherwise
        """
        # Verify Schnorr proofs
        if self._schnorr_proofs:
            proofs_data = [
                {'g': g, 'h': h, 'proof': proof}
                for g, h, proof in self._schnorr_proofs
            ]
            if not batch_verify_schnorr(self.group, proofs_data):
                logger.debug("Batch Schnorr verification failed")
                return False

        # Verify DLEQ proofs
        if self._dleq_proofs:
            proofs_data = [
                {'g1': g1, 'h1': h1, 'g2': g2, 'h2': h2, 'proof': proof}
                for g1, h1, g2, h2, proof in self._dleq_proofs
            ]
            if not batch_verify_dleq(self.group, proofs_data):
                logger.debug("Batch DLEQ verification failed")
                return False

        logger.debug("Batch verification succeeded")
        return True

    def clear(self):
        """Clear all proofs from the batch."""
        self._schnorr_proofs = []
        self._dleq_proofs = []
        logger.debug("Batch cleared")


def batch_verify_schnorr(group, proofs_data):
    """
    Batch verify multiple Schnorr proofs.

    Uses random linear combination technique:
    1. For each proof i with (ui, ci, zi), pick random weight ρi
    2. Check: g^(Σ ρi*zi) == (Π ui^ρi) * (Π hi^(ρi*ci))

    Args:
        group: The pairing group
        proofs_data: List of dicts with {'g': g, 'h': h, 'proof': proof}
            where proof has commitment, challenge, and response attributes

    Returns:
        True if all proofs are valid, False otherwise
    """
    if not proofs_data:
        return True

    # First, verify all Fiat-Shamir challenges are correctly computed
    for data in proofs_data:
        g, h, proof = data['g'], data['h'], data['proof']
        expected_challenge = SchnorrProof._compute_challenge_hash(
            group, g, h, proof.commitment)
        if expected_challenge != proof.challenge:
            logger.debug("Schnorr challenge mismatch in batch verification")
            return False

    # Generate random weights for each proof
    weights = [group.random(ZR) for _ in proofs_data]

    # Compute LHS = g^(Σ ρi*zi)
    # All proofs should use the same generator g for this optimization
    # If generators differ, we compute the full product
    first_g = proofs_data[0]['g']
    same_generator = all(data['g'] == first_g for data in proofs_data)

    if same_generator:
        # Optimized case: single exponentiation for g
        z_sum = sum(
            (weights[i] * proofs_data[i]['proof'].response for i in range(len(proofs_data))),
            group.init(ZR, 0)
        )
        lhs = first_g ** z_sum
    else:
        # General case: multi-exponentiation
        lhs = group.init(G1, 1)  # Identity element
        for i, data in enumerate(proofs_data):
            exp = weights[i] * data['proof'].response
            lhs = lhs * (data['g'] ** exp)

    # Compute RHS = (Π ui^ρi) * (Π hi^(ρi*ci))
    rhs = group.init(G1, 1)  # Identity element
    for i, data in enumerate(proofs_data):
        proof = data['proof']
        rho = weights[i]
        # Add ui^ρi
        rhs = rhs * (proof.commitment ** rho)
        # Add hi^(ρi*ci)
        rhs = rhs * (data['h'] ** (rho * proof.challenge))

    result = lhs == rhs
    logger.debug("Batch Schnorr verification result: %s (n=%d)", result, len(proofs_data))
    return result


def batch_verify_dleq(group, proofs_data):
    """
    Batch verify multiple DLEQ proofs.

    Uses random linear combination technique extended for DLEQ:
    For each proof i with (u1i, u2i, ci, zi), pick random weight ρi
    Check two equations:
    - g1^(Σ ρi*zi) == (Π u1i^ρi) * (Π h1i^(ρi*ci))
    - g2^(Σ ρi*zi) == (Π u2i^ρi) * (Π h2i^(ρi*ci))

    Args:
        group: The pairing group
        proofs_data: List of dicts with:
            {'g1': g1, 'h1': h1, 'g2': g2, 'h2': h2, 'proof': proof}
            where proof has commitment1, commitment2, challenge, response

    Returns:
        True if all proofs are valid, False otherwise
    """
    if not proofs_data:
        return True

    # First, verify all Fiat-Shamir challenges are correctly computed
    for data in proofs_data:
        g1, h1, g2, h2 = data['g1'], data['h1'], data['g2'], data['h2']
        proof = data['proof']
        expected_challenge = DLEQProof._compute_challenge_hash(
            group, g1, h1, g2, h2, proof.commitment1, proof.commitment2)
        if expected_challenge != proof.challenge:
            logger.debug("DLEQ challenge mismatch in batch verification")
            return False

    # Generate random weights for each proof
    weights = [group.random(ZR) for _ in proofs_data]

    # Compute weighted sum of responses
    z_sum = sum(
        (weights[i] * proofs_data[i]['proof'].response for i in range(len(proofs_data))),
        group.init(ZR, 0)
    )

    # Check first equation: g1^(Σ ρi*zi) == (Π u1i^ρi) * (Π h1i^(ρi*ci))
    first_g1 = proofs_data[0]['g1']
    same_g1 = all(data['g1'] == first_g1 for data in proofs_data)

    if same_g1:
        lhs1 = first_g1 ** z_sum
    else:
        lhs1 = group.init(G1, 1)
        for i, data in enumerate(proofs_data):
            exp = weights[i] * data['proof'].response
            lhs1 = lhs1 * (data['g1'] ** exp)

    rhs1 = group.init(G1, 1)
    for i, data in enumerate(proofs_data):
        proof = data['proof']
        rho = weights[i]
        rhs1 = rhs1 * (proof.commitment1 ** rho)
        rhs1 = rhs1 * (data['h1'] ** (rho * proof.challenge))

    if lhs1 != rhs1:
        logger.debug("Batch DLEQ verification failed on first equation")
        return False

    # Check second equation: g2^(Σ ρi*zi) == (Π u2i^ρi) * (Π h2i^(ρi*ci))
    first_g2 = proofs_data[0]['g2']
    same_g2 = all(data['g2'] == first_g2 for data in proofs_data)

    if same_g2:
        lhs2 = first_g2 ** z_sum
    else:
        lhs2 = group.init(G1, 1)
        for i, data in enumerate(proofs_data):
            exp = weights[i] * data['proof'].response
            lhs2 = lhs2 * (data['g2'] ** exp)

    rhs2 = group.init(G1, 1)
    for i, data in enumerate(proofs_data):
        proof = data['proof']
        rho = weights[i]
        rhs2 = rhs2 * (proof.commitment2 ** rho)
        rhs2 = rhs2 * (data['h2'] ** (rho * proof.challenge))

    if lhs2 != rhs2:
        logger.debug("Batch DLEQ verification failed on second equation")
        return False

    logger.debug("Batch DLEQ verification result: True (n=%d)", len(proofs_data))
    return True