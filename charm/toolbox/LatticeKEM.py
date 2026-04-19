"""
Base class for lattice-based Key Encapsulation Mechanisms (KEMs).

Subclass this to implement ML-KEM (Kyber) or other lattice-based KEMs.
"""

from charm.toolbox.latticegroup import LatticeGroup


class LatticeKEM:
    """
    Abstract base class for lattice-based KEMs.

    A KEM consists of three algorithms:
    - keygen() -> (pk, sk)
    - encapsulate(pk) -> (ct, shared_secret)
    - decapsulate(sk, ct) -> shared_secret
    """

    def __init__(self, group):
        if not isinstance(group, LatticeGroup):
            raise TypeError("group must be a LatticeGroup instance")
        self.group = group

    def keygen(self):
        """Generate a keypair (pk, sk)."""
        raise NotImplementedError("Subclasses must implement keygen()")

    def encapsulate(self, pk):
        """Encapsulate: returns (ciphertext, shared_secret)."""
        raise NotImplementedError("Subclasses must implement encapsulate()")

    def decapsulate(self, sk, ct):
        """Decapsulate: returns shared_secret."""
        raise NotImplementedError("Subclasses must implement decapsulate()")
