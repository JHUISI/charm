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
    encode as _encode,
    decode as _decode,
    get_coeff as _get_coeff,
    set_coeff as _set_coeff,
    cbd_sample as _cbd_sample,
    compress as _compress,
    decompress as _decompress,
    poly_from_coeffs as _poly_from_coeffs,
    mat_transpose as _mat_transpose,
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
        """Encode a binary message into a polynomial (1 bit per coefficient, scaled by q/2)."""
        if isinstance(msg, str):
            msg = msg.encode('utf-8')
        return _encode(self._ctx, msg)

    def decode(self, elem, num_bytes=None):
        """Decode a polynomial back to bytes by thresholding coefficients."""
        if num_bytes is not None:
            return _decode(self._ctx, elem, num_bytes * 8)
        return _decode(self._ctx, elem)

    def get_coeff(self, elem, idx):
        """Get coefficient idx of a POLY element as a Python int."""
        return _get_coeff(self._ctx, elem, idx)

    def set_coeff(self, elem, idx, val):
        """Set coefficient idx of a POLY element."""
        return _set_coeff(self._ctx, elem, idx, val)

    def cbd_sample(self, eta):
        """Sample a polynomial from Centered Binomial Distribution(eta)."""
        return _cbd_sample(self._ctx, eta)

    def compress(self, elem, d):
        """Compress polynomial coefficients to d bits."""
        return _compress(self._ctx, elem, d)

    def decompress(self, elem, d):
        """Decompress polynomial coefficients from d bits."""
        return _decompress(self._ctx, elem, d)

    def poly_from_coeffs(self, coeffs):
        """Create a polynomial from a list of integer coefficients."""
        return _poly_from_coeffs(self._ctx, coeffs)

    def mat_transpose(self, mat):
        """Transpose a matrix element."""
        return _mat_transpose(self._ctx, mat)

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

    # =========================================================
    # RLWE Primitives
    # =========================================================

    def rlwe_keygen(self, sigma=3.0):
        """
        RLWE key generation.

        Returns (pk, sk) where:
            pk = (a, b = a*s + e)  with a uniform, s,e Gaussian
            sk = s
        """
        a = self.random(POLY)
        s = self.gaussian(sigma)
        e = self.gaussian(sigma)
        b = a * s + e
        pk = {'a': a, 'b': b}
        sk = {'s': s}
        return pk, sk

    def rlwe_encrypt(self, pk, msg_poly, sigma=3.0):
        """
        RLWE encryption.

        msg_poly: a polynomial already scaled (output of encode(), with
                  coefficients 0 or floor(q/2))

        Returns ct = (c1, c2) where:
            c1 = a*r + e1
            c2 = b*r + e2 + msg_poly
        """
        a, b = pk['a'], pk['b']
        r = self.gaussian(sigma)
        e1 = self.gaussian(sigma)
        e2 = self.gaussian(sigma)
        c1 = a * r + e1
        c2 = b * r + e2 + msg_poly
        return {'c1': c1, 'c2': c2}

    def rlwe_decrypt(self, sk, ct):
        """
        RLWE decryption.

        Returns the noisy message polynomial. Caller should threshold
        each coefficient: if closer to 0 -> 0, if closer to q/2 -> 1.
        """
        s = sk['s']
        return ct['c2'] - ct['c1'] * s

    # =========================================================
    # MLWE Primitives (for Kyber/Dilithium)
    # =========================================================

    def mlwe_keygen(self, k, sigma=3.0):
        """
        Module-LWE key generation.

        Returns (pk, sk) where:
            pk = (A, t = A*s + e)  with A uniform k×k matrix
            sk = s (vector of k polynomials)
        """
        A = self.random_mat(k, k)
        s = self.gaussian_vec(k, sigma)
        e = self.gaussian_vec(k, sigma)
        t = A * s + e
        pk = {'A': A, 't': t}
        sk = {'s': s}
        return pk, sk

    def __repr__(self):
        return f"LatticeGroup('{self._param_id}', n={self._n}, q={self._q})"
