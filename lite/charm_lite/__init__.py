"""
charm-crypto-lite: Lightweight elliptic curve cryptography from the Charm framework.

This package provides OpenSSL-based elliptic curve operations without
GMP or PBC dependencies.

Example usage:
    from charm_lite.toolbox.ecgroup import ECGroup
    from charm_lite.toolbox.eccurve import secp256k1
    
    group = ECGroup(secp256k1)
    g = group.random(G)
    x = group.random(ZR)
    h = g ** x
"""

# Preload benchmark module to ensure symbols are available
import charm_lite.core.benchmark

__version__ = "0.1.0"
__all__ = ['__version__']

