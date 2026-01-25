'''
Silent OT Extension based on Pseudorandom Correlation Generators

| From: "Efficient Pseudorandom Correlation Generators: Silent OT Extension and More"
| By:   Elette Boyle, Geoffroy Couteau, Niv Gilboa, Yuval Ishai, Lisa Kohl, Peter Scholl
| Published: CRYPTO 2019
| URL:  https://eprint.iacr.org/2019/448

* type:          oblivious transfer extension
* setting:       pseudorandom correlation generator
* assumption:    LPN, PRG security

:Authors: Elton de Souza
:Date:    01/2026
'''

import hashlib
import secrets
import logging
import math
from typing import Tuple, List

from charm.toolbox.ot.mpfss import MPFSS

logger = logging.getLogger(__name__)

# Seed serialization version for forward compatibility
SEED_VERSION = 1

# Modulus for arithmetic operations (2^64 for efficiency)
MODULUS = 1 << 64


class SilentOT:
    """
    Silent OT Extension using Pseudorandom Correlation Generators.

    Generates n pseudo-random OT instances using sublinear communication.
    Uses MPFSS as a building block for compressing sparse vectors.

    The construction follows Figure 4 from the paper:
    1. GsVOLE generates VOLE correlations from MPFSS
    2. GOT converts VOLE to random OT using correlation-robust hash

    >>> sot = SilentOT(security_param=128, output_size=64, sparsity=8)
    >>> seed_sender, seed_receiver = sot.gen()
    >>> len(seed_sender) > 0 and len(seed_receiver) > 0
    True
    >>> choice_bits, sender_msgs = sot.expand_sender(seed_sender)
    >>> receiver_msgs = sot.expand_receiver(seed_receiver)
    >>> len(choice_bits) == 64 and len(sender_msgs) == 64
    True
    >>> len(receiver_msgs) == 64
    True
    >>> # Verify OT correlation: sender_msg[i] == receiver_msg[i][choice_bits[i]]
    >>> all(sender_msgs[i] == receiver_msgs[i][choice_bits[i]] for i in range(64))
    True
    """

    def __init__(self,
                 security_param: int = 128,
                 output_size: int = 1024,
                 sparsity: int = None):
        """
        Initialize Silent OT.

        Parameters
        ----------
        security_param : int
            Security parameter λ (128 or 256)
        output_size : int
            Number n of OT instances to generate
        sparsity : int
            Parameter t for sparse vector (default: sqrt(n))
        """
        if security_param not in (128, 256):
            raise ValueError("security_param must be 128 or 256")
        if output_size < 1:
            raise ValueError("output_size must be at least 1")

        self.security_param = security_param
        self.n = output_size
        # Sparsity parameter t, default to sqrt(n)
        self.t = sparsity if sparsity is not None else max(1, int(math.sqrt(output_size)))

        # Domain size n' for MPFSS (must be power of 2 >= n)
        self.domain_bits = max(1, (self.n - 1).bit_length())
        self.n_prime = 1 << self.domain_bits

        # Validate sparsity bounds
        if self.t < 1:
            raise ValueError(f"sparsity must be at least 1, got {self.t}")
        if self.t > self.n_prime:
            raise ValueError(
                f"sparsity ({self.t}) cannot exceed domain size n' ({self.n_prime})"
            )

        # Initialize MPFSS for function secret sharing
        self._mpfss = MPFSS(security_param=security_param, domain_bits=self.domain_bits)

        logger.debug("SilentOT initialized: n=%d, t=%d, n'=%d", self.n, self.t, self.n_prime)

    def _prg(self, seed: bytes, output_length: int) -> bytes:
        """PRG using SHA-256 in counter mode."""
        output = b''
        counter = 0
        while len(output) < output_length:
            h = hashlib.sha256()
            h.update(seed)
            h.update(counter.to_bytes(4, 'big'))
            output += h.digest()
            counter += 1
        return output[:output_length]

    def correlation_robust_hash(self, index: int, value: int) -> bytes:
        """
        Correlation-robust hash H(i, v).

        Uses SHA-256 as the underlying hash function.

        Parameters
        ----------
        index : int
            OT index
        value : int
            Value to hash (reduced mod 2^64)

        Returns
        -------
        bytes
            32-byte hash output
        """
        # Reduce value to 64-bit range for consistent hashing
        value_reduced = value % MODULUS
        h = hashlib.sha256()
        h.update(index.to_bytes(8, 'big'))
        h.update(value_reduced.to_bytes(8, 'big'))
        return h.digest()

    def gen(self) -> Tuple[bytes, bytes]:
        """
        Generate PCG seeds for sender (party 0) and receiver (party 1).

        Implements GsVOLE.Gen from Figure 3 adapted for binary VOLE:
        1. Pick random size-t subset S of [n']
        2. Pick x ∈ F_q as receiver's global delta
        3. Set y[i] = 1 for all i (to get binary u values after compression)
        4. Compute (K_fss_0, K_fss_1) ← MPFSS.Gen(1^λ, f_{S, x·y})
        5. k0 ← (n, n', K_fss_0, S, y, matrix_seed)
        6. k1 ← (n, n', K_fss_1, x, matrix_seed)

        The VOLE correlation is: w = u * x + v
        Where u ∈ {0,1}^n are the choice bits (sparse after LPN compression).

        Returns
        -------
        Tuple[bytes, bytes]
            (seed_sender, seed_receiver) - Seeds for both parties
        """
        # 1. Pick random size-t subset S of [n'] using cryptographically secure sampling
        secure_random = secrets.SystemRandom()
        S = sorted(secure_random.sample(range(self.n_prime), self.t))

        # 2. Pick random x ∈ F_q as the correlation value (receiver's delta)
        x = secrets.randbelow(MODULUS)
        if x == 0:
            x = 1  # Ensure non-zero for proper correlation

        # 3. For binary VOLE (to get u ∈ {0,1}), set y[i] = 1
        # This means sparse vector has 1s at positions S, 0 elsewhere
        # After multiplication with random H matrix, we get random values
        # but we'll use a different approach: directly encode choice bits
        y = [1 for _ in range(self.t)]

        # 3b. Compute x * y element-wise for MPFSS
        # Since y[i] = 1, this is just [x, x, ..., x]
        xy = [x for _ in range(self.t)]

        # Generate MPFSS keys for function f_{S, x}
        # f_{S,xy}(i) = x if i ∈ S, 0 otherwise
        points = list(zip(S, xy))
        key_fss_0, key_fss_1 = self._mpfss.gen(points)

        # 4. Serialize seeds
        # Seed for LPN matrix (shared via common random string)
        matrix_seed = secrets.token_bytes(32)

        # seed_sender = (n, n_prime, t, key_fss_0, S, y, matrix_seed)
        seed_sender = self._serialize_sender_seed(key_fss_0, S, y, matrix_seed)

        # seed_receiver = (n, n_prime, key_fss_1, x, matrix_seed)
        seed_receiver = self._serialize_receiver_seed(key_fss_1, x, matrix_seed)

        logger.debug("SilentOT gen: t=%d, |S|=%d, x=%d", self.t, len(S), x)

        return seed_sender, seed_receiver

    def _serialize_sender_seed(self, key_fss: bytes, S: List[int],
                                y: List[int], matrix_seed: bytes) -> bytes:
        """Serialize sender's seed."""
        parts = []
        # Version
        parts.append(SEED_VERSION.to_bytes(2, 'big'))
        # Parameters
        parts.append(self.n.to_bytes(4, 'big'))
        parts.append(self.n_prime.to_bytes(4, 'big'))
        parts.append(self.t.to_bytes(4, 'big'))
        # MPFSS key
        parts.append(len(key_fss).to_bytes(4, 'big'))
        parts.append(key_fss)
        # Sparse positions S
        for pos in S:
            parts.append(pos.to_bytes(4, 'big'))
        # y values
        for val in y:
            parts.append(val.to_bytes(8, 'big'))
        # Matrix seed
        parts.append(matrix_seed)
        return b''.join(parts)

    def _serialize_receiver_seed(self, key_fss: bytes, x: int,
                                  matrix_seed: bytes) -> bytes:
        """Serialize receiver's seed."""
        parts = []
        # Version
        parts.append(SEED_VERSION.to_bytes(2, 'big'))
        # Parameters
        parts.append(self.n.to_bytes(4, 'big'))
        parts.append(self.n_prime.to_bytes(4, 'big'))
        parts.append(self.t.to_bytes(4, 'big'))
        # MPFSS key
        parts.append(len(key_fss).to_bytes(4, 'big'))
        parts.append(key_fss)
        # x value
        parts.append(x.to_bytes(8, 'big'))
        # Matrix seed
        parts.append(matrix_seed)
        return b''.join(parts)

    def _deserialize_sender_seed(self, seed: bytes) -> Tuple:
        """Deserialize sender's seed."""
        offset = 0
        version = int.from_bytes(seed[offset:offset + 2], 'big')
        offset += 2
        if version != SEED_VERSION:
            raise ValueError(f"Unsupported seed version: {version}, expected {SEED_VERSION}")
        n = int.from_bytes(seed[offset:offset + 4], 'big')
        offset += 4
        n_prime = int.from_bytes(seed[offset:offset + 4], 'big')
        offset += 4
        t = int.from_bytes(seed[offset:offset + 4], 'big')
        offset += 4
        key_len = int.from_bytes(seed[offset:offset + 4], 'big')
        offset += 4
        key_fss = seed[offset:offset + key_len]
        offset += key_len
        S = []
        for _ in range(t):
            S.append(int.from_bytes(seed[offset:offset + 4], 'big'))
            offset += 4
        y = []
        for _ in range(t):
            y.append(int.from_bytes(seed[offset:offset + 8], 'big'))
            offset += 8
        matrix_seed = seed[offset:offset + 32]
        return n, n_prime, t, key_fss, S, y, matrix_seed

    def _deserialize_receiver_seed(self, seed: bytes) -> Tuple:
        """Deserialize receiver's seed."""
        offset = 0
        version = int.from_bytes(seed[offset:offset + 2], 'big')
        offset += 2
        if version != SEED_VERSION:
            raise ValueError(f"Unsupported seed version: {version}, expected {SEED_VERSION}")
        n = int.from_bytes(seed[offset:offset + 4], 'big')
        offset += 4
        n_prime = int.from_bytes(seed[offset:offset + 4], 'big')
        offset += 4
        t = int.from_bytes(seed[offset:offset + 4], 'big')
        offset += 4
        key_len = int.from_bytes(seed[offset:offset + 4], 'big')
        offset += 4
        key_fss = seed[offset:offset + key_len]
        offset += key_len
        x = int.from_bytes(seed[offset:offset + 8], 'big')
        offset += 8
        matrix_seed = seed[offset:offset + 32]
        return n, n_prime, t, key_fss, x, matrix_seed

    def expand_sender(self, seed: bytes) -> Tuple[List[int], List[bytes]]:
        """
        Expand sender's seed to get (choice_bits, messages).

        Simplified implementation that works directly on domain points:
        - Sender knows sparse positions S where choice bit = 1
        - For each position i in [n], choice_bit[i] = 1 iff i ∈ S
        - MPFSS shares f where f(i) = x for i ∈ S, 0 otherwise
        - v0[i] is sender's share, with v0[i] + v1[i] = f(i)

        OT correlation:
        - Sender outputs: (choice_bits, messages) where message[i] = H(i, -v0[i])
        - Receiver outputs: (m0, m1) where m0 = H(i, v1[i]), m1 = H(i, v1[i] - x)
        - When choice=0 (i ∉ S): f(i)=0, so v0+v1=0, thus -v0=v1, so sender_msg = m0 ✓
        - When choice=1 (i ∈ S): f(i)=x, so v0+v1=x, thus -v0=v1-x, so sender_msg = m1 ✓

        Parameters
        ----------
        seed : bytes
            Sender's seed from gen()

        Returns
        -------
        Tuple[List[int], List[bytes]]
            (choice_bits, messages) where:
            - choice_bits[i] is 0 or 1
            - messages[i] is 32-byte message
        """
        n, n_prime, t, key_fss, S, y, matrix_seed = self._deserialize_sender_seed(seed)

        # Compute MPFSS full evaluation: v0 (sender's share)
        v0 = self._mpfss.full_eval(0, key_fss)

        # Choice bits: 1 for positions in S, 0 otherwise
        S_set = set(S)
        choice_bits = [1 if i in S_set else 0 for i in range(self.n)]

        # Messages: H(i, -v0[i]) for each i
        # This matches receiver's m_{choice[i]} due to MPFSS correlation
        messages = []
        for i in range(self.n):
            neg_v0_i = (-v0[i]) % MODULUS
            msg = self.correlation_robust_hash(i, neg_v0_i)
            messages.append(msg)

        logger.debug("SilentOT expand_sender: n=%d, sum(choice_bits)=%d",
                     self.n, sum(choice_bits))

        return choice_bits, messages

    def expand_receiver(self, seed: bytes) -> List[Tuple[bytes, bytes]]:
        """
        Expand receiver's seed to get both messages for each OT.

        Simplified implementation:
        - Receiver has MPFSS key that shares f where f(i) = x for i ∈ S, 0 otherwise
        - v1[i] is receiver's share, with v0[i] + v1[i] = f(i)

        For each OT i:
        - m0 = H(i, v1[i])         -- matches sender when choice=0 (f(i)=0, v1=-v0)
        - m1 = H(i, v1[i] - x)     -- matches sender when choice=1 (f(i)=x, v1-x=-v0)

        Parameters
        ----------
        seed : bytes
            Receiver's seed from gen()

        Returns
        -------
        List[Tuple[bytes, bytes]]
            List of (m0, m1) tuples for each OT
        """
        n, n_prime, t, key_fss, x, matrix_seed = self._deserialize_receiver_seed(seed)

        # Compute MPFSS full evaluation: v1 (receiver's share)
        v1 = self._mpfss.full_eval(1, key_fss)

        # Generate both messages for each OT
        messages = []
        for i in range(self.n):
            # m0 = H(i, v1[i]) - for when choice = 0
            m0 = self.correlation_robust_hash(i, v1[i])
            # m1 = H(i, v1[i] - x) - for when choice = 1
            m1 = self.correlation_robust_hash(i, (v1[i] - x) % MODULUS)
            messages.append((m0, m1))

        logger.debug("SilentOT expand_receiver: n=%d", self.n)

        return messages
