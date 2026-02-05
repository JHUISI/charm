"""
ECGroup: Elliptic Curve Group abstraction for charm-crypto-lite.

This module provides a minimal interface for elliptic curve operations
on the secp256k1 curve using OpenSSL's EC implementation.

Supported operations:
- EC point operations (multiplicative group notation):
    * Point addition: h * k (group operation)
    * Scalar multiplication: g ** x (exponentiation)
    * Point negation: -h
    * Serialize/deserialize
- Scalar operations (additive notation):
    * Addition: x + y
    * Subtraction: x - y
    * Multiplication: x * y
    * Inversion: ~x
    * Random generation
- generator() to get the curve generator point

Example:
    from charm_lite.toolbox.ecgroup import ECGroup, ZR, G
    from charm_lite.toolbox.eccurve import secp256k1

    group = ECGroup(secp256k1)

    # Get the generator point
    g = group.generator()

    # Generate random scalar
    x = group.random(ZR)

    # Scalar multiplication: h = g^x
    h = g ** x

    # Point addition (multiplicative notation)
    k = g ** group.random(ZR)
    p = h * k

    # Point negation
    neg_h = -h

    # Scalar inversion
    x_inv = ~x

    # Serialization
    data = group.serialize(h)
    h2 = group.deserialize(data)
"""

try:
    from charm_lite.core.math.elliptic_curve import (
        elliptic_curve, ec_element, ZR, G, init, random, order,
        getGenerator, serialize, deserialize
    )
except Exception as err:
    raise ImportError(
        "Cannot import elliptic_curve module. "
        "Ensure charm-crypto-lite C extensions are compiled: %s" % err
    )

# Re-export element types for convenience
__all__ = ['ECGroup', 'ZR', 'G', 'ec_element']


class ECGroup:
    """Elliptic Curve Group for secp256k1 cryptographic operations.

    This is a minimal implementation focused on:
    - EC point operations: add, scalar multiply, negate
    - Scalar operations: add, subtract, multiply, invert
    - Serialization/deserialization
    - Random element generation
    """

    def __init__(self, curve_id):
        """Initialize an EC group with secp256k1 curve.

        Args:
            curve_id: Curve identifier (use secp256k1 = 714)
        """
        self.ec_group = elliptic_curve(nid=curve_id)
        self.param = curve_id

    def __str__(self):
        return str(self.ec_group)

    def order(self):
        """Returns the order of the group (number of points on curve)."""
        return order(self.ec_group)

    def generator(self):
        """Returns the generator point G of the curve.

        This is the standard base point for secp256k1.
        """
        return getGenerator(self.ec_group)

    def init(self, _type=ZR, value=None):
        """Initialize an element with a specified type and optional value.

        Args:
            _type: Element type - ZR (scalar) or G (point)
            value: Optional initial value (integer for ZR)

        Returns:
            New element of the specified type
        """
        if value is not None:
            return init(self.ec_group, _type, value)
        return init(self.ec_group, _type)

    def random(self, _type=ZR):
        """Generate a random element in ZR (scalar) or G (point).

        Args:
            _type: Element type - ZR for random scalar, G for random point

        Returns:
            Random element of the specified type
        """
        if _type == ZR or _type == G:
            return random(self.ec_group, _type)
        return None

    def serialize(self, element):
        """Serialize an EC element (point or scalar) to bytes.

        Args:
            element: EC element to serialize

        Returns:
            bytes representation of the element
        """
        return serialize(element)

    def deserialize(self, bytes_object):
        """Deserialize bytes back to an EC element.

        Args:
            bytes_object: Serialized element bytes

        Returns:
            Deserialized EC element
        """
        return deserialize(self.ec_group, bytes_object)

