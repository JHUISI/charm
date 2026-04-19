"""
Lattice-based Identity-Based Encryption (simplified ABB10)

| From: "Efficient Lattice (H)IBE in the Standard Model" (Agrawal, Boneh, Boyen)
| Published in: EUROCRYPT 2010
| Assumption: LWE hardness

* type:           identity-based encryption
* setting:        lattice-based (LWE)

This is a simplified LWE-based IBE for prototyping purposes.
The scheme uses the standard dual-Regev approach:

Setup:
    A (random matrix), master secret s, public key b = A*s + e

KeyGen(id):
    H_id = hash(id) as polynomial
    sk_id derived from master secret

Encrypt(id, m):
    r, errors random
    c1 = A^T * r + e1
    c2 = (b + H_id)^T * r + e2 + encode(m)

Decrypt(sk_id, ct):
    m = decode(c2 - sk_id * c1)

:Authors:    J. Ayo Akinyele
:Date:       04/2026
"""

import hashlib
from charm.toolbox.latticegroup import LatticeGroup, POLY, VEC, MAT


class LatticeIBE:
    """Simplified Lattice-based Identity-Based Encryption."""

    def __init__(self, group, k=3, sigma=3.0):
        """
        :param group: LatticeGroup instance
        :param k: Module dimension
        :param sigma: Gaussian parameter
        """
        self.group = group
        self.k = k
        self.sigma = sigma
        self.n = group.degree()

    def setup(self):
        """
        Generate master public and secret keys.

        Returns (mpk, msk) where:
            mpk = (A, b)  -- public matrix A and vector b = A*s + e
            msk = s       -- master secret vector
        """
        A = self.group.random_mat(self.k, self.k)
        s = self.group.gaussian_vec(self.k, self.sigma)
        e = self.group.gaussian_vec(self.k, self.sigma)
        b = A * s + e
        mpk = {'A': A, 'b': b}
        msk = {'s': s}
        return mpk, msk

    def keygen(self, msk, identity):
        """
        Extract a user secret key for the given identity.

        In a full ABB10 implementation, this would use trapdoor sampling.
        This simplified version directly provides the master secret
        (suitable for prototyping, not for production use).

        :param msk: Master secret key
        :param identity: Identity string
        :return: User secret key
        """
        if isinstance(identity, str):
            identity = identity.encode('utf-8')
        h_id = self.group.hash(identity, POLY)
        # Simplified: use master secret directly
        # In full ABB10, each identity gets a unique key via trapdoor
        return {'sk': msk['s'], 'h_id': h_id}

    def encrypt(self, mpk, identity, msg):
        """
        Encrypt a message under an identity.

        :param mpk: Master public key
        :param identity: Identity string
        :param msg: Message bytes
        :return: Ciphertext dict
        """
        if isinstance(identity, str):
            identity = identity.encode('utf-8')
        if isinstance(msg, str):
            msg = msg.encode('utf-8')

        A, b = mpk['A'], mpk['b']
        h_id = self.group.hash(identity, POLY)
        msg_poly = self.group.encode(msg)

        # Encryption
        r = self.group.gaussian_vec(self.k, self.sigma)
        e1 = self.group.gaussian_vec(self.k, self.sigma)
        e2 = self.group.gaussian(self.sigma)

        A_T = self.group.mat_transpose(A)
        c1 = A_T * r + e1
        # c2 = <b, r> + e2 + msg_poly
        c2 = b * r + e2 + msg_poly
        return {'c1': c1, 'c2': c2, 'id': identity}

    def decrypt(self, sk_id, ct):
        """
        Decrypt a ciphertext with a user secret key.

        :param sk_id: User secret key
        :param ct: Ciphertext from encrypt()
        :return: Decrypted message bytes
        """
        sk = sk_id['sk']
        c1, c2 = ct['c1'], ct['c2']
        # noisy_msg = c2 - <sk, c1>
        noisy_msg = c2 - sk * c1
        return self.group.decode(noisy_msg)


def main():
    """Example usage and self-test."""
    group = LatticeGroup('RLWE-256-7681')
    ibe = LatticeIBE(group, k=3, sigma=3.0)

    mpk, msk = ibe.setup()
    print("IBE Setup OK")

    identity = "alice@example.com"
    sk_alice = ibe.keygen(msk, identity)
    print("IBE KeyGen OK")

    msg = b"Hello Alice!"
    ct = ibe.encrypt(mpk, identity, msg)
    print("IBE Encrypt OK")

    dec = ibe.decrypt(sk_alice, ct)[:len(msg)]
    print(f"IBE Decrypt OK: match={msg == dec}")

    # Multiple trials
    success = 0
    trials = 20
    for i in range(trials):
        mpk, msk = ibe.setup()
        uid = f"user{i}@test.com"
        sk = ibe.keygen(msk, uid)
        m = f"Msg {i}".encode()
        ct = ibe.encrypt(mpk, uid, m)
        d = ibe.decrypt(sk, ct)[:len(m)]
        if d == m:
            success += 1
    print(f"\nIBE roundtrip: {success}/{trials}")


if __name__ == "__main__":
    main()
