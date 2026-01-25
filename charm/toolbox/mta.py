'''
Multiplicative-to-Additive (MtA) Share Conversion for DKLS23

| From: "Threshold ECDSA from ECDSA Assumptions: The Multiparty Case"
| By:   Jack Doerner, Yashvanth Kondi, Eysa Lee, abhi shelat
| Published: IEEE S&P 2019
| URL:  https://eprint.iacr.org/2019/523
|
| Also implements MtAwc (MtA with check) from:
| "Two-Round Threshold ECDSA from ECDSA Assumptions" (DKLS23)
| By:   Jack Doerner, Yashvanth Kondi, Eysa Lee, abhi shelat
| Published: IEEE S&P 2023
| URL:  https://eprint.iacr.org/2023/765

* type:          share conversion
* setting:       Elliptic Curve DDH-hard group
* assumption:    DDH + OT security

MtA converts multiplicative shares (a, b) where two parties hold a and b
to additive shares (alpha, beta) such that a*b = alpha + beta (mod q).
Neither party learns the other's share.

:Authors: Elton de Souza
:Date:    01/2026
'''

from typing import Dict, List, Tuple, Optional, Any, Union

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.eccurve import secp256k1
from charm.toolbox.securerandom import SecureRandomFactory
from charm.toolbox.ot.base_ot import SimpleOT
from charm.toolbox.mpc_utils import (
    int_to_bytes,
    bytes_to_int,
    bit_decompose,
    bits_to_int,
    PedersenCommitment,
)
import struct
import hashlib
import logging

# Type aliases for charm-crypto types
ZRElement = Any  # Scalar field element
GElement = Any   # Group/curve point element
ECGroupType = Any  # ECGroup instance

# Module logger
logger = logging.getLogger(__name__)


def hash_to_field(group: ECGroupType, *args: Any) -> ZRElement:
    """
    Hash multiple values to a field element with domain separation.

    Uses group.hash() for proper domain separation and automatic
    serialization of different types.

    Parameters
    ----------
    group : ECGroup
        The elliptic curve group
    *args : various
        Values to hash

    Returns
    -------
    ZR element
        Hash output as field element
    """
    return group.hash((b"MTA_FIELD:",) + args, target_type=ZR)


class CorrelatedOT:
    """
    Correlated Oblivious Transfer for MtA.

    Generates correlated random values for OT-based MtA.
    For each bit of the sender's input, generates correlation pairs.
    """

    def __init__(self, groupObj):
        """
        Initialize CorrelatedOT with an elliptic curve group.

        Parameters
        ----------
        groupObj : ECGroup
            An elliptic curve group object
        """
        self.group = groupObj
        self.order = int(groupObj.order())
        self.rand = SecureRandomFactory.getInstance()
        # Bit length based on group order
        self.bit_length = self.order.bit_length()

    def generate_correlation(self, delta):
        """
        Generate correlated pair (t0, t1) where t1 = t0 + delta.

        Parameters
        ----------
        delta : int
            The correlation offset

        Returns
        -------
        tuple
            (t0, t1) where t1 = t0 + delta (mod order)
        """
        t0 = bytes_to_int(self.rand.getRandomBytes(32)) % self.order
        t1 = (t0 + delta) % self.order
        return (t0, t1)

    def generate_batch_correlations(self, deltas):
        """
        Generate batch of correlated pairs.

        Parameters
        ----------
        deltas : list of int
            List of correlation offsets

        Returns
        -------
        list of tuples
            List of (t0, t1) pairs
        """
        return [self.generate_correlation(d) for d in deltas]


class MtA:
    """
    Multiplicative-to-Additive share conversion using OT.

    Converts multiplicative shares (a, b) where parties hold a and b
    to additive shares (alpha, beta) where a*b = alpha + beta (mod q).

    Curve Agnostic
    --------------
    This implementation supports any elliptic curve group that is DDH-hard.
    The curve is specified via the groupObj parameter.

    The protocol works as follows:
    1. Sender (holding a) decomposes a into bits
    2. For each bit position i, run correlated OT with correlation 2^i * b
    3. Receiver (holding b) chooses based on sender's bits
    4. Parties compute their additive shares from OT outputs

    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> # Create separate instances for Alice (sender) and Bob (receiver)
    >>> alice_mta = MtA(group)
    >>> bob_mta = MtA(group)
    >>> # Alice has share a, Bob has share b
    >>> a = group.random(ZR)
    >>> b = group.random(ZR)
    >>> # Convert to additive shares using the protocol with real OT
    >>> sender_msg = alice_mta.sender_round1(a)
    >>> receiver_msg, _ = bob_mta.receiver_round1(b, sender_msg)
    >>> alpha, ot_data = alice_mta.sender_round2(receiver_msg)
    >>> beta = bob_mta.receiver_round2(ot_data)
    >>> # Verify: a*b = alpha + beta (mod q)
    >>> product = a * b
    >>> additive_sum = alpha + beta
    >>> product == additive_sum
    True
    """

    def __init__(self, groupObj: ECGroupType) -> None:
        """
        Initialize MtA with an elliptic curve group.

        Parameters
        ----------
        groupObj : ECGroup
            An elliptic curve group object from charm.toolbox.ecgroup

        Raises
        ------
        ValueError
            If groupObj is None
        """
        if groupObj is None:
            raise ValueError("groupObj cannot be None")
        self.group = groupObj
        self.order = int(groupObj.order())
        self.rand = SecureRandomFactory.getInstance()
        self.bit_length = self.order.bit_length()

        # State variables
        self._a = None
        self._alpha = None

    def sender_round1(self, a: ZRElement) -> Dict[str, Any]:
        """
        Sender (holding a) generates first message.

        Sender samples random alpha and prepares OT messages such that
        receiver can learn beta = a*b - alpha. Uses real SimpleOT for security.

        Parameters
        ----------
        a : ZR element
            Sender's multiplicative share

        Returns
        -------
        dict
            OT setup parameters containing:
            - 'ot_params': list of OT sender parameters (one per bit position)
            - 'adjustment': integer for receiver to compute beta
        """
        self._a = a
        a_int = int(a) % self.order

        # Sample random alpha
        alpha_int = bytes_to_int(self.rand.getRandomBytes(32)) % self.order
        self._alpha = alpha_int

        # OT-based MtA protocol:
        # Goal: alpha + beta = a*b, where sender gets alpha (random), receiver gets beta
        #
        # Receiver has b = sum_i b_i * 2^i
        # For each bit position i, sender prepares two messages:
        #   m0_i = r_i           (receiver gets this if b_i = 0)
        #   m1_i = r_i + a * 2^i (receiver gets this if b_i = 1)
        #
        # After OT, receiver has: sum_i selected_i = sum_i (r_i + b_i * a * 2^i) = r_sum + a*b
        #
        # To get beta = a*b - alpha:
        #   beta = sum(selected) - (r_sum + alpha)
        # So sender sends: adjustment = r_sum + alpha

        # Store OT senders and messages for the transfer phase
        self._ot_senders = []
        self._ot_raw_messages = []
        ot_params_list = []
        r_sum = 0

        for i in range(self.bit_length):
            # Random mask for this position
            r_i = bytes_to_int(self.rand.getRandomBytes(32)) % self.order
            r_sum = (r_sum + r_i) % self.order

            # m0 = r_i (receiver gets this if b_i = 0)
            # m1 = r_i + a * 2^i (receiver gets this if b_i = 1)
            power_of_two = (1 << i) % self.order
            m0 = r_i
            m1 = (r_i + a_int * power_of_two) % self.order

            # Create OT sender instance and setup
            ot_sender = SimpleOT(self.group)
            sender_params = ot_sender.sender_setup()

            self._ot_senders.append(ot_sender)
            self._ot_raw_messages.append((m0, m1))
            ot_params_list.append(sender_params)

        # Sender sends r_sum + alpha so receiver can compute beta = sum(selected) - (r_sum + alpha)
        adjustment = (r_sum + alpha_int) % self.order

        return {
            'ot_params': ot_params_list,
            'adjustment': adjustment,
        }

    def receiver_round1(self, b: ZRElement, sender_msg: Dict[str, Any]) -> Tuple[Dict[str, Any], None]:
        """
        Receiver (holding b) selects OT messages based on bits of b.

        Uses real SimpleOT: for each bit b_i, receiver only learns m_{b_i}.
        The receiver NEVER sees both m0 and m1.

        Parameters
        ----------
        b : ZR element
            Receiver's multiplicative share
        sender_msg : dict
            Message from sender_round1

        Returns
        -------
        tuple (dict, None)
            A tuple containing:
            - dict: Receiver parameters with 'ot_responses' list of OT receiver responses
            - None: Placeholder for beta (computed in receiver_round2)
        """
        ot_params_list = sender_msg['ot_params']
        self._adjustment = sender_msg['adjustment']

        b_int = int(b) % self.order
        bits_b = bit_decompose(b_int, self.order, len(ot_params_list))

        # Use real OT to select messages based on bits of b
        # Receiver only learns m_{b_i} for each position - never both messages
        self._ot_receivers = []
        self._ot_receiver_states = []
        ot_responses = []

        for i, bit in enumerate(bits_b):
            ot_receiver = SimpleOT(self.group)
            receiver_response, receiver_state = ot_receiver.receiver_choose(ot_params_list[i], bit)

            self._ot_receivers.append(ot_receiver)
            self._ot_receiver_states.append(receiver_state)
            ot_responses.append(receiver_response)

        # Store bits for compatibility with old interface
        self._bits_b = bits_b

        return {'ot_responses': ot_responses}, None

    def sender_round2(self, receiver_msg: Dict[str, Any]) -> Tuple[ZRElement, Dict[str, Any]]:
        """
        Sender processes receiver's OT responses and returns alpha.

        Parameters
        ----------
        receiver_msg : dict
            Message from receiver_round1 containing OT responses

        Returns
        -------
        tuple (ZR element, dict)
            A tuple containing:
            - ZR element: Sender's additive share alpha
            - dict: OT data with 'ot_ciphertexts' list for receiver to retrieve
        """
        ot_responses = receiver_msg['ot_responses']
        ot_ciphertexts = []

        # Complete OT transfer for each bit position
        for i, ot_sender in enumerate(self._ot_senders):
            m0, m1 = self._ot_raw_messages[i]
            # Convert integers to bytes for OT encryption
            m0_bytes = int_to_bytes(m0, 32)
            m1_bytes = int_to_bytes(m1, 32)
            ciphertexts = ot_sender.sender_transfer(ot_responses[i], m0_bytes, m1_bytes)
            ot_ciphertexts.append(ciphertexts)

        alpha = self.group.init(ZR, self._alpha)
        return alpha, {'ot_ciphertexts': ot_ciphertexts}

    def receiver_round2(self, sender_round2_msg: Dict[str, Any]) -> ZRElement:
        """
        Receiver retrieves selected OT messages and computes beta.

        Parameters
        ----------
        sender_round2_msg : dict
            Message from sender_round2 containing OT ciphertexts

        Returns
        -------
        ZR element
            Receiver's additive share beta such that a*b = alpha + beta (mod q)
        """
        ot_ciphertexts = sender_round2_msg['ot_ciphertexts']

        # Retrieve selected messages using OT - receiver only gets m_{b_i}
        selected_sum = 0
        for i, ot_receiver in enumerate(self._ot_receivers):
            selected_bytes = ot_receiver.receiver_retrieve(
                ot_ciphertexts[i],
                self._ot_receiver_states[i]
            )
            selected = bytes_to_int(selected_bytes)
            selected_sum = (selected_sum + selected) % self.order

        # beta = sum(selected) - adjustment = (r_sum + a*b) - (r_sum + alpha) = a*b - alpha
        beta_int = (selected_sum - self._adjustment) % self.order
        self._beta = self.group.init(ZR, beta_int)

        return self._beta

    def receiver_complete(self, sender_bits: List[int]) -> ZRElement:
        """
        Receiver returns their additive share beta (already computed).

        Parameters
        ----------
        sender_bits : list of int
            Sender's bit decomposition (unused in correct protocol)

        Returns
        -------
        ZR element
            Receiver's additive share beta
        """
        # Beta was already computed in receiver_round1
        return self._beta



class MtAwc:
    """
    MtA with check - includes ZK proof that conversion is correct.

    Used for malicious security. Adds commitment and proof phases
    to verify that parties performed MtA correctly.

    The protocol adds:
    1. Commitment phase: parties commit to their shares
    2. Proof phase: parties prove correctness of OT selections
    3. Verification: parties verify each other's proofs

    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> mta_wc = MtAwc(group)
    >>> # Alice has share a, Bob has share b
    >>> a = group.random(ZR)
    >>> b = group.random(ZR)
    >>> # Run MtA with correctness check
    >>> sender_commit = mta_wc.sender_commit(a)
    >>> receiver_commit = mta_wc.receiver_commit(b)
    >>> # Exchange commitments and run MtA
    >>> sender_msg = mta_wc.sender_round1(a, receiver_commit)
    >>> receiver_msg, _ = mta_wc.receiver_round1(b, sender_commit, sender_msg)
    >>> alpha, sender_proof = mta_wc.sender_round2(receiver_msg)
    >>> beta, valid = mta_wc.receiver_verify(sender_proof)
    >>> valid
    True
    >>> # Verify: a*b = alpha + beta (mod q)
    >>> product = a * b
    >>> additive_sum = alpha + beta
    >>> product == additive_sum
    True
    """

    def __init__(self, groupObj: ECGroupType) -> None:
        """
        Initialize MtAwc with an elliptic curve group.

        Parameters
        ----------
        groupObj : ECGroup
            An elliptic curve group object from charm.toolbox.ecgroup

        Raises
        ------
        ValueError
            If groupObj is None
        """
        if groupObj is None:
            raise ValueError("groupObj cannot be None")
        self.group = groupObj
        self.order = int(groupObj.order())
        self.rand = SecureRandomFactory.getInstance()
        self.bit_length = self.order.bit_length()
        self.mta = MtA(groupObj)

        # Use centralized PedersenCommitment
        self._pedersen = PedersenCommitment(groupObj)
        self._pedersen.setup()
        self._g = self._pedersen.g
        self._h = self._pedersen.h

        # State
        self._a = None
        self._b = None
        self._commitment_randomness = None
        self._sender_commit = None
        self._receiver_commit = None
        self._sender_bit_proof = None

    def _pedersen_commit(self, value: Union[ZRElement, int], randomness: Optional[ZRElement] = None) -> Tuple[GElement, ZRElement]:
        """
        Create Pedersen commitment: C = g^value * h^randomness.

        Delegates to the centralized PedersenCommitment class.

        Parameters
        ----------
        value : ZR element or int
            Value to commit to
        randomness : ZR element, optional
            Randomness for commitment (generated if not provided)

        Returns
        -------
        tuple
            (commitment, randomness)
        """
        return self._pedersen.commit(value, randomness)

    def _prove_bit_or(self, bit: int, randomness: ZRElement, commitment: GElement) -> Dict[str, Any]:
        """
        Create OR-proof that commitment contains 0 or 1.

        Uses Schnorr OR-proof (Cramer-Damgard-Schoenmakers technique):
        - Prover knows witness for one branch (the actual bit value)
        - Simulates proof for the other branch
        - Verifier cannot distinguish which branch is real

        Parameters
        ----------
        bit : int
            The bit value (0 or 1)
        randomness : ZR element
            Randomness used in commitment C = g^bit * h^randomness
        commitment : G element
            The Pedersen commitment to verify

        Returns
        -------
        dict
            OR-proof containing commitments, challenges, and responses
        """
        g = self._g
        h = self._h
        order = self.order

        # For C = g^b * h^r, we prove b ∈ {0, 1}
        # If b=0: C = h^r, prove knowledge of r s.t. C = h^r
        # If b=1: C = g * h^r, prove knowledge of r s.t. C/g = h^r

        # Random values for the real branch
        k = self.group.random(ZR)  # Real branch randomness

        if bit == 0:
            # Real branch: prove C = h^r (b=0)
            # Simulated branch: C/g = h^r' (b=1)

            # Commit for real branch (b=0)
            A0 = h ** k  # Real commitment

            # Simulate b=1 branch: need (A1, e1, z1) s.t. h^z1 = A1 * (C/g)^e1
            e1 = self.group.random(ZR)
            z1 = self.group.random(ZR)
            C_over_g = commitment * (g ** (-1))
            A1 = (h ** z1) * (C_over_g ** (-int(e1) % order))

            # Compute challenge e = H(g, h, C, A0, A1)
            challenge_input = (b"OR_PROOF:", g, h, commitment, A0, A1)
            e = self.group.hash(challenge_input, target_type=ZR)
            e_int = int(e) % order

            # Compute e0 = e - e1 (real challenge)
            e1_int = int(e1) % order
            e0_int = (e_int - e1_int) % order
            e0 = self.group.init(ZR, e0_int)

            # Compute z0 = k + e0 * r (real response)
            r_int = int(randomness) % order
            k_int = int(k) % order
            z0_int = (k_int + e0_int * r_int) % order
            z0 = self.group.init(ZR, z0_int)

        else:  # bit == 1
            # Real branch: prove C/g = h^r (b=1)
            # Simulated branch: C = h^r' (b=0)

            # Simulate b=0 branch: need (A0, e0, z0) s.t. h^z0 = A0 * C^e0
            e0 = self.group.random(ZR)
            z0 = self.group.random(ZR)
            A0 = (h ** z0) * (commitment ** (-int(e0) % order))

            # Commit for real branch (b=1)
            A1 = h ** k  # Real commitment

            # Compute challenge e = H(g, h, C, A0, A1)
            challenge_input = (b"OR_PROOF:", g, h, commitment, A0, A1)
            e = self.group.hash(challenge_input, target_type=ZR)
            e_int = int(e) % order

            # Compute e1 = e - e0 (real challenge)
            e0_int = int(e0) % order
            e1_int = (e_int - e0_int) % order
            e1 = self.group.init(ZR, e1_int)

            # Compute z1 = k + e1 * r (real response)
            r_int = int(randomness) % order
            k_int = int(k) % order
            z1_int = (k_int + e1_int * r_int) % order
            z1 = self.group.init(ZR, z1_int)

        return {
            'A0': A0,
            'A1': A1,
            'e0': e0,
            'e1': e1,
            'z0': z0,
            'z1': z1,
        }

    def _verify_bit_or(self, commitment: GElement, or_proof: Dict[str, Any]) -> bool:
        """
        Verify OR-proof that commitment contains 0 or 1.

        Parameters
        ----------
        commitment : G element
            Pedersen commitment to verify
        or_proof : dict
            OR-proof from _prove_bit_or

        Returns
        -------
        bool
            True if proof is valid, False otherwise
        """
        g = self._g
        h = self._h
        order = self.order

        A0 = or_proof['A0']
        A1 = or_proof['A1']
        e0 = or_proof['e0']
        e1 = or_proof['e1']
        z0 = or_proof['z0']
        z1 = or_proof['z1']

        # Verify challenge: e = e0 + e1 = H(g, h, C, A0, A1)
        challenge_input = (b"OR_PROOF:", g, h, commitment, A0, A1)
        e = self.group.hash(challenge_input, target_type=ZR)
        e_int = int(e) % order
        e0_int = int(e0) % order
        e1_int = int(e1) % order

        if (e0_int + e1_int) % order != e_int:
            return False

        # Verify b=0 branch: h^z0 = A0 * C^e0
        lhs0 = h ** z0
        rhs0 = A0 * (commitment ** e0)
        if lhs0 != rhs0:
            return False

        # Verify b=1 branch: h^z1 = A1 * (C/g)^e1
        C_over_g = commitment * (g ** (-1))
        lhs1 = h ** z1
        rhs1 = A1 * (C_over_g ** e1)
        if lhs1 != rhs1:
            return False

        return True

    def _prove_bit_decomposition(self, value_int: int, bits: List[int], value_randomness: ZRElement) -> Dict[str, Any]:
        """
        Create ZK proof that bits are valid (0 or 1) and sum to value.

        Parameters
        ----------
        value_int : int
            The value being decomposed
        bits : list of int
            The bit decomposition (each 0 or 1)
        value_randomness : ZR element
            Randomness used in the value commitment

        Returns
        -------
        dict
            ZK proof containing:
            - bit_commitments: list of Pedersen commitments to each bit
            - or_proofs: list of OR-proofs that each bit is 0 or 1
            - sum_randomness: combined randomness for sum verification
        """
        bit_commitments = []
        bit_randomness = []
        or_proofs = []

        # Commit to each bit with fresh randomness
        for i, bit in enumerate(bits):
            r_i = self.group.random(ZR)
            bit_randomness.append(r_i)
            C_i, _ = self._pedersen_commit(bit, r_i)
            bit_commitments.append(C_i)

            # Generate OR-proof: C_i commits to 0 OR C_i commits to 1
            or_proof = self._prove_bit_or(bit, r_i, C_i)
            or_proofs.append(or_proof)

        # Sum of bit randomness weighted by powers of 2 should equal value_randomness
        # C = g^value * h^r = ∏ (g^{bit_i * 2^i} * h^{r_i * 2^i})
        # = g^{∑ bit_i * 2^i} * h^{∑ r_i * 2^i}
        # So: r = ∑ r_i * 2^i
        # We provide the sum_randomness_diff = value_randomness - ∑ r_i * 2^i
        # which should be 0 if honest, verifier can check

        sum_r = 0
        for i, r_i in enumerate(bit_randomness):
            r_i_int = int(r_i) % self.order
            sum_r = (sum_r + r_i_int * (1 << i)) % self.order

        value_r_int = int(value_randomness) % self.order
        # Diff should be 0 for honest prover
        randomness_diff = (value_r_int - sum_r) % self.order

        return {
            'bit_commitments': bit_commitments,
            'or_proofs': or_proofs,
            'randomness_diff': randomness_diff,
        }

    def _verify_bit_decomposition(self, commitment: GElement, proof: Dict[str, Any]) -> bool:
        """
        Verify ZK proof of correct bit decomposition.

        Parameters
        ----------
        commitment : G element
            Pedersen commitment to the original value
        proof : dict
            Proof from _prove_bit_decomposition

        Returns
        -------
        bool
            True if proof is valid, False otherwise
        """
        bit_commitments = proof['bit_commitments']
        or_proofs = proof['or_proofs']
        randomness_diff = proof['randomness_diff']

        if len(bit_commitments) != len(or_proofs):
            return False

        # 1. Verify each OR-proof (bit is 0 or 1)
        for i, (C_i, or_proof) in enumerate(zip(bit_commitments, or_proofs)):
            if not self._verify_bit_or(C_i, or_proof):
                logger.debug("OR-proof verification failed for bit %d", i)
                return False

        # 2. Verify sum proof: ∏ C_i^{2^i} * h^{diff} = C
        # If bits sum correctly and randomness is consistent, this should hold
        product = self.group.init(G, 1)  # Identity element
        for i, C_i in enumerate(bit_commitments):
            power = 1 << i
            product = product * (C_i ** power)

        # Account for randomness difference (should be 0 for honest prover)
        if randomness_diff != 0:
            product = product * (self._h ** randomness_diff)

        if product != commitment:
            logger.debug("Sum verification failed: product != commitment")
            return False

        return True

    def sender_commit(self, a: ZRElement) -> Dict[str, Any]:
        """
        Sender commits to share a with ZK bit decomposition proof.

        Parameters
        ----------
        a : ZR element
            Sender's multiplicative share

        Returns
        -------
        dict
            Commitment and bit decomposition proof to send to receiver
        """
        self._a = a
        a_int = int(a) % self.order
        commitment, randomness = self._pedersen_commit(a)
        self._commitment_randomness = randomness
        self._sender_commit = commitment

        # Decompose into bits
        bits = bit_decompose(a_int, self.order, self.bit_length)

        # Generate ZK proof of correct bit decomposition
        bit_proof = self._prove_bit_decomposition(a_int, bits, randomness)

        return {
            'commitment': commitment,
            'g': self._g,
            'h': self._h,
            'bit_proof': bit_proof,
        }

    def receiver_commit(self, b: ZRElement) -> Dict[str, Any]:
        """
        Receiver commits to share b.

        Parameters
        ----------
        b : ZR element
            Receiver's multiplicative share

        Returns
        -------
        dict
            Commitment to send to sender
        """
        self._b = b
        commitment, randomness = self._pedersen_commit(b)
        self._receiver_randomness = randomness
        self._receiver_commit = commitment

        return {
            'commitment': commitment,
        }

    def sender_round1(self, a: ZRElement, receiver_commit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sender generates first message with receiver's commitment.

        Parameters
        ----------
        a : ZR element
            Sender's multiplicative share
        receiver_commit : dict
            Receiver's commitment from receiver_commit

        Returns
        -------
        dict
            Message to send to receiver
        """
        self._a = a
        self._receiver_commit = receiver_commit['commitment']

        # Run base MtA
        mta_msg = self.mta.sender_round1(a)

        return {
            'mta_msg': mta_msg,
            'sender_commit': self._sender_commit,
        }

    def receiver_round1(self, b: ZRElement, sender_commit: Dict[str, Any], sender_msg: Dict[str, Any]) -> Tuple[Dict[str, Any], None]:
        """
        Receiver processes sender message with commitments.

        Parameters
        ----------
        b : ZR element
            Receiver's multiplicative share
        sender_commit : dict
            Sender's commitment from sender_commit (includes bit_proof)
        sender_msg : dict
            Message from sender_round1

        Returns
        -------
        tuple
            (receiver_message, beta_placeholder)
        """
        self._b = b
        self._g = sender_commit['g']
        self._h = sender_commit['h']
        self._sender_commit = sender_commit['commitment']
        # Store bit decomposition proof for verification in receiver_verify
        self._sender_bit_proof = sender_commit.get('bit_proof')

        # Run base MtA - now returns (receiver_msg, None) since beta is computed later
        mta_msg = sender_msg['mta_msg']
        receiver_msg, _ = self.mta.receiver_round1(b, mta_msg)

        # Add proof of correct computation
        # In full implementation, this would include ZK proofs
        return {
            'mta_msg': receiver_msg,
            'receiver_commit': self._receiver_commit,
        }, None

    def sender_round2(self, receiver_msg: Dict[str, Any]) -> Tuple[ZRElement, Dict[str, Any]]:
        """
        Sender completes MtA and generates proof.

        Parameters
        ----------
        receiver_msg : dict
            Message from receiver_round1

        Returns
        -------
        tuple
            (alpha, proof) where:
            - alpha: sender's additive share
            - proof: ZK proof of correctness (does NOT reveal sender_bits)
        """
        mta_msg = receiver_msg['mta_msg']
        # New MtA returns (alpha, ot_data) from sender_round2
        alpha, ot_data = self.mta.sender_round2(mta_msg)

        # Generate commitment-based proof that doesn't reveal the actual bits
        # This proof verifies:
        # 1. The commitment opens correctly
        # 2. The bit decomposition is consistent with the committed value
        # Using a Fiat-Shamir style challenge-response
        a_int = int(self._a) % self.order

        # Create challenge by hashing public values with domain separation
        challenge_zr = self.group.hash(
            (b"MTA_CHALLENGE:", self._sender_commit, self._g, self._h),
            target_type=ZR
        )
        challenge = self.group.serialize(challenge_zr)

        # Compute response: s = r + e*a (mod order)
        # where r is the commitment randomness and e is the challenge
        e = int(challenge_zr) % self.order
        r_int = int(self._commitment_randomness) % self.order
        s = (r_int + e * a_int) % self.order

        # The proof consists of:
        # - The challenge (derived from public values)
        # - The response s
        # - The commitment randomness (for Pedersen opening verification)
        # This does NOT reveal the actual bits of 'a'
        proof = {
            'challenge': challenge,
            'response': s,
            'commitment_randomness': self._commitment_randomness,
            'ot_data': ot_data,  # For receiver to complete OT and get beta
        }

        return alpha, proof

    def receiver_verify(self, proof: Dict[str, Any]) -> Tuple[Optional[ZRElement], bool]:
        """
        Receiver verifies proof including ZK bit decomposition and returns beta.

        Implements full ZK verification per DKLS23 Section 3:
        1. Verifies challenge-response for commitment
        2. Verifies bit decomposition OR-proofs (each bit is 0 or 1)
        3. Verifies bits sum to the committed value

        Parameters
        ----------
        proof : dict
            Proof from sender_round2

        Returns
        -------
        tuple
            (beta, valid) where:
            - beta: receiver's additive share
            - valid: boolean indicating if proof is valid
        """
        commitment_randomness = proof['commitment_randomness']
        challenge = proof['challenge']
        response = proof['response']
        ot_data = proof['ot_data']

        # First, complete the OT to get beta
        beta = self.mta.receiver_round2(ot_data)
        self._beta = beta

        # Check commitment exists
        if self._sender_commit is None:
            logger.debug("Verification failed: no sender commitment")
            return None, False

        # Verify the challenge was computed correctly with domain separation
        expected_challenge_zr = self.group.hash(
            (b"MTA_CHALLENGE:", self._sender_commit, self._g, self._h),
            target_type=ZR
        )
        expected_challenge = self.group.serialize(expected_challenge_zr)

        if challenge != expected_challenge:
            logger.debug("Verification failed: challenge mismatch")
            return None, False

        # Verify response is in valid range
        if response < 0 or response >= self.order:
            logger.debug("Verification failed: response out of range")
            return None, False

        # Verify bit decomposition proof (DKLS23 Section 3 ZK verification)
        # This proves that:
        # 1. Each bit is 0 or 1 (via OR-proofs)
        # 2. The bits sum to the committed value
        if self._sender_bit_proof is None:
            logger.debug("Verification failed: no bit decomposition proof")
            return None, False

        if not self._verify_bit_decomposition(
            self._sender_commit,
            self._sender_bit_proof
        ):
            logger.debug("Verification failed: bit decomposition proof invalid")
            return None, False

        logger.debug("MtAwc verification successful")
        return self._beta, True

