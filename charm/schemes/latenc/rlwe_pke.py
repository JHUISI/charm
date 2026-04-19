"""
LPR (Lyubashevsky-Peikert-Regev) Ring-LWE Public Key Encryption

| From: "On Ideal Lattices and Learning with Errors Over Rings"
| Published in: EUROCRYPT 2010
| Available from: https://eprint.iacr.org/2012/230.pdf

* type:           encryption (public key)
* setting:        lattice-based (Ring-LWE)
* assumption:     RLWE hardness in R_q = Z_q[X]/(X^n+1)

:Authors:    J. Ayo Akinyele
:Date:       04/2026

This scheme encrypts binary messages of up to n bits using Ring-LWE.

KeyGen:
    a <- uniform R_q
    s, e <- Gaussian(sigma)
    pk = (a, b = a*s + e),  sk = s

Encrypt(pk, m):
    r, e1, e2 <- Gaussian(sigma)
    c1 = a*r + e1
    c2 = b*r + e2 + floor(q/2)*m

Decrypt(sk, (c1, c2)):
    noisy = c2 - c1*s
    threshold each coefficient: closer to 0 -> bit 0, closer to q/2 -> bit 1
"""

from charm.toolbox.latticegroup import LatticeGroup, POLY


class RLWE_PKE:
    """Ring-LWE Public Key Encryption (LPR scheme)."""

    def __init__(self, group, sigma=3.0):
        """
        Initialize with a LatticeGroup and Gaussian parameter sigma.

        :param group: LatticeGroup instance (e.g., LatticeGroup('RLWE-256-7681'))
        :param sigma: Standard deviation for discrete Gaussian sampling
        """
        if not isinstance(group, LatticeGroup):
            raise TypeError("group must be a LatticeGroup instance")
        self.group = group
        self.sigma = sigma
        self._max_msg_bytes = group.degree() // 8

    def keygen(self):
        """
        Generate a key pair.

        :return: (pk, sk) where pk = {'a': poly, 'b': poly}, sk = {'s': poly}
        """
        return self.group.rlwe_keygen(sigma=self.sigma)

    def encrypt(self, pk, msg):
        """
        Encrypt a binary message.

        :param pk: Public key from keygen()
        :param msg: bytes to encrypt (max n/8 bytes = n bits)
        :return: Ciphertext dict {'c1': poly, 'c2': poly}
        """
        if isinstance(msg, str):
            msg = msg.encode('utf-8')
        if len(msg) > self._max_msg_bytes:
            raise ValueError(
                f"Message too long: {len(msg)} bytes > {self._max_msg_bytes} max"
            )

        # Encode message: each bit becomes coefficient 0 or floor(q/2)
        msg_poly = self.group.encode(msg)

        # Encrypt using RLWE
        return self.group.rlwe_encrypt(pk, msg_poly, sigma=self.sigma)

    def decrypt(self, sk, ct):
        """
        Decrypt a ciphertext.

        :param sk: Secret key from keygen()
        :param ct: Ciphertext from encrypt()
        :return: Decrypted bytes
        """
        # Get noisy message polynomial: c2 - c1*s ≈ floor(q/2)*m + noise
        noisy = self.group.rlwe_decrypt(sk, ct)

        # Decode by thresholding coefficients
        return self.group.decode(noisy)


def main():
    """Example usage and self-test."""
    group = LatticeGroup('RLWE-256-7681')
    rlwe = RLWE_PKE(group, sigma=3.0)

    # Key generation
    pk, sk = rlwe.keygen()
    print("KeyGen OK")

    # Encrypt
    msg = b"Hello, lattice world!"
    ct = rlwe.encrypt(pk, msg)
    print("Encrypt OK")

    # Decrypt
    decrypted = rlwe.decrypt(sk, ct)
    # Trim to original message length
    decrypted = decrypted[:len(msg)]
    print("Decrypt OK")
    print(f"Original:  {msg}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {msg == decrypted}")

    # Multiple roundtrips
    success = 0
    trials = 20
    for i in range(trials):
        pk, sk = rlwe.keygen()
        test_msg = bytes([i % 256]) * (i % 32 + 1)
        ct = rlwe.encrypt(pk, test_msg)
        dec = rlwe.decrypt(sk, ct)[:len(test_msg)]
        if dec == test_msg:
            success += 1
    print(f"\nRoundtrip test: {success}/{trials} passed")


if __name__ == "__main__":
    main()
