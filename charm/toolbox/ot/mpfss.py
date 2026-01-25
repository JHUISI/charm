'''
Multi-Point Function Secret Sharing (MPFSS)

| From: "Efficient Pseudorandom Correlation Generators: Silent OT Extension and More"
| By:   Elette Boyle, Geoffroy Couteau, Niv Gilboa, Yuval Ishai, Lisa Kohl, Peter Scholl
| Published: CRYPTO 2019
| URL:  https://eprint.iacr.org/2019/448

* type:          function secret sharing
* setting:       symmetric key
* assumption:    PRG security

:Authors: Elton de Souza
:Date:    01/2026
'''

from typing import List, Tuple
from charm.toolbox.ot.dpf import DPF

KEY_VERSION = 1


class MPFSS:
    """
    Multi-Point Function Secret Sharing (MPFSS).

    Extends DPF to support multiple points. Shares a function f_{S,y} where S
    is a set of points and y is a vector of values. For each point α_i in S,
    f_{S,y}(α_i) = y_i, and f_{S,y}(x) = 0 for x not in S.

    This implementation uses the simple approach from the paper: run independent
    DPF for each point. Key size is O(t * λ * log n) where t is number of points,
    λ is security parameter, and n is domain size.

    The MPFSS key is constructed by composing DPF instances:
        K_{fss,σ} = (K^1_{dpf,σ}, K^2_{dpf,σ}, ..., K^t_{dpf,σ})

    The full_eval runs each DPF's full_eval and sums the outputs.

    Example
    -------
    >>> mpfss = MPFSS(security_param=128, domain_bits=10)
    >>> # Share function with points: f(5) = 100, f(20) = 200
    >>> points = [(5, 100), (20, 200)]
    >>> key0, key1 = mpfss.gen(points)
    >>> # Evaluate at specific point
    >>> v0 = mpfss.eval(0, key0, 5)
    >>> v1 = mpfss.eval(1, key1, 5)
    >>> (v0 + v1) % (2**64) == 100
    True
    >>> # Full domain evaluation sums each DPF
    >>> full0 = mpfss.full_eval(0, key0)
    >>> full1 = mpfss.full_eval(1, key1)
    >>> domain_size = 2**10
    >>> [(full0[i] + full1[i]) % (2**64) for i in [5, 20]] == [100, 200]
    True
    """

    def __init__(self, security_param: int = 128, domain_bits: int = 20):
        """
        Initialize MPFSS with security and domain parameters.

        Parameters
        ----------
        security_param : int
            Security parameter in bits (default: 128)
        domain_bits : int
            Number of bits for domain size N = 2^domain_bits (default: 20)
        """
        self.security_param = security_param
        self.domain_bits = domain_bits
        self.domain_size = 1 << domain_bits
        self._dpf = DPF(security_param=security_param, domain_bits=domain_bits)
        self._modulus = 1 << 64  # 2^64 for 64-bit arithmetic

    def gen(self, points: List[Tuple[int, int]]) -> Tuple[bytes, bytes]:
        """
        Generate MPFSS keys for a set of points.

        Generates keys that share a function f where f(α_i) = y_i for each
        (α_i, y_i) in points, and f(x) = 0 elsewhere.

        Parameters
        ----------
        points : List[Tuple[int, int]]
            List of (α, y) pairs where α is the point and y is the value

        Returns
        -------
        Tuple[bytes, bytes]
            (key0, key1) - MPFSS keys for party 0 and party 1

        Raises
        ------
        ValueError
            If any point α is outside the domain [0, 2^domain_bits)
        """
        if not points:
            # Empty function - return empty keys with proper version header
            empty_key = self._serialize_keys([])
            return empty_key, empty_key

        # Check for duplicate alpha values
        alphas = [alpha for alpha, _ in points]
        seen = set()
        duplicates = set()
        for alpha in alphas:
            if alpha in seen:
                duplicates.add(alpha)
            seen.add(alpha)
        if duplicates:
            raise ValueError(
                f"Duplicate alpha values are not allowed: {sorted(duplicates)}"
            )

        # Validate points are within domain
        for alpha, _ in points:
            if alpha < 0 or alpha >= self.domain_size:
                raise ValueError(
                    f"Point {alpha} is outside domain [0, {self.domain_size})"
                )

        # Generate independent DPF for each point
        dpf_keys_0 = []
        dpf_keys_1 = []

        for alpha, y in points:
            k0, k1 = self._dpf.gen(alpha, y)
            dpf_keys_0.append(k0)
            dpf_keys_1.append(k1)

        # Serialize: count + list of (length, key) pairs
        key0 = self._serialize_keys(dpf_keys_0)
        key1 = self._serialize_keys(dpf_keys_1)

        return key0, key1

    def _serialize_keys(self, keys: List[bytes]) -> bytes:
        """Serialize a list of DPF keys into a single bytes object."""
        # Format: 2 bytes version, 4 bytes count, then for each key: 4 bytes length + key data
        result = KEY_VERSION.to_bytes(2, 'big')
        result += len(keys).to_bytes(4, 'big')
        for key in keys:
            result += len(key).to_bytes(4, 'big')
            result += key
        return result

    def _deserialize_keys(self, data: bytes) -> List[bytes]:
        """Deserialize a bytes object into a list of DPF keys."""
        # Read and validate version (2 bytes)
        version = int.from_bytes(data[:2], 'big')
        if version != KEY_VERSION:
            raise ValueError(
                f"Unsupported key version {version}, expected {KEY_VERSION}"
            )
        count = int.from_bytes(data[2:6], 'big')
        keys = []
        offset = 6
        for _ in range(count):
            length = int.from_bytes(data[offset:offset + 4], 'big')
            offset += 4
            keys.append(data[offset:offset + length])
            offset += length
        return keys

    def eval(self, sigma: int, key: bytes, x: int) -> int:
        """
        Evaluate MPFSS at a single point.

        Parameters
        ----------
        sigma : int
            Party index (0 or 1)
        key : bytes
            MPFSS key for this party
        x : int
            Point at which to evaluate

        Returns
        -------
        int
            The share of f(x) for this party
        """
        dpf_keys = self._deserialize_keys(key)

        # Sum evaluations from all DPF instances
        total = 0
        for dpf_key in dpf_keys:
            total += self._dpf.eval(sigma, dpf_key, x)

        return total % self._modulus

    def full_eval(self, sigma: int, key: bytes) -> List[int]:
        """
        Evaluate MPFSS on the entire domain.

        Runs each DPF's full_eval and sums the outputs element-wise.

        Parameters
        ----------
        sigma : int
            Party index (0 or 1)
        key : bytes
            MPFSS key for this party

        Returns
        -------
        List[int]
            List of shares for all points in domain [0, 2^domain_bits)
        """
        dpf_keys = self._deserialize_keys(key)

        if not dpf_keys:
            # Empty function - return all zeros
            return [0] * self.domain_size

        # Initialize result with first DPF's full evaluation
        result = self._dpf.full_eval(sigma, dpf_keys[0])

        # Sum remaining DPF evaluations
        for i in range(1, len(dpf_keys)):
            dpf_eval = self._dpf.full_eval(sigma, dpf_keys[i])
            for j in range(self.domain_size):
                result[j] += dpf_eval[j]

        # Apply modular reduction to ensure 64-bit arithmetic
        return [x % self._modulus for x in result]

