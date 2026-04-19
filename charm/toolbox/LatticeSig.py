"""
Base class for lattice-based digital signature schemes.

Subclass this to implement ML-DSA (Dilithium) or other lattice-based signatures.
"""

from charm.toolbox.latticegroup import LatticeGroup


class LatticeSig:
    """
    Abstract base class for lattice-based signatures.

    A signature scheme consists of three algorithms:
    - keygen() -> (pk, sk)
    - sign(sk, msg) -> signature
    - verify(pk, msg, signature) -> bool
    """

    def __init__(self, group):
        if not isinstance(group, LatticeGroup):
            raise TypeError("group must be a LatticeGroup instance")
        self.group = group

    def keygen(self):
        """Generate a keypair (pk, sk)."""
        raise NotImplementedError("Subclasses must implement keygen()")

    def sign(self, sk, msg):
        """Sign a message. Returns signature."""
        raise NotImplementedError("Subclasses must implement sign()")

    def verify(self, pk, msg, sig):
        """Verify a signature. Returns True/False."""
        raise NotImplementedError("Subclasses must implement verify()")
