'''
Distributed Point Function (DPF) based on GGM Construction

| From: "Function Secret Sharing: Improvements and Extensions"
| By:   Elette Boyle, Niv Gilboa, Yuval Ishai
| Published: CCS 2016
| URL:  https://eprint.iacr.org/2018/707
|
| Also based on GGM PRF construction from:
| "How to Construct Random Functions" - Goldreich, Goldwasser, Micali (JACM 1986)
| URL:  https://people.csail.mit.edu/silvio/Selected%20Scientific%20Papers/Pseudo%20Randomness/How%20To%20Construct%20Random%20Functions.pdf

* type:          function secret sharing
* setting:       symmetric key
* assumption:    PRG security

:Authors: Elton de Souza
:Date:    01/2026
'''

import hashlib
import logging
from typing import Tuple, List

# Module logger
logger = logging.getLogger(__name__)

# Key serialization version
KEY_VERSION = 1


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """
    XOR two byte strings of equal length.

    Parameters
    ----------
    a : bytes
        First byte string
    b : bytes
        Second byte string

    Returns
    -------
    bytes
        XOR of the two byte strings

    >>> xor_bytes(b'\\x00\\xff', b'\\xff\\x00')
    b'\\xff\\xff'
    >>> xor_bytes(b'\\xab\\xcd', b'\\xab\\xcd')
    b'\\x00\\x00'
    """
    assert len(a) == len(b), f"xor_bytes: operands differ in length ({len(a)} vs {len(b)})"
    return bytes(x ^ y for x, y in zip(a, b))


class DPF:
    """
    Distributed Point Function (DPF) based on GGM PRF construction.

    A DPF allows secret-sharing a point function f_{α,β}(x) = β if x=α else 0
    between two parties, such that:
    - Neither party learns α or β individually
    - The sum of both evaluations equals f_{α,β}(x)

    The construction uses a GGM-style binary tree with a length-doubling PRG.
    Key size is O(λ * log n) for domain size n.

    >>> dpf = DPF(security_param=128, domain_bits=8)
    >>> # Create point function f(5) = 42, f(x) = 0 for x != 5
    >>> k0, k1 = dpf.gen(alpha=5, beta=42)
    >>> # Evaluate at target point - sum should equal beta
    >>> y0 = dpf.eval(0, k0, 5)
    >>> y1 = dpf.eval(1, k1, 5)
    >>> (y0 + y1) % (2**64)
    42
    >>> # Evaluate at non-target point - sum should equal 0
    >>> z0 = dpf.eval(0, k0, 7)
    >>> z1 = dpf.eval(1, k1, 7)
    >>> (z0 + z1) % (2**64)
    0

    Security Limitations
    --------------------
    WARNING: This implementation is NOT constant-time and is vulnerable to
    timing attacks. This implementation is suitable for research and educational
    purposes only.
    """

    def __init__(self, security_param: int = 128, domain_bits: int = 20):
        """
        Initialize DPF with security parameter and domain size.

        Parameters
        ----------
        security_param : int
            Security parameter in bits (default: 128)
        domain_bits : int
            Domain size is 2^domain_bits (default: 20, giving 1M points)
        """
        if security_param not in (128, 256):
            raise ValueError("security_param must be 128 or 256")
        if domain_bits < 1 or domain_bits > 32:
            raise ValueError("domain_bits must be between 1 and 32")

        self.lambda_bytes = security_param // 8  # 16 bytes for 128-bit security
        self.n = domain_bits  # log2 of domain size
        self.domain_size = 1 << domain_bits  # 2^n

        logger.debug("DPF initialized: lambda=%d bits, domain=2^%d", security_param, domain_bits)

    def prg(self, seed: bytes) -> Tuple[bytes, bytes]:
        """
        Length-doubling PRG using SHA-256.

        Expands a λ-bit seed to (2λ + 2) bits by hashing with domain separators.
        Returns two seeds (each λ bits) and extracts 2 control bits.

        Parameters
        ----------
        seed : bytes
            Input seed of lambda_bytes length

        Returns
        -------
        tuple
            ((left_seed, left_bit), (right_seed, right_bit)) where:
            - left_seed, right_seed are bytes of lambda_bytes length
            - left_bit, right_bit are control bits (0 or 1)

        >>> dpf = DPF(security_param=128, domain_bits=8)
        >>> seed = b'\\x00' * 16
        >>> (left, left_bit), (right, right_bit) = dpf.prg(seed)
        >>> len(left) == 16 and len(right) == 16
        True
        >>> left_bit in (0, 1) and right_bit in (0, 1)
        True
        """
        assert len(seed) == self.lambda_bytes, f"Seed must be {self.lambda_bytes} bytes"

        # Hash with domain separator for left child
        h_left = hashlib.sha256()
        h_left.update(b'\x00')  # domain separator for left
        h_left.update(seed)
        left_output = h_left.digest()

        # Hash with domain separator for right child
        h_right = hashlib.sha256()
        h_right.update(b'\x01')  # domain separator for right
        h_right.update(seed)
        right_output = h_right.digest()

        # Extract seeds and control bits
        left_seed = left_output[:self.lambda_bytes]
        left_bit = left_output[self.lambda_bytes] & 1

        right_seed = right_output[:self.lambda_bytes]
        right_bit = right_output[self.lambda_bytes] & 1

        return (left_seed, left_bit), (right_seed, right_bit)

    def _get_bit(self, x: int, level: int) -> int:
        """
        Get bit at position level from MSB of x.

        Parameters
        ----------
        x : int
            The value to extract bit from
        level : int
            The bit position (0 is MSB for n-bit value)

        Returns
        -------
        int
            0 or 1
        """
        return (x >> (self.n - 1 - level)) & 1

    def _convert_output(self, seed: bytes) -> int:
        """
        Convert a seed to an integer output value.

        Parameters
        ----------
        seed : bytes
            Seed bytes

        Returns
        -------
        int
            64-bit integer value
        """
        # Hash the seed and take first 8 bytes as output
        h = hashlib.sha256()
        h.update(b'\x02')  # domain separator for output conversion
        h.update(seed)
        return int.from_bytes(h.digest()[:8], 'big')

    def gen(self, alpha: int, beta: int) -> Tuple[bytes, bytes]:
        """
        Generate DPF keys for point function f_{α,β}.

        Creates keys (k0, k1) such that:
        - eval(0, k0, x) + eval(1, k1, x) = β if x = α
        - eval(0, k0, x) + eval(1, k1, x) = 0 if x ≠ α

        The algorithm walks down the GGM tree from root to leaf α,
        generating correction words at each level to "fix" the off-path
        sibling values.

        Parameters
        ----------
        alpha : int
            The target point (must be in [0, 2^n))
        beta : int
            The output value at target point

        Returns
        -------
        tuple
            (k0, k1) where each key is a bytes object containing:
            - Initial seed (λ bytes)
            - Initial control bit (1 byte)
            - Correction words (n * (2λ + 2) bytes)
            - Final correction word (8 bytes for 64-bit output)

        Raises
        ------
        ValueError
            If alpha is out of range

        >>> dpf = DPF(security_param=128, domain_bits=4)
        >>> k0, k1 = dpf.gen(alpha=3, beta=100)
        >>> len(k0) > 0 and len(k1) > 0
        True
        """
        if not (0 <= alpha < self.domain_size):
            raise ValueError(f"alpha must be in [0, {self.domain_size})")

        import os

        # Sample random initial seeds for both parties
        s0 = os.urandom(self.lambda_bytes)
        s1 = os.urandom(self.lambda_bytes)

        # Initial control bits: t0 = 0, t1 = 1 (parties start different)
        t0 = 0
        t1 = 1

        # Store correction words
        correction_words = []

        # Current seeds and control bits along the path to alpha
        s0_curr, s1_curr = s0, s1
        t0_curr, t1_curr = t0, t1

        logger.debug("DPF gen: alpha=%d, beta=%d, n=%d", alpha, beta, self.n)

        # Walk down tree from root to leaf alpha
        for level in range(self.n):
            # Get direction at this level (0=left, 1=right)
            alpha_bit = self._get_bit(alpha, level)

            # Expand both current seeds
            (s0_left, t0_left), (s0_right, t0_right) = self.prg(s0_curr)
            (s1_left, t1_left), (s1_right, t1_right) = self.prg(s1_curr)

            # The correction word should make the "lose" (off-path) children
            # have equal seeds s0_lose' = s1_lose' and equal control bits t0_lose' = t1_lose'
            # The "keep" (on-path) children should maintain t0_keep' XOR t1_keep' = 1

            # s_cw = s0_lose XOR s1_lose (so after XOR both have same value)
            if alpha_bit == 0:
                # Keep left, lose right
                s_cw_left = xor_bytes(s0_left, s1_left)
                s_cw_right = xor_bytes(s0_right, s1_right)
            else:
                # Keep right, lose left
                s_cw_left = xor_bytes(s0_left, s1_left)
                s_cw_right = xor_bytes(s0_right, s1_right)

            # For control bit correction:
            # After applying CW (based on t_curr), we want:
            # - On "lose" path: t0' XOR t1' = 0 (both same, so output cancels)
            # - On "keep" path: t0' XOR t1' = 1 (different, maintains invariant)
            #
            # Let L = alpha_bit (1 if going left is "lose")
            # t_new = t_old XOR (t_curr * t_cw)
            #
            # For lose side (L=1 means left is keep, 1-L means left is lose):
            # t0_lose' XOR t1_lose' = (t0_lose XOR t0_curr*t_cw) XOR (t1_lose XOR t1_curr*t_cw)
            #                       = t0_lose XOR t1_lose XOR (t0_curr XOR t1_curr)*t_cw
            # Since t0_curr XOR t1_curr = 1, we need t_cw = t0_lose XOR t1_lose for them to equal.
            #
            # For keep side:
            # Similarly, t_cw_keep = t0_keep XOR t1_keep XOR 1

            # Correction for control bits
            # For left (keep if alpha_bit=0, lose if alpha_bit=1):
            if alpha_bit == 0:
                # left is keep: want t0_left' XOR t1_left' = 1
                t_cw_left = t0_left ^ t1_left ^ 1
                # right is lose: want t0_right' XOR t1_right' = 0
                t_cw_right = t0_right ^ t1_right
            else:
                # left is lose: want t0_left' XOR t1_left' = 0
                t_cw_left = t0_left ^ t1_left
                # right is keep: want t0_right' XOR t1_right' = 1
                t_cw_right = t0_right ^ t1_right ^ 1

            # Store correction word: (s_left, t_left, s_right, t_right)
            cw = (s_cw_left, t_cw_left, s_cw_right, t_cw_right)
            correction_words.append(cw)

            # Apply correction based on control bit and compute new seeds
            # Party 0's new values
            s0_left_new = s0_left
            t0_left_new = t0_left
            s0_right_new = s0_right
            t0_right_new = t0_right
            if t0_curr == 1:
                s0_left_new = xor_bytes(s0_left, s_cw_left)
                t0_left_new = t0_left ^ t_cw_left
                s0_right_new = xor_bytes(s0_right, s_cw_right)
                t0_right_new = t0_right ^ t_cw_right

            # Party 1's new values
            s1_left_new = s1_left
            t1_left_new = t1_left
            s1_right_new = s1_right
            t1_right_new = t1_right
            if t1_curr == 1:
                s1_left_new = xor_bytes(s1_left, s_cw_left)
                t1_left_new = t1_left ^ t_cw_left
                s1_right_new = xor_bytes(s1_right, s_cw_right)
                t1_right_new = t1_right ^ t_cw_right

            # Move to next level along path to alpha
            if alpha_bit == 0:
                s0_curr, t0_curr = s0_left_new, t0_left_new
                s1_curr, t1_curr = s1_left_new, t1_left_new
            else:
                s0_curr, t0_curr = s0_right_new, t0_right_new
                s1_curr, t1_curr = s1_right_new, t1_right_new

        # Final correction word to encode beta
        # At leaf alpha: we have t0_curr XOR t1_curr = 1
        #
        # Eval computes:
        # - Party 0's output = convert(s0) + t0 * final_cw
        # - Party 1's output = -convert(s1) - t1 * final_cw
        #
        # For off-path (s0=s1, t0=t1):
        #   Sum = convert(s) - convert(s) + t*final_cw - t*final_cw = 0 ✓
        #
        # For on-path (t0 XOR t1 = 1):
        #   If t0=0, t1=1: Sum = convert(s0) - convert(s1) - final_cw
        #     Want: convert(s0) - convert(s1) - final_cw = beta
        #     So: final_cw = out0 - out1 - beta
        #
        #   If t0=1, t1=0: Sum = convert(s0) + final_cw - convert(s1)
        #     Want: convert(s0) - convert(s1) + final_cw = beta
        #     So: final_cw = beta - out0 + out1

        out0 = self._convert_output(s0_curr)
        out1 = self._convert_output(s1_curr)

        modulus = 1 << 64
        if t0_curr == 1:
            # t0=1, t1=0: final_cw = beta - out0 + out1
            final_cw = (beta - out0 + out1) % modulus
        else:
            # t0=0, t1=1: final_cw = out0 - out1 - beta
            final_cw = (out0 - out1 - beta) % modulus

        # Serialize keys
        # Key format: seed || control_bit || CW1 || CW2 || ... || CWn || final_cw
        k0 = self._serialize_key(s0, t0, correction_words, final_cw)
        k1 = self._serialize_key(s1, t1, correction_words, final_cw)

        logger.debug("DPF gen complete: key_size=%d bytes", len(k0))

        return k0, k1

    def _serialize_key(
        self,
        seed: bytes,
        control_bit: int,
        correction_words: list,
        final_cw: int
    ) -> bytes:
        """
        Serialize a DPF key to bytes.

        Parameters
        ----------
        seed : bytes
            Initial seed
        control_bit : int
            Initial control bit (0 or 1)
        correction_words : list
            List of (s_left, t_left, s_right, t_right) tuples
        final_cw : int
            Final correction word (64-bit integer)

        Returns
        -------
        bytes
            Serialized key
        """
        parts = [KEY_VERSION.to_bytes(2, 'big'), seed, bytes([control_bit])]

        for s_left, t_left, s_right, t_right in correction_words:
            parts.append(s_left)
            parts.append(bytes([t_left]))
            parts.append(s_right)
            parts.append(bytes([t_right]))

        parts.append(final_cw.to_bytes(8, 'big'))

        return b''.join(parts)

    def _deserialize_key(self, key: bytes) -> tuple:
        """
        Deserialize a DPF key from bytes.

        Parameters
        ----------
        key : bytes
            Serialized key

        Returns
        -------
        tuple
            (seed, control_bit, correction_words, final_cw)
        """
        offset = 0

        # Read and validate version
        version = int.from_bytes(key[offset:offset + 2], 'big')
        offset += 2
        if version != KEY_VERSION:
            raise ValueError(
                f"Unsupported DPF key version {version}. Expected {KEY_VERSION}."
            )

        # Read initial seed
        seed = key[offset:offset + self.lambda_bytes]
        offset += self.lambda_bytes

        # Read initial control bit
        control_bit = key[offset]
        offset += 1

        # Read correction words
        correction_words = []
        for _ in range(self.n):
            s_left = key[offset:offset + self.lambda_bytes]
            offset += self.lambda_bytes
            t_left = key[offset]
            offset += 1
            s_right = key[offset:offset + self.lambda_bytes]
            offset += self.lambda_bytes
            t_right = key[offset]
            offset += 1
            correction_words.append((s_left, t_left, s_right, t_right))

        # Read final correction word
        final_cw = int.from_bytes(key[offset:offset + 8], 'big')

        return seed, control_bit, correction_words, final_cw

    def eval(self, sigma: int, key: bytes, x: int) -> int:
        """
        Evaluate DPF at point x with key k_sigma.

        Parameters
        ----------
        sigma : int
            Party index (0 or 1)
        key : bytes
            DPF key for party sigma
        x : int
            Point to evaluate (must be in [0, 2^n))

        Returns
        -------
        int
            The party's share of f_{α,β}(x). When combined:
            eval(0, k0, x) + eval(1, k1, x) ≡ f_{α,β}(x) (mod 2^64)

        Raises
        ------
        ValueError
            If sigma is not 0 or 1, or x is out of range

        >>> dpf = DPF(security_param=128, domain_bits=4)
        >>> k0, k1 = dpf.gen(alpha=10, beta=999)
        >>> # At target point, shares sum to beta
        >>> (dpf.eval(0, k0, 10) + dpf.eval(1, k1, 10)) % (2**64)
        999
        >>> # At other points, shares sum to 0
        >>> (dpf.eval(0, k0, 5) + dpf.eval(1, k1, 5)) % (2**64)
        0
        """
        if sigma not in (0, 1):
            raise ValueError("sigma must be 0 or 1")
        if not (0 <= x < self.domain_size):
            raise ValueError(f"x must be in [0, {self.domain_size})")

        seed, t_curr, correction_words, final_cw = self._deserialize_key(key)
        s_curr = seed

        # Walk down tree to leaf x
        for level in range(self.n):
            x_bit = self._get_bit(x, level)
            s_cw_left, t_cw_left, s_cw_right, t_cw_right = correction_words[level]

            # Expand current seed
            (s_left, t_left), (s_right, t_right) = self.prg(s_curr)

            # Apply correction word if control bit is 1
            if t_curr == 1:
                s_left = xor_bytes(s_left, s_cw_left)
                t_left ^= t_cw_left
                s_right = xor_bytes(s_right, s_cw_right)
                t_right ^= t_cw_right

            # Move to child based on x_bit
            if x_bit == 0:
                s_curr, t_curr = s_left, t_left
            else:
                s_curr, t_curr = s_right, t_right

        # Compute output share using (-1)^sigma factor for additive sharing
        # Party 0: +convert(s), Party 1: -convert(s)
        modulus = 1 << 64
        base_out = self._convert_output(s_curr)

        if sigma == 0:
            out = base_out
        else:
            out = (-base_out) % modulus

        # Apply final correction based on control bit
        # Party 0 adds, Party 1 subtracts when their control bit is 1
        # This ensures: when t0=t1=1, corrections cancel out
        if t_curr == 1:
            if sigma == 0:
                out = (out + final_cw) % modulus
            else:
                out = (out - final_cw) % modulus

        return out

    def full_eval(self, sigma: int, key: bytes) -> List[int]:
        """
        Evaluate DPF on entire domain [0, 2^n).

        This is more efficient than calling eval() for each point,
        as it reuses intermediate tree computations.

        Parameters
        ----------
        sigma : int
            Party index (0 or 1)
        key : bytes
            DPF key for party sigma

        Returns
        -------
        list
            List of shares for all domain points. When combined:
            full_eval(0, k0)[x] + full_eval(1, k1)[x] ≡ f_{α,β}(x) (mod 2^64)

        Raises
        ------
        ValueError
            If sigma is not 0 or 1

        >>> dpf = DPF(security_param=128, domain_bits=3)
        >>> k0, k1 = dpf.gen(alpha=5, beta=777)
        >>> out0 = dpf.full_eval(0, k0)
        >>> out1 = dpf.full_eval(1, k1)
        >>> # Check all positions
        >>> all((out0[i] + out1[i]) % (2**64) == (777 if i == 5 else 0) for i in range(8))
        True
        """
        if sigma not in (0, 1):
            raise ValueError("sigma must be 0 or 1")

        seed, t_init, correction_words, final_cw = self._deserialize_key(key)

        # Build tree level by level
        # Each level stores list of (seed, control_bit) pairs
        current_level = [(seed, t_init)]

        for level in range(self.n):
            s_cw_left, t_cw_left, s_cw_right, t_cw_right = correction_words[level]
            next_level = []

            for s_curr, t_curr in current_level:
                # Expand current seed
                (s_left, t_left), (s_right, t_right) = self.prg(s_curr)

                # Apply correction word if control bit is 1
                if t_curr == 1:
                    s_left = xor_bytes(s_left, s_cw_left)
                    t_left ^= t_cw_left
                    s_right = xor_bytes(s_right, s_cw_right)
                    t_right ^= t_cw_right

                next_level.append((s_left, t_left))
                next_level.append((s_right, t_right))

            current_level = next_level

        # Convert leaves to output shares using (-1)^sigma factor
        modulus = 1 << 64
        outputs = []

        for s_leaf, t_leaf in current_level:
            base_out = self._convert_output(s_leaf)

            # Party 0: +convert(s), Party 1: -convert(s)
            if sigma == 0:
                out = base_out
            else:
                out = (-base_out) % modulus

            # Apply final correction based on control bit
            # Party 0 adds, Party 1 subtracts when their control bit is 1
            if t_leaf == 1:
                if sigma == 0:
                    out = (out + final_cw) % modulus
                else:
                    out = (out - final_cw) % modulus

            outputs.append(out)

        return outputs
