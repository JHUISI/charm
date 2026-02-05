"""
Basic tests for charm-crypto-lite wheel verification.

These tests verify that the core functionality works after installation.
"""

import pytest


def test_import_ecgroup():
    """Test that ECGroup can be imported."""
    from charm_lite.toolbox.ecgroup import ECGroup, ZR, G
    assert ECGroup is not None
    assert ZR is not None
    assert G is not None


def test_import_eccurve():
    """Test that eccurve module can be imported."""
    from charm_lite.toolbox.eccurve import secp256k1
    assert secp256k1 is not None


def test_import_pkenc():
    """Test that PKEnc base class can be imported."""
    from charm_lite.toolbox.PKEnc import PKEnc
    assert PKEnc is not None


def test_ecgroup_initialization():
    """Test ECGroup initialization with secp256k1."""
    from charm_lite.toolbox.ecgroup import ECGroup
    from charm_lite.toolbox.eccurve import secp256k1
    
    group = ECGroup(secp256k1)
    assert group is not None


def test_generator():
    """Test getting the generator point."""
    from charm_lite.toolbox.ecgroup import ECGroup
    from charm_lite.toolbox.eccurve import secp256k1
    
    group = ECGroup(secp256k1)
    g = group.generator()
    assert g is not None


def test_random_scalar():
    """Test generating random scalars."""
    from charm_lite.toolbox.ecgroup import ECGroup, ZR
    from charm_lite.toolbox.eccurve import secp256k1
    
    group = ECGroup(secp256k1)
    x = group.random(ZR)
    assert x is not None
    
    # Two random scalars should be different (with overwhelming probability)
    y = group.random(ZR)
    assert x != y


def test_scalar_multiplication():
    """Test scalar multiplication (g ** x)."""
    from charm_lite.toolbox.ecgroup import ECGroup, ZR
    from charm_lite.toolbox.eccurve import secp256k1
    
    group = ECGroup(secp256k1)
    g = group.generator()
    x = group.random(ZR)
    
    # Scalar multiplication
    pk = g ** x
    assert pk is not None
    
    # Result should be different from generator
    assert pk != g


def test_point_addition():
    """Test point addition (p1 * p2)."""
    from charm_lite.toolbox.ecgroup import ECGroup, ZR
    from charm_lite.toolbox.eccurve import secp256k1
    
    group = ECGroup(secp256k1)
    g = group.generator()
    x = group.random(ZR)
    y = group.random(ZR)
    
    p1 = g ** x
    p2 = g ** y
    
    # Point addition
    p3 = p1 * p2
    assert p3 is not None


def test_serialization():
    """Test serialization and deserialization."""
    from charm_lite.toolbox.ecgroup import ECGroup, ZR
    from charm_lite.toolbox.eccurve import secp256k1
    
    group = ECGroup(secp256k1)
    g = group.generator()
    x = group.random(ZR)
    pk = g ** x
    
    # Serialize
    data = group.serialize(pk)
    assert data is not None
    assert len(data) > 0
    
    # Deserialize
    pk2 = group.deserialize(data)
    assert pk2 is not None
    
    # Should be equal
    assert pk == pk2


def test_pkenc_subclass():
    """Test that PKEnc can be subclassed."""
    from charm_lite.toolbox.PKEnc import PKEnc
    
    class MyScheme(PKEnc):
        def __init__(self):
            super().__init__()
        
        def keygen(self):
            return None
        
        def encrypt(self, pk, msg):
            return None
        
        def decrypt(self, sk, ct):
            return None
    
    scheme = MyScheme()
    assert scheme is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

