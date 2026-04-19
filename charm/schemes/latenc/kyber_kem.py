"""
Kyber-style Key Encapsulation Mechanism (simplified ML-KEM)

| From: CRYSTALS-Kyber / ML-KEM (FIPS 203)
| Published in: NIST Post-Quantum Standard
| Assumption: Module-LWE hardness

* type:           KEM (key encapsulation)
* setting:        lattice-based (Module-LWE)
* security:       IND-CPA (this implementation; full ML-KEM adds IND-CCA via FO transform)

This is a simplified Kyber implementation for prototyping.
It implements the core CPAPKE component (IND-CPA secure PKE)
without the Fujisaki-Okamoto transform needed for IND-CCA security.

:Authors:    J. Ayo Akinyele
:Date:       04/2026
"""

import hashlib
from charm.toolbox.latticegroup import LatticeGroup, POLY, VEC, MAT
from charm.toolbox.LatticeKEM import LatticeKEM


KYBER_PARAMS = {
    'KYBER-512':  {'k': 2, 'eta1': 3, 'eta2': 2, 'du': 10, 'dv': 4},
    'KYBER-768':  {'k': 3, 'eta1': 2, 'eta2': 2, 'du': 10, 'dv': 4},
    'KYBER-1024': {'k': 4, 'eta1': 2, 'eta2': 2, 'du': 11, 'dv': 5},
}


class KyberKEM(LatticeKEM):
    """Simplified Kyber (ML-KEM) Key Encapsulation Mechanism."""

    def __init__(self, group, param_id='KYBER-768'):
        super().__init__(group)
        if param_id not in KYBER_PARAMS:
            raise ValueError(f"Unknown Kyber params: {param_id}. Use: {list(KYBER_PARAMS.keys())}")
        self.params = KYBER_PARAMS[param_id]
        self.k = self.params['k']
        self.eta1 = self.params['eta1']
        self.eta2 = self.params['eta2']
        self.du = self.params['du']
        self.dv = self.params['dv']
        self.n = group.degree()
        # CBD(eta) has variance eta/2; use sqrt(eta/2) as Gaussian sigma
        # to match the noise distribution of real Kyber
        import math
        self._sigma1 = math.sqrt(self.eta1 / 2.0)
        self._sigma2 = math.sqrt(self.eta2 / 2.0)

    def keygen(self):
        """
        Kyber.CPAPKE.KeyGen

        Returns (pk, sk) where:
            pk = (A, t)  -- public matrix A and vector t = A*s + e
            sk = s       -- secret vector
        """
        k = self.k
        # Generate uniform matrix A (k×k of polynomials)
        A = self.group.random_mat(k, k)
        # Sample secret and error (Gaussian approximation of CBD(eta1))
        s = self.group.gaussian_vec(k, self._sigma1)
        e = self.group.gaussian_vec(k, self._sigma1)
        # t = A*s + e
        t = A * s + e
        pk = {'A': A, 't': t}
        sk = {'s': s}
        return pk, sk

    def encapsulate(self, pk):
        """
        Kyber.CPAPKE.Enc + shared secret derivation.

        Returns (ct, shared_secret) where ct contains compressed ciphertext.
        """
        k = self.k
        A, t = pk['A'], pk['t']
        # Sample ephemeral secret and errors (Gaussian approximation of CBD)
        r = self.group.gaussian_vec(k, self._sigma1)
        e1 = self.group.gaussian_vec(k, self._sigma2)
        e2 = self.group.gaussian(self._sigma2)
        # Generate random message for KEM
        import os
        msg_bytes = os.urandom(32)
        msg_poly = self.group.encode(msg_bytes)
        # u = A^T * r + e1  (transpose is critical for noise cancellation)
        A_T = self.group.mat_transpose(A)
        u = A_T * r + e1
        # v = t^T * r + e2 + encode(m) (inner product of vectors)
        v = t * r + e2 + msg_poly
        ct = {'u': u, 'v': v}
        # Shared secret = H(msg)
        shared_secret = hashlib.sha256(msg_bytes).digest()
        return ct, shared_secret

    def decapsulate(self, sk, ct):
        """
        Kyber.CPAPKE.Dec + shared secret derivation.

        Returns shared_secret bytes.
        """
        s = sk['s']
        u, v = ct['u'], ct['v']
        # Recover noisy message: v - s^T * u
        noisy_msg = v - s * u
        # Decode message
        msg_bytes = self.group.decode(noisy_msg, num_bytes=32)
        # Shared secret = H(msg)
        shared_secret = hashlib.sha256(msg_bytes).digest()
        return shared_secret


def main():
    """Example usage and self-test."""
    group = LatticeGroup('KYBER-768')
    kem = KyberKEM(group, 'KYBER-768')

    pk, sk = kem.keygen()
    print("Kyber KeyGen OK")

    ct, ss_enc = kem.encapsulate(pk)
    print("Kyber Encapsulate OK")

    ss_dec = kem.decapsulate(sk, ct)
    print("Kyber Decapsulate OK")
    print(f"Shared secrets match: {ss_enc == ss_dec}")
    print(f"SS (enc): {ss_enc.hex()[:32]}...")
    print(f"SS (dec): {ss_dec.hex()[:32]}...")

    # Multiple trials
    success = 0
    trials = 20
    for _ in range(trials):
        pk, sk = kem.keygen()
        ct, ss1 = kem.encapsulate(pk)
        ss2 = kem.decapsulate(sk, ct)
        if ss1 == ss2:
            success += 1
    print(f"\nKEM roundtrip: {success}/{trials}")


if __name__ == "__main__":
    main()
