'''
MPC Utility Functions for Charm

Common utilities for multi-party computation protocols including:
- Byte/integer conversion with consistent big-endian ordering
- Bit decomposition and reconstruction for OT-based protocols
- Pedersen commitment scheme for hiding commitments

:Authors: Elton de Souza
:Date:    01/2026
'''

from charm.toolbox.ecgroup import ECGroup, ZR, G
from typing import List, Tuple, Any, Optional

# Type aliases
ZRElement = Any
GElement = Any
ECGroupType = Any


def int_to_bytes(n: int, length: int) -> bytes:
    """
    Convert a non-negative integer to a fixed-length byte string.

    Uses big-endian byte ordering (most significant byte first),
    which is standard for cryptographic protocols.

    Parameters
    ----------
    n : int
        Non-negative integer to convert. Must fit within `length` bytes.
    length : int
        Exact number of bytes in the output. Value is zero-padded if needed.

    Returns
    -------
    bytes
        Big-endian representation of `n` with exactly `length` bytes.

    Raises
    ------
    OverflowError
        If `n` is too large to fit in `length` bytes.
    ValueError
        If `n` is negative.

    Examples
    --------
    >>> int_to_bytes(256, 2)
    b'\\x01\\x00'
    >>> int_to_bytes(0, 4)
    b'\\x00\\x00\\x00\\x00'
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    return n.to_bytes(length, byteorder='big')


def bytes_to_int(b: bytes) -> int:
    """
    Convert a byte string to a non-negative integer.

    Uses big-endian byte ordering (most significant byte first),
    which is standard for cryptographic protocols.

    Parameters
    ----------
    b : bytes
        Byte string to convert.

    Returns
    -------
    int
        The integer value represented by the bytes.

    Examples
    --------
    >>> bytes_to_int(b'\\x01\\x00')
    256
    >>> bytes_to_int(b'\\x00\\x00\\x00\\x00')
    0
    """
    return int.from_bytes(b, byteorder='big')


def bit_decompose(value: Any, order: int, num_bits: int) -> List[int]:
    """
    Decompose a field element into its bit representation.

    The input value is first reduced modulo order to ensure consistent
    behavior for values at or near the group order boundary.

    Parameters
    ----------
    value : ZR element or int
        The value to decompose (will be reduced mod order)
    order : int
        The group order
    num_bits : int
        Number of bits to extract

    Returns
    -------
    list of int
        List of bits (0 or 1), LSB first

    Examples
    --------
    >>> bit_decompose(5, 2**256, 4)
    [1, 0, 1, 0]
    >>> bit_decompose(0, 2**256, 4)
    [0, 0, 0, 0]
    """
    if hasattr(value, '__int__'):
        v = int(value) % order
    else:
        v = int(str(value)) % order

    bits = []
    for i in range(num_bits):
        bits.append((v >> i) & 1)
    return bits


def bits_to_int(bits: List[int], order: int) -> int:
    """
    Reconstruct an integer from its bit representation, reduced mod order.

    This is the inverse of bit_decompose. The result is always reduced
    modulo the group order to ensure values stay in the valid field range.

    Parameters
    ----------
    bits : list of int
        List of bits (0 or 1), LSB first
    order : int
        The group order

    Returns
    -------
    int
        The reconstructed integer, reduced mod order

    Examples
    --------
    >>> bits_to_int([1, 0, 1, 0], 2**256)
    5
    >>> bits_to_int([0, 0, 0, 0], 2**256)
    0
    """
    result = 0
    for i, bit in enumerate(bits):
        if bit:
            result += (1 << i)
    return result % order


class PedersenCommitment:
    """
    Pedersen Commitment Scheme for Elliptic Curve Groups.

    Implements the information-theoretically hiding commitment scheme:
    C = g^value * h^randomness

    where g and h are generators with unknown discrete log relationship.

    Properties:
    - Computationally binding (under DLP assumption)
    - Information-theoretically hiding
    - Additively homomorphic

    Parameters
    ----------
    group : ECGroup
        An elliptic curve group object
    g : GElement, optional
        First generator (random if not provided)
    h : GElement, optional
        Second generator (random if not provided)

    Examples
    --------
    >>> from charm.toolbox.eccurve import secp256k1
    >>> from charm.toolbox.ecgroup import ECGroup, ZR
    >>> group = ECGroup(secp256k1)
    >>> pc = PedersenCommitment(group)
    >>> pc.setup()
    >>> value = group.random(ZR)
    >>> c, r = pc.commit(value)
    >>> pc.open(c, value, r)
    True
    """

    def __init__(self, group: ECGroup, g: Optional[GElement] = None,
                 h: Optional[GElement] = None):
        if group is None:
            raise ValueError("group cannot be None")
        self.group = group
        self.order = int(group.order())
        self._g = g
        self._h = h

    def setup(self) -> Tuple[GElement, GElement]:
        """Generate random generators if not already set."""
        if self._g is None:
            self._g = self.group.random(G)
        if self._h is None:
            self._h = self.group.random(G)
        return self._g, self._h

    @property
    def g(self) -> GElement:
        """First generator."""
        if self._g is None:
            raise RuntimeError("Call setup() first")
        return self._g

    @property
    def h(self) -> GElement:
        """Second generator."""
        if self._h is None:
            raise RuntimeError("Call setup() first")
        return self._h

    def commit(self, value: Any, randomness: Optional[ZRElement] = None
               ) -> Tuple[GElement, ZRElement]:
        """
        Create Pedersen commitment: C = g^value * h^randomness.

        Parameters
        ----------
        value : ZRElement or int
            Value to commit to
        randomness : ZRElement, optional
            Randomness for commitment (generated if not provided)

        Returns
        -------
        tuple
            (commitment, randomness)
        """
        if randomness is None:
            randomness = self.group.random(ZR)

        if isinstance(value, int):
            value = self.group.init(ZR, value % self.order)

        commitment = (self.g ** value) * (self.h ** randomness)
        return commitment, randomness

    def open(self, commitment: GElement, value: Any,
             randomness: ZRElement) -> bool:
        """
        Verify that a commitment opens to the given value.

        Parameters
        ----------
        commitment : GElement
            The commitment to verify
        value : ZRElement or int
            The claimed value
        randomness : ZRElement
            The randomness used in commitment

        Returns
        -------
        bool
            True if commitment opens correctly
        """
        if isinstance(value, int):
            value = self.group.init(ZR, value % self.order)

        expected = (self.g ** value) * (self.h ** randomness)
        return commitment == expected

    def add(self, c1: GElement, c2: GElement) -> GElement:
        """
        Homomorphically add two commitments.

        If c1 = Commit(v1, r1) and c2 = Commit(v2, r2),
        then c1 * c2 = Commit(v1 + v2, r1 + r2).

        Parameters
        ----------
        c1 : GElement
            First commitment
        c2 : GElement
            Second commitment

        Returns
        -------
        GElement
            Combined commitment
        """
        return c1 * c2
