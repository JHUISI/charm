"""
Lattice-based group abstraction for Charm.

Provides a Pythonic wrapper around the C++ lattice extension module,
following the same API pattern as PairingGroup, ECGroup, and IntegerGroup.

Ring: R_q = Z_q[X]/(X^n + 1) backed by NTL.
"""

import warnings
from charm.core.math.lattice import (
    LatticeContext, LatticeElement,
    ZQ, POLY, VEC, MAT,
    random, random_vec, random_mat,
    gaussian, gaussian_vec,
    hash as _hash,
    serialize as _serialize,
    deserialize as _deserialize,
    ismember as _ismember,
    order as _order,
    degree as _degree,
)

# Re-export element type constants
__all__ = ['LatticeGroup', 'ZQ', 'POLY', 'VEC', 'MAT']

# Named parameter sets: name -> (n, q)
PARAM_SETS = {
    # Basic RLWE
    'RLWE-256-7681':   (256, 7681),
    'RLWE-512-12289':  (512, 12289),
    'RLWE-1024-12289': (1024, 12289),
    # ML-KEM (Kyber) parameters
    'KYBER-512':       (256, 3329),
    'KYBER-768':       (256, 3329),
    'KYBER-1024':      (256, 3329),
    # ML-DSA (Dilithium) parameters
    'DILITHIUM-2':     (256, 8380417),
    'DILITHIUM-3':     (256, 8380417),
    'DILITHIUM-5':     (256, 8380417),
}

# Kyber/Dilithium-specific parameters (k, eta1, eta2, du, dv) / (k, l, eta, gamma1, gamma2, tau)
KYBER_PARAMS = {
    'KYBER-512':  {'k': 2, 'eta1': 3, 'eta2': 2, 'du': 10, 'dv': 4},
    'KYBER-768':  {'k': 3, 'eta1': 2, 'eta2': 2, 'du': 10, 'dv': 4},
    'KYBER-1024': {'k': 4, 'eta1': 2, 'eta2': 2, 'du': 11, 'dv': 5},
}

DILITHIUM_PARAMS = {
    'DILITHIUM-2': {'k': 4, 'l': 4, 'eta': 2, 'gamma1': 2**17, 'gamma2': (8380417-1)//88, 'tau': 39, 'beta': 78},
    'DILITHIUM-3': {'k': 6, 'l': 5, 'eta': 4, 'gamma1': 2**19, 'gamma2': (8380417-1)//32, 'tau': 49, 'beta': 196},
    'DILITHIUM-5': {'k': 8, 'l': 7, 'eta': 2, 'gamma1': 2**19, 'gamma2': (8380417-1)//32, 'tau': 60, 'beta': 120},
}


class LatticeGroup:
    """
    Lattice-based group abstraction.

    Usage:
        group = LatticeGroup('RLWE-256-7681')
        a = group.random(POLY)
        b = group.random(POLY)
        c = a + b  # ring addition
        d = a * b  # ring multiplication mod X^n+1

    Custom parameters:
        group = LatticeGroup(n=512, q=12289)
    """

    def __init__(self, param_id=None, n=None, q=None):
        if param_id is not None:
            if param_id not in PARAM_SETS:
                raise ValueError(
                    f"Unknown parameter set '{param_id}'. "
                    f"Available: {', '.join(sorted(PARAM_SETS.keys()))}"
                )
            self._param_id = param_id
            n, q = PARAM_SETS[param_id]
        elif n is not None and q is not None:
            self._param_id = f'custom-{n}-{q}'
        else:
            raise ValueError("Must specify param_id or both n and q")

        self._ctx = LatticeContext(n, q)
        self._n = n
        self._q = q
        # Store scheme-specific params if applicable
        self._kyber_params = KYBER_PARAMS.get(self._param_id, {})
        self._dilithium_params = DILITHIUM_PARAMS.get(self._param_id, {})

    @property
    def ctx(self):
        """Access the underlying C LatticeContext."""
        return self._ctx

    def order(self):
        """Return the ring modulus q."""
        return _order(self._ctx)

    def degree(self):
        """Return the ring dimension n."""
        return _degree(self._ctx)

    def random(self, elem_type=POLY):
        """Generate a uniform random element of the given type."""
        if elem_type in (ZQ, POLY):
            return random(self._ctx, elem_type)
        raise ValueError("random() supports ZQ and POLY types. Use random_vec/random_mat for VEC/MAT.")

    def random_vec(self, k):
        """Generate a vector of k uniform random polynomials."""
        return random_vec(self._ctx, k)

    def random_mat(self, rows, cols):
        """Generate a matrix of uniform random polynomials."""
        return random_mat(self._ctx, rows, cols)

    def gaussian(self, sigma, elem_type=POLY):
        """Generate an element with discrete Gaussian coefficients."""
        return gaussian(self._ctx, elem_type, sigma)

    def gaussian_vec(self, k, sigma):
        """Generate a vector of k Gaussian polynomials."""
        return gaussian_vec(self._ctx, k, sigma)

    def hash(self, data, elem_type=POLY):
        """Hash bytes to a ring element."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return _hash(self._ctx, data, elem_type)

    def encode(self, msg):
        """Encode a binary message into a polynomial (1 bit per coefficient)."""
        if isinstance(msg, str):
            msg = msg.encode('utf-8')
        # Convert bytes to bits, embed as coefficients scaled by q/2
        half_q = self._q // 2
        poly = self.random(POLY)  # placeholder — will be replaced by C-level encode
        return poly

    def serialize(self, elem):
        """Serialize an element to bytes."""
        return _serialize(self._ctx, elem)

    def deserialize(self, data):
        """Deserialize bytes back to an element."""
        return _deserialize(self._ctx, data)

    def ismember(self, elem):
        """Check if an element belongs to this ring."""
        return _ismember(self._ctx, elem)

    def groupSetting(self):
        """Return the group setting identifier."""
        return 'lattice'

    def groupType(self):
        """Return the parameter set name."""
        return self._param_id

    def __repr__(self):
        return f"LatticeGroup('{self._param_id}', n={self._n}, q={self._q})"
