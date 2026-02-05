"""
secp256k1 curve constant for charm-crypto-lite.

This is the only curve supported by charm-crypto-lite.
For additional curves, use the full charm-crypto-framework package.
"""

# secp256k1: The curve used by Bitcoin and Ethereum
# OpenSSL NID (Numeric ID) for secp256k1
secp256k1 = 714

__all__ = ['secp256k1']
