"""
PKEnc: Public Key Encryption base class for charm-crypto-lite.

This is a minimal base class for public key encryption schemes.
Subclass this to implement your own EC-based encryption schemes.
"""

from charm_lite.toolbox.ecgroup import ECGroup

__all__ = ['PKEnc']


class PKEnc:
    """Base class for public key encryption schemes.
    
    This is an empty base class that can be subclassed to implement
    EC-based public key encryption schemes on secp256k1.
    
    Example:
        from charm_lite.toolbox.PKEnc import PKEnc
        from charm_lite.toolbox.ecgroup import ECGroup, ZR, G
        from charm_lite.toolbox.eccurve import secp256k1
        
        class MyEncryptionScheme(PKEnc):
            def __init__(self):
                super().__init__()
                self.group = ECGroup(secp256k1)
            
            def keygen(self):
                # Generate key pair
                x = self.group.random(ZR)  # private key
                g = self.group.generator()
                h = g ** x                  # public key
                return {'pk': h, 'sk': x}
            
            def encrypt(self, pk, msg):
                # Implement encryption
                pass
            
            def decrypt(self, sk, ct):
                # Implement decryption
                pass
    """
    
    def __init__(self):
        """Initialize the PKEnc base class."""
        pass
    
    def keygen(self):
        """Generate a key pair. Override in subclass."""
        raise NotImplementedError("keygen must be implemented by subclass")
    
    def encrypt(self, pk, msg):
        """Encrypt a message. Override in subclass."""
        raise NotImplementedError("encrypt must be implemented by subclass")
    
    def decrypt(self, sk, ct):
        """Decrypt a ciphertext. Override in subclass."""
        raise NotImplementedError("decrypt must be implemented by subclass")

