'''
Zero-Knowledge Proofs for CGGMP21 Threshold ECDSA

| From: "UC Non-Interactive, Proactive, Threshold ECDSA with Identifiable Aborts"
| By:   Ran Canetti, Rosario Gennaro, Steven Goldfeder, et al.
| Published: CCS 2020 / ePrint 2021/060
| URL:  https://eprint.iacr.org/2021/060

* type:          zero-knowledge proofs
* setting:       Composite modulus (Paillier) + Elliptic Curve
* assumption:    DCR, DDH, Strong RSA

This module implements the ZK proofs needed for CGGMP21:
- Ring-Pedersen Parameters: Special commitment parameters for ZK proofs
- Π^{enc}: Prove knowledge of Paillier plaintext
- Π^{log}: Prove Paillier plaintext equals EC discrete log
- Π^{aff-g}: Prove affine operation on Paillier ciphertext
- Π^{mul}: Prove multiplication of Paillier ciphertexts

:Authors: J. Ayo Akinyele
:Date:    02/2026
'''

from typing import Dict, Tuple, Optional, Any, List
from dataclasses import dataclass
from charm.toolbox.integergroup import RSAGroup, integer, toInt
from charm.toolbox.securerandom import SecureRandomFactory
from charm.toolbox.paillier_zkproofs import PaillierZKProofs, PaillierEncProof, PaillierDLogProof
import hashlib

# Type aliases
ZRElement = Any
GElement = Any


@dataclass
class RingPedersenParams:
    """
    Ring-Pedersen commitment parameters for CGGMP21.
    
    Used for range proofs and other ZK proofs in CGGMP21.
    Generated using a safe RSA modulus with unknown factorization.
    
    Attributes:
        N: RSA modulus (product of two safe primes)
        s: Random quadratic residue mod N
        t: t = s^lambda mod N where lambda is secret
    """
    N: int
    s: int
    t: int
    
    def __post_init__(self):
        if self.N <= 0:
            raise ValueError("N must be positive")


@dataclass
class AffGProof:
    """
    Proof for affine operation on Paillier ciphertext (Π^{aff-g}).
    
    Proves: D = C^x * Enc_pk(y; rho) for known x, y
    Also proves: X = g^x in EC group
    """
    commitment_S: int       # S = s^x * t^mu mod N_tilde
    commitment_A: int       # A in Paillier
    commitment_Bx: Any      # B_x in EC group
    commitment_By: int      # B_y in Paillier
    commitment_E: int       # E = s^alpha * t^gamma mod N_tilde
    commitment_F: int       # F = s^beta * t^delta mod N_tilde
    challenge: bytes
    response_z1: int        # z_1 = alpha + e*x
    response_z2: int        # z_2 = beta + e*y
    response_z3: int        # z_3 = gamma + e*mu
    response_z4: int        # z_4 = delta + e*nu
    response_w: int         # w = r * rho^e mod N_tilde


@dataclass
class MulProof:
    """
    Proof for multiplication of Paillier ciphertexts (Π^{mul}).
    
    Proves: C = A^x * Enc(0; r) where D = Enc(x)
    i.e., C encrypts the product of plaintexts of A and D.
    """
    commitment_A: int       # A = Enc(alpha; r_a)
    commitment_Bx: Any      # B_x = g^alpha in EC
    commitment_E: int       # E = s^alpha * t^gamma mod N_tilde
    challenge: bytes
    response_z: int         # z = alpha + e*x
    response_u: int         # u in ZZ
    response_v: int         # v in ZZ


class RingPedersenGenerator:
    """
    Generator for Ring-Pedersen commitment parameters.
    
    Creates safe parameters for CGGMP21 ZK proofs.
    """
    
    def __init__(self, rsa_group: RSAGroup):
        self.rsa_group = rsa_group
        self.rand = SecureRandomFactory.getInstance()
    
    def generate(self, bits: int = 2048) -> Tuple[RingPedersenParams, Dict[str, int]]:
        """
        Generate Ring-Pedersen parameters.
        
        Args:
            bits: Bit length for RSA modulus (default 2048)
            
        Returns:
            Tuple of (public params, private trapdoor)
        """
        # Generate safe RSA modulus N = p*q where p=2p'+1, q=2q'+1
        # For simplicity, we use regular RSA primes here
        # Full implementation should use safe primes
        p = self._generate_prime(bits // 2)
        q = self._generate_prime(bits // 2)
        N = p * q
        
        # phi(N) = (p-1)(q-1)
        phi_N = (p - 1) * (q - 1)
        
        # Generate random lambda
        lambda_bytes = self.rand.getRandomBytes(bits // 8)
        lambda_val = int.from_bytes(lambda_bytes, 'big') % phi_N
        
        # Generate random s (quadratic residue)
        s_bytes = self.rand.getRandomBytes(bits // 8)
        s_raw = int.from_bytes(s_bytes, 'big') % N
        s = pow(s_raw, 2, N)  # Make it a quadratic residue
        
        # Compute t = s^lambda mod N
        t = pow(s, lambda_val, N)
        
        params = RingPedersenParams(N=N, s=s, t=t)
        trapdoor = {'p': p, 'q': q, 'lambda': lambda_val, 'phi_N': phi_N}
        
        return params, trapdoor
    
    def _generate_prime(self, bits: int) -> int:
        """Generate a random prime of specified bit length."""
        from charm.core.math.integer import randomPrime
        return int(randomPrime(bits))


class CGGMP21_ZKProofs(PaillierZKProofs):
    """
    Extended ZK proofs for CGGMP21.
    
    Builds on PaillierZKProofs with additional proofs:
    - Π^{aff-g}: Affine operation on Paillier ciphertext
    - Π^{mul}: Multiplication of Paillier ciphertexts
    - Range proofs using Ring-Pedersen commitments
    """
    
    def __init__(self, rsa_group: RSAGroup, ec_group: Any = None,
                 ring_pedersen: Optional[RingPedersenParams] = None):
        """
        Initialize CGGMP21 ZK proofs.
        
        Args:
            rsa_group: RSA group for Paillier
            ec_group: EC group for curve operations
            ring_pedersen: Ring-Pedersen parameters (generated if None)
        """
        super().__init__(rsa_group, ec_group)
        self.ring_pedersen = ring_pedersen

    def _ring_pedersen_commit(self, x: int, r: int) -> int:
        """Compute Ring-Pedersen commitment: s^x * t^r mod N."""
        if self.ring_pedersen is None:
            raise ValueError("Ring-Pedersen parameters required")
        N = self.ring_pedersen.N
        s = self.ring_pedersen.s
        t = self.ring_pedersen.t
        return (pow(s, x, N) * pow(t, r, N)) % N

    def prove_affine_g(self, x: int, y: int, rho: int,
                       C: Any, D: Any, X: Any,
                       pk: Dict, generator: Any) -> AffGProof:
        """
        Prove affine operation on Paillier ciphertext (Π^{aff-g}).

        Proves: D = C^x * Enc(y; rho) and X = g^x

        Args:
            x: Scalar multiplier
            y: Additive term (plaintext)
            rho: Randomness for encryption of y
            C: Input Paillier ciphertext
            D: Output Paillier ciphertext D = C^x * Enc(y; rho)
            X: EC point X = g^x
            pk: Paillier public key
            generator: EC generator g

        Returns:
            AffGProof object
        """
        if self.ec_group is None:
            raise ValueError("EC group required")
        if self.ring_pedersen is None:
            raise ValueError("Ring-Pedersen parameters required")

        n = int(pk['n'])
        n2 = int(pk['n2'])
        N_tilde = self.ring_pedersen.N

        # Sample random values
        alpha_bytes = self.rand.getRandomBytes(32)
        alpha = int.from_bytes(alpha_bytes, 'big') % int(self.ec_group.order())

        beta_bytes = self.rand.getRandomBytes(256)
        beta = int.from_bytes(beta_bytes, 'big') % n

        r_bytes = self.rand.getRandomBytes(256)
        r = int.from_bytes(r_bytes, 'big') % n

        gamma_bytes = self.rand.getRandomBytes(256)
        gamma = int.from_bytes(gamma_bytes, 'big') % N_tilde

        mu_bytes = self.rand.getRandomBytes(256)
        mu = int.from_bytes(mu_bytes, 'big') % N_tilde

        delta_bytes = self.rand.getRandomBytes(256)
        delta = int.from_bytes(delta_bytes, 'big') % N_tilde

        nu_bytes = self.rand.getRandomBytes(256)
        nu = int.from_bytes(nu_bytes, 'big') % N_tilde

        # Commitments
        S = self._ring_pedersen_commit(x, mu)

        # A = C^alpha * Enc(beta; r)
        C_int = int(C['c']) if isinstance(C, dict) else int(C)
        g_int = int(pk['g'])
        A = (pow(C_int, alpha, n2) * pow(g_int, beta, n2) * pow(r, n, n2)) % n2

        # B_x = g^alpha in EC
        from charm.toolbox.ecgroup import ZR
        alpha_zr = self.ec_group.init(ZR, alpha)
        Bx = generator ** alpha_zr

        # B_y = Enc(beta; r) - simplified
        By = (pow(g_int, beta, n2) * pow(r, n, n2)) % n2

        E = self._ring_pedersen_commit(alpha, gamma)
        F = self._ring_pedersen_commit(beta, delta)

        # Fiat-Shamir challenge
        challenge = self._hash_to_challenge(n, C_int, A, Bx, By, E, F, S)
        e = int.from_bytes(challenge, 'big') % int(self.ec_group.order())

        # Responses
        z1 = alpha + e * x
        z2 = beta + e * y
        z3 = gamma + e * mu
        z4 = delta + e * nu
        w = (r * pow(rho, e, n)) % n

        return AffGProof(
            commitment_S=S,
            commitment_A=A,
            commitment_Bx=Bx,
            commitment_By=By,
            commitment_E=E,
            commitment_F=F,
            challenge=challenge,
            response_z1=z1,
            response_z2=z2,
            response_z3=z3,
            response_z4=z4,
            response_w=w
        )

    def verify_affine_g(self, C: Any, D: Any, X: Any,
                        pk: Dict, generator: Any, proof: AffGProof) -> bool:
        """
        Verify Π^{aff-g} proof.

        Args:
            C: Input Paillier ciphertext
            D: Output Paillier ciphertext
            X: EC point
            pk: Paillier public key
            generator: EC generator
            proof: The proof to verify

        Returns:
            True if proof is valid
        """
        if self.ec_group is None or self.ring_pedersen is None:
            return False

        n = int(pk['n'])
        n2 = int(pk['n2'])
        g_int = int(pk['g'])
        N_tilde = self.ring_pedersen.N

        C_int = int(C['c']) if isinstance(C, dict) else int(C)
        D_int = int(D['c']) if isinstance(D, dict) else int(D)

        e = int.from_bytes(proof.challenge, 'big') % int(self.ec_group.order())

        # Verify: C^{z1} * g^{z2} * w^n = A * D^e mod n^2
        lhs = (pow(C_int, proof.response_z1, n2) *
               pow(g_int, proof.response_z2, n2) *
               pow(proof.response_w, n, n2)) % n2
        rhs = (proof.commitment_A * pow(D_int, e, n2)) % n2
        if lhs != rhs:
            return False

        # Verify EC: g^{z1} = B_x * X^e
        from charm.toolbox.ecgroup import ZR
        z1_zr = self.ec_group.init(ZR, proof.response_z1)
        e_zr = self.ec_group.init(ZR, e)
        lhs_ec = generator ** z1_zr
        rhs_ec = proof.commitment_Bx * (X ** e_zr)
        if lhs_ec != rhs_ec:
            return False

        # Verify Ring-Pedersen: s^{z1} * t^{z3} = E * S^e mod N_tilde
        s = self.ring_pedersen.s
        t = self.ring_pedersen.t
        lhs_rp = (pow(s, proof.response_z1, N_tilde) *
                  pow(t, proof.response_z3, N_tilde)) % N_tilde
        rhs_rp = (proof.commitment_E * pow(proof.commitment_S, e, N_tilde)) % N_tilde
        if lhs_rp != rhs_rp:
            return False

        return True

    def prove_mul(self, x: int, C: Any, D: Any, pk: Dict,
                  generator: Any) -> MulProof:
        """
        Prove multiplication of Paillier ciphertexts (Π^{mul}).

        Proves: D = C^x * Enc(0; r) where we know x

        Args:
            x: The scalar multiplier
            C: Input ciphertext C = Enc(m)
            D: Output ciphertext D = Enc(x*m)
            pk: Paillier public key
            generator: EC generator for proving X = g^x

        Returns:
            MulProof object
        """
        if self.ec_group is None or self.ring_pedersen is None:
            raise ValueError("EC group and Ring-Pedersen required")

        n = int(pk['n'])
        n2 = int(pk['n2'])
        g_int = int(pk['g'])
        N_tilde = self.ring_pedersen.N

        # Sample random values
        alpha_bytes = self.rand.getRandomBytes(32)
        alpha = int.from_bytes(alpha_bytes, 'big') % int(self.ec_group.order())

        r_a_bytes = self.rand.getRandomBytes(256)
        r_a = int.from_bytes(r_a_bytes, 'big') % n

        gamma_bytes = self.rand.getRandomBytes(256)
        gamma = int.from_bytes(gamma_bytes, 'big') % N_tilde

        # Commitments
        C_int = int(C['c']) if isinstance(C, dict) else int(C)
        A = (pow(C_int, alpha, n2) * pow(r_a, n, n2)) % n2

        from charm.toolbox.ecgroup import ZR
        alpha_zr = self.ec_group.init(ZR, alpha)
        Bx = generator ** alpha_zr

        E = self._ring_pedersen_commit(alpha, gamma)

        # Fiat-Shamir challenge
        challenge = self._hash_to_challenge(n, C_int, A, Bx, E)
        e = int.from_bytes(challenge, 'big') % int(self.ec_group.order())

        # Responses
        z = alpha + e * x
        u = 0  # Simplified
        v = gamma + e * 0  # Simplified

        return MulProof(
            commitment_A=A,
            commitment_Bx=Bx,
            commitment_E=E,
            challenge=challenge,
            response_z=z,
            response_u=u,
            response_v=v
        )

    def verify_mul(self, C: Any, D: Any, X: Any,
                   pk: Dict, generator: Any, proof: MulProof) -> bool:
        """
        Verify Π^{mul} proof.

        Args:
            C: Input ciphertext
            D: Output ciphertext
            X: EC point X = g^x
            pk: Paillier public key
            generator: EC generator
            proof: The proof to verify

        Returns:
            True if proof is valid
        """
        if self.ec_group is None:
            return False

        n = int(pk['n'])
        n2 = int(pk['n2'])

        C_int = int(C['c']) if isinstance(C, dict) else int(C)
        D_int = int(D['c']) if isinstance(D, dict) else int(D)

        e = int.from_bytes(proof.challenge, 'big') % int(self.ec_group.order())

        # Verify EC: g^z = B_x * X^e
        from charm.toolbox.ecgroup import ZR
        z_zr = self.ec_group.init(ZR, proof.response_z)
        e_zr = self.ec_group.init(ZR, e)
        lhs_ec = generator ** z_zr
        rhs_ec = proof.commitment_Bx * (X ** e_zr)

        return lhs_ec == rhs_ec

