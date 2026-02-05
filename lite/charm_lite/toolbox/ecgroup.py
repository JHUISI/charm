"""
ECGroup: Elliptic Curve Group abstraction for charm-crypto-lite.

This module provides a high-level interface for elliptic curve operations
using OpenSSL's EC implementation.

Example:
    from charm_lite.toolbox.ecgroup import ECGroup
    from charm_lite.toolbox.eccurve import secp256k1
    
    group = ECGroup(secp256k1)
    
    # Generate random elements
    g = group.random(G)   # Random point on curve
    x = group.random(ZR)  # Random scalar
    
    # Scalar multiplication
    h = g ** x
    
    # Hash to curve
    h = group.hash(b"message", G)
    
    # Serialization
    data = group.serialize(h)
    h2 = group.deserialize(data)
"""

try:
    from charm_lite.core.math.elliptic_curve import (
        elliptic_curve, ec_element, ZR, G, init, random, order,
        getGenerator, bitsize, serialize, deserialize, hashEC,
        encode, decode, getXY
    )
    import charm_lite.core.math.elliptic_curve as ecc
except Exception as err:
    raise ImportError(
        "Cannot import elliptic_curve module. "
        "Ensure charm-crypto-lite C extensions are compiled: %s" % err
    )

# Re-export element types for convenience
__all__ = ['ECGroup', 'ZR', 'G', 'ec_element']


class ECGroup:
    """Elliptic Curve Group for cryptographic operations."""
    
    def __init__(self, builtin_cv):
        """Initialize an EC group with a specific curve.
        
        Args:
            builtin_cv: Curve identifier (e.g., secp256k1 = 714)
        """
        self.ec_group = elliptic_curve(nid=builtin_cv)
        self.param = builtin_cv
        self._verbose = True

    def __str__(self):
        return str(self.ec_group)

    def order(self):
        """Returns the order of the group."""
        return order(self.ec_group)

    def bitsize(self):
        """Returns the bitsize for encoding messages in the group."""
        return bitsize(self.ec_group)
    
    def paramgen(self, secparam):
        return None

    def groupSetting(self):
        return 'elliptic_curve'

    def groupType(self): 
        return self.param

    def init(self, _type=ZR, value=None):
        """Initializes an element with a specified type and value."""
        if value is not None:
            return init(self.ec_group, _type, value)
        return init(self.ec_group, _type)
    
    def random(self, _type=ZR):
        """Selects a random element in ZR (scalar) or G (point)."""        
        if _type == ZR or _type == G:
            return random(self.ec_group, _type)
        return None
    
    def encode(self, message, include_ctr=False):
        """Encode arbitrary string as a group element."""
        return encode(self.ec_group, message, include_ctr)
    
    def decode(self, msg_bytes, include_ctr=False):
        """Decode a group element into a string."""
        return decode(self.ec_group, msg_bytes, include_ctr)
    
    def serialize(self, element):
        """Serializes an EC element into bytes."""        
        return serialize(element)
    
    def deserialize(self, bytes_object):
        """Deserializes bytes into an EC element."""        
        return deserialize(self.ec_group, bytes_object)

    def hash(self, args, target_type=ZR):
        """Hashes objects into ZR (scalar) or G (curve point)."""
        def hash_encode(arg):
            if type(arg) is bytes:
                s = arg
            elif type(arg) is ec_element:
                s = serialize(arg)
            elif type(arg) is str:
                s = arg.encode('utf-8')
            elif type(arg) is int:
                s = arg.to_bytes((arg.bit_length() + 7) // 8, 'little')
            elif isinstance(args, tuple):
                def left_encode(x):
                    n = (x.bit_length() + 7) // 8
                    return n.to_bytes(1, 'little') + x.to_bytes(n, 'little')
                s = b''
                for a in args:
                    z = hash_encode(a)
                    s += left_encode(len(z)) + z
            else:
                raise ValueError("unexpected type to hash: {}".format(type(arg)))
            return s

        return hashEC(self.ec_group, hash_encode(args), target_type)

    def zr(self, point):
        """Get the X coordinate only."""
        if type(point) == ec_element:
            return getXY(self.ec_group, point, False)
        return None

    def coordinates(self, point):
        """Get the X and Y coordinates of an EC point."""
        if type(point) == ec_element:
            return getXY(self.ec_group, point, True)

    # Benchmark methods
    def InitBenchmark(self):
        return ecc.InitBenchmark(self.ec_group)
    
    def StartBenchmark(self, options):
        return ecc.StartBenchmark(self.ec_group, options)
    
    def EndBenchmark(self):
        return ecc.EndBenchmark(self.ec_group)
        
    def GetGeneralBenchmarks(self):
        return ecc.GetGeneralBenchmarks(self.ec_group)
    
    def GetGranularBenchmarks(self):
        return ecc.GetGranularBenchmarks(self.ec_group)
    
    def GetBenchmark(self, option):
        return ecc.GetBenchmark(self.ec_group, option)

