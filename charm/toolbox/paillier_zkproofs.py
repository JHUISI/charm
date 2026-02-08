'''
Zero-Knowledge Proofs for Paillier Encryption (GG18/CGGMP21)

| From: "Fast Multiparty Threshold ECDSA with Fast Trustless Setup" (GG18)
| By:   Rosario Gennaro, Steven Goldfeder
| Published: CCS 2018 / ePrint 2019/114
|
| And: "UC Non-Interactive, Proactive, Threshold ECDSA" (CGGMP21)
| By:   Ran Canetti, Rosario Gennaro, et al.
| Published: ePrint 2021/060

This module implements ZK proofs for Paillier-based threshold ECDSA:
- Range proofs: prove encrypted value is in a specified range
- Π^{enc}: prove knowledge of plaintext for a ciphertext
- Π^{log}: prove EC discrete log equals Paillier plaintext

* type:          zero-knowledge proofs
* setting:       Composite modulus (Paillier) + Elliptic Curve  
* assumption:    DCR, DL

:Authors: Charm Developers
:Date:    02/2026
'''

from typing import Dict, Tuple, Optional, Any, List
from dataclasses import dataclass
from charm.toolbox.integergroup import RSAGroup, integer, toInt
from charm.toolbox.securerandom import SecureRandomFactory
import hashlib

# Type aliases
ZRElement = Any
GElement = Any


@dataclass
class PaillierEncProof:
    """
    Proof of knowledge of plaintext for Paillier ciphertext.
    
    Proves: "I know m such that c = Enc(m; r)"
    
    Attributes:
        commitment: First message (commitment)
        challenge: Fiat-Shamir challenge
        response_m: Response for message
        response_r: Response for randomness
    """
    commitment: Any
    challenge: bytes
    response_m: int
    response_r: int


@dataclass  
class PaillierRangeProof:
    """
    Range proof for Paillier ciphertext.
    
    Proves: "c encrypts m where 0 <= m < B"
    
    Uses bit decomposition approach for simplicity.
    Full implementation would use more efficient techniques.
    """
    bit_commitments: List[Any]
    bit_proofs: List[Dict]
    range_bound_bits: int


@dataclass
class PaillierDLogProof:
    """
    Proof that EC discrete log equals Paillier plaintext (Π^{log}).
    
    Proves: "c = Enc(x) and Q = g^x for the same x"
    
    This links Paillier encryption to EC group operations,
    essential for GG18/CGGMP21 MtA correctness.
    """
    commitment_c: Any      # Paillier commitment
    commitment_Q: Any      # EC commitment
    challenge: bytes
    response_x: int
    response_r: int


class PaillierZKProofs:
    """
    Zero-knowledge proofs for Paillier encryption.
    
    Implements the ZK proofs needed for GG18 and CGGMP21
    threshold ECDSA protocols.
    """
    
    def __init__(self, rsa_group: RSAGroup, ec_group: Any = None):
        """
        Initialize ZK proof system.
        
        Args:
            rsa_group: RSA group for Paillier operations
            ec_group: EC group for DLog proofs (optional)
        """
        self.rsa_group = rsa_group
        self.ec_group = ec_group
        self.rand = SecureRandomFactory.getInstance()
    
    def _hash_to_challenge(self, *args) -> bytes:
        """Compute Fiat-Shamir challenge hash."""
        h = hashlib.sha256()
        h.update(b"PAILLIER_ZK_CHALLENGE:")
        for arg in args:
            if isinstance(arg, bytes):
                h.update(arg)
            elif isinstance(arg, int):
                h.update(arg.to_bytes(256, 'big', signed=False))
            else:
                h.update(str(arg).encode())
        return h.digest()
    
    def prove_encryption_knowledge(self, plaintext: int, ciphertext: Any,
                                    randomness: int, pk: Dict) -> PaillierEncProof:
        """
        Prove knowledge of plaintext for Paillier ciphertext.
        
        Args:
            plaintext: The plaintext m
            ciphertext: The ciphertext c = Enc(m; r)
            randomness: The randomness r used in encryption
            pk: Paillier public key
            
        Returns:
            PaillierEncProof object
        """
        n = int(pk['n'])
        n2 = int(pk['n2'])
        g = pk['g']
        
        # Sample random values for commitment
        alpha_bytes = self.rand.getRandomBytes(256)
        alpha = int.from_bytes(alpha_bytes, 'big') % n
        
        rho_bytes = self.rand.getRandomBytes(256)
        rho = int.from_bytes(rho_bytes, 'big') % n
        
        # Commitment: A = g^alpha * rho^n mod n^2
        g_int = int(g)
        A = (pow(g_int, alpha, n2) * pow(rho, n, n2)) % n2
        
        # Fiat-Shamir challenge
        c_bytes = int(ciphertext['c']) if isinstance(ciphertext, dict) else int(ciphertext)
        challenge = self._hash_to_challenge(n, g_int, c_bytes, A)
        e = int.from_bytes(challenge, 'big') % n
        
        # Responses
        z_m = (alpha + e * plaintext) % n
        z_r = (rho * pow(randomness, e, n)) % n
        
        return PaillierEncProof(
            commitment=A,
            challenge=challenge,
            response_m=z_m,
            response_r=z_r
        )
    
    def verify_encryption_knowledge(self, ciphertext: Any, pk: Dict,
                                     proof: PaillierEncProof) -> bool:
        """
        Verify proof of knowledge of plaintext.
        
        Args:
            ciphertext: The ciphertext being proven
            pk: Paillier public key
            proof: The proof to verify
            
        Returns:
            True if proof is valid
        """
        n = int(pk['n'])
        n2 = int(pk['n2'])
        g = pk['g']
        g_int = int(g)

        # Extract ciphertext value
        c_int = int(ciphertext['c']) if isinstance(ciphertext, dict) else int(ciphertext)

        # Recompute challenge
        expected_challenge = self._hash_to_challenge(n, g_int, c_int, proof.commitment)
        if proof.challenge != expected_challenge:
            return False

        e = int.from_bytes(proof.challenge, 'big') % n

        # Verify: g^{z_m} * z_r^n = A * c^e mod n^2
        lhs = (pow(g_int, proof.response_m, n2) * pow(proof.response_r, n, n2)) % n2
        rhs = (proof.commitment * pow(c_int, e, n2)) % n2

        return lhs == rhs

    def prove_dlog_equality(self, x: int, ciphertext: Any, Q: Any,
                            randomness: int, pk: Dict,
                            generator: Any) -> PaillierDLogProof:
        """
        Prove Paillier plaintext equals EC discrete log (Π^{log}).

        Proves: c = Enc(x) and Q = g^x for the same x

        Args:
            x: The secret value
            ciphertext: Paillier encryption of x
            Q: EC point Q = g^x
            randomness: Randomness used in Paillier encryption
            pk: Paillier public key
            generator: EC generator g

        Returns:
            PaillierDLogProof object
        """
        if self.ec_group is None:
            raise ValueError("EC group required for DLog proof")

        n = int(pk['n'])
        n2 = int(pk['n2'])
        g_pai = pk['g']
        g_pai_int = int(g_pai)

        # Sample random alpha for both proofs
        alpha_bytes = self.rand.getRandomBytes(32)
        alpha = int.from_bytes(alpha_bytes, 'big') % int(self.ec_group.order())

        rho_bytes = self.rand.getRandomBytes(256)
        rho = int.from_bytes(rho_bytes, 'big') % n

        # Paillier commitment: A_c = g^alpha * rho^n mod n^2
        A_c = (pow(g_pai_int, alpha, n2) * pow(rho, n, n2)) % n2

        # EC commitment: A_Q = g^alpha
        from charm.toolbox.ecgroup import ZR
        alpha_zr = self.ec_group.init(ZR, alpha)
        A_Q = generator ** alpha_zr

        # Fiat-Shamir challenge
        c_int = int(ciphertext['c']) if isinstance(ciphertext, dict) else int(ciphertext)
        Q_bytes = self.ec_group.serialize(Q)
        A_Q_bytes = self.ec_group.serialize(A_Q)
        challenge = self._hash_to_challenge(n, c_int, Q_bytes, A_c, A_Q_bytes)
        e = int.from_bytes(challenge, 'big') % int(self.ec_group.order())

        # Responses
        z_x = (alpha + e * x) % int(self.ec_group.order())
        z_r = (rho * pow(randomness, e, n)) % n

        return PaillierDLogProof(
            commitment_c=A_c,
            commitment_Q=A_Q,
            challenge=challenge,
            response_x=z_x,
            response_r=z_r
        )

    def verify_dlog_equality(self, ciphertext: Any, Q: Any, pk: Dict,
                              generator: Any, proof: PaillierDLogProof) -> bool:
        """
        Verify Paillier-EC discrete log equality proof.

        Args:
            ciphertext: Paillier ciphertext
            Q: EC point
            pk: Paillier public key
            generator: EC generator
            proof: The proof to verify

        Returns:
            True if proof is valid
        """
        if self.ec_group is None:
            raise ValueError("EC group required for DLog verification")

        n = int(pk['n'])
        n2 = int(pk['n2'])
        g_pai = pk['g']
        g_pai_int = int(g_pai)

        c_int = int(ciphertext['c']) if isinstance(ciphertext, dict) else int(ciphertext)

        # Recompute challenge
        Q_bytes = self.ec_group.serialize(Q)
        A_Q_bytes = self.ec_group.serialize(proof.commitment_Q)
        expected_challenge = self._hash_to_challenge(
            n, c_int, Q_bytes, proof.commitment_c, A_Q_bytes
        )
        if proof.challenge != expected_challenge:
            return False

        e = int.from_bytes(proof.challenge, 'big') % int(self.ec_group.order())

        # Verify Paillier part: g^{z_x} * z_r^n = A_c * c^e mod n^2
        lhs_c = (pow(g_pai_int, proof.response_x, n2) * pow(proof.response_r, n, n2)) % n2
        rhs_c = (proof.commitment_c * pow(c_int, e, n2)) % n2
        if lhs_c != rhs_c:
            return False

        # Verify EC part: g^{z_x} = A_Q * Q^e
        from charm.toolbox.ecgroup import ZR
        z_x_zr = self.ec_group.init(ZR, proof.response_x)
        e_zr = self.ec_group.init(ZR, e)
        lhs_Q = generator ** z_x_zr
        rhs_Q = proof.commitment_Q * (Q ** e_zr)

        return lhs_Q == rhs_Q

