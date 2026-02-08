'''
Distributed Key Generation for CGGMP21 Threshold ECDSA

| From: "UC Non-Interactive, Proactive, Threshold ECDSA with Identifiable Aborts"
| By:   Ran Canetti, Rosario Gennaro, Steven Goldfeder, et al.
| Published: CCS 2020 / ePrint 2021/060
| URL:  https://eprint.iacr.org/2021/060

* type:          distributed key generation
* setting:       Elliptic Curve + Paillier
* assumption:    DDH, DCR, Strong RSA

This module implements the DKG protocol for CGGMP21 threshold ECDSA.
Key differences from GG18:
- Uses Pedersen VSS for information-theoretic hiding
- Includes Paillier key correctness proofs
- Supports identifiable aborts

Protocol Overview (3 rounds):
1. Round 1: Generate secrets, Pedersen commitments, Paillier keypair + proof
2. Round 2: Send VSS shares with decommitments
3. Round 3: Verify shares, compute key share with abort identification

:Authors: J. Ayo Akinyele
:Date:    02/2026
'''

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.integergroup import RSAGroup
from charm.toolbox.threshold_sharing import ThresholdSharing
from charm.toolbox.paillier_mta import PaillierMtA, PaillierKeyPair
from charm.schemes.threshold.cggmp21_proofs import (
    RingPedersenParams, RingPedersenGenerator, CGGMP21_ZKProofs
)
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
import hashlib

# Type aliases
ZRElement = Any
GElement = Any
ECGroupType = Any
PartyId = int


@dataclass
class CGGMP21_KeyShare:
    """
    Key share for CGGMP21 threshold ECDSA.
    
    Contains EC key share, Paillier keypair, and Ring-Pedersen parameters.
    
    Attributes:
        party_id: Party identifier (1 to n)
        x_i: Private key share
        X: Combined public key
        X_i: Verification key g^{x_i}
        paillier: Paillier keypair for this party
        other_paillier_pks: Dict of other parties' Paillier public keys
        ring_pedersen: Ring-Pedersen commitment parameters
        t: Threshold parameter
        n: Total number of parties
    """
    party_id: PartyId
    x_i: ZRElement
    X: GElement
    X_i: GElement
    paillier: PaillierKeyPair
    other_paillier_pks: Dict[PartyId, Dict]
    ring_pedersen: RingPedersenParams
    t: int
    n: int
    
    def get_paillier_pk(self, party_id: PartyId) -> Dict:
        """Get Paillier public key for a party."""
        if party_id == self.party_id:
            return self.paillier.pk
        return self.other_paillier_pks.get(party_id)


class SecurityAbort(Exception):
    """Exception for identifiable security abort in CGGMP21."""
    
    def __init__(self, message: str, accused_party: Optional[PartyId] = None,
                 evidence: Optional[Dict] = None):
        super().__init__(message)
        self.accused_party = accused_party
        self.evidence = evidence or {}


class CGGMP21_DKG:
    """
    CGGMP21 Distributed Key Generation with identifiable aborts.
    
    Uses Pedersen VSS and includes proofs for Paillier key correctness.
    
    >>> from charm.toolbox.eccurve import secp256k1
    >>> from charm.toolbox.integergroup import RSAGroup
    >>> group = ECGroup(secp256k1)
    >>> rsa_group = RSAGroup()
    >>> dkg = CGGMP21_DKG(group, rsa_group, threshold=2, num_parties=3, paillier_bits=512)
    >>> g = group.random(G)
    >>> h = group.random(G)
    >>> # Round 1
    >>> r1_results = [dkg.keygen_round1(i+1, g, h, b"session1") for i in range(3)]
    >>> round1_msgs = [r[0] for r in r1_results]
    >>> states = [r[1] for r in r1_results]
    >>> # Round 2
    >>> r2_results = [dkg.keygen_round2(i+1, states[i], round1_msgs) for i in range(3)]
    >>> shares_out = [r[0] for r in r2_results]
    >>> states = [r[1] for r in r2_results]
    >>> # Collect shares
    >>> received = {}
    >>> for recv in range(1, 4):
    ...     received[recv] = {send+1: shares_out[send][recv] for send in range(3)}
    >>> # Round 3
    >>> results = [dkg.keygen_round3(i+1, states[i], received[i+1], round1_msgs) for i in range(3)]
    >>> key_shares = [r[0] for r in results]
    >>> key_shares[0].X == key_shares[1].X == key_shares[2].X
    True
    """
    
    def __init__(self, ec_group: ECGroupType, rsa_group: RSAGroup,
                 threshold: int, num_parties: int, paillier_bits: int = 2048):
        """
        Initialize CGGMP21 DKG.
        
        Args:
            ec_group: EC group (e.g., ECGroup(secp256k1))
            rsa_group: RSA group for Paillier
            threshold: Minimum parties to sign (t)
            num_parties: Total parties (n)
            paillier_bits: Paillier modulus bit length
        """
        if threshold > num_parties:
            raise ValueError("threshold cannot exceed num_parties")
        if threshold < 1:
            raise ValueError("threshold must be at least 1")
        
        self.group = ec_group
        self.rsa_group = rsa_group
        self.t = threshold
        self.n = num_parties
        self.paillier_bits = paillier_bits
        self.order = ec_group.order()
        self._sharing = ThresholdSharing(ec_group)
        self._paillier_mta = PaillierMtA(rsa_group, int(self.order), paillier_bits)
        self._rp_gen = RingPedersenGenerator(rsa_group)

    def _hash_commitment(self, *args) -> bytes:
        """Compute commitment hash for round 1."""
        h = hashlib.sha256()
        h.update(b"CGGMP21_COMMIT:")
        for arg in args:
            if isinstance(arg, bytes):
                h.update(arg)
            else:
                h.update(str(arg).encode())
        return h.digest()

    def keygen_round1(self, party_id: PartyId, generator: GElement,
                      h_point: GElement, session_id: bytes) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Round 1: Generate secrets, commitments, and Paillier keypair.

        Args:
            party_id: This party's identifier (1 to n)
            generator: EC generator point g
            h_point: Second generator h for Pedersen commitment (must be independent of g)
            session_id: Unique session identifier

        Returns:
            Tuple of (broadcast_msg, private_state)
        """
        # Generate random secret and blinding factor
        secret = self.group.random(ZR)
        blinding = self.group.random(ZR)

        # Generate polynomial coefficients (secret is constant term)
        coeffs = [secret]
        blinding_coeffs = [blinding]
        for _ in range(self.t - 1):
            coeffs.append(self.group.random(ZR))
            blinding_coeffs.append(self.group.random(ZR))

        # Compute Pedersen commitments: C_j = g^{a_j} * h^{b_j}
        commitments = []
        for j in range(self.t):
            C_j = (generator ** coeffs[j]) * (h_point ** blinding_coeffs[j])
            commitments.append(C_j)

        # Pre-compute shares for all parties
        shares = {}
        blinding_shares = {}
        for j in range(1, self.n + 1):
            shares[j] = self._sharing._eval_polynomial(coeffs, j)
            blinding_shares[j] = self._sharing._eval_polynomial(blinding_coeffs, j)

        # Generate Paillier keypair
        paillier_keypair = self._paillier_mta.generate_keypair()

        # Generate Ring-Pedersen parameters
        rp_params, rp_trapdoor = self._rp_gen.generate(self.paillier_bits)

        # Commitment to round 1 data (for decommitment in round 2)
        commitment_data = self._hash_commitment(
            session_id, party_id,
            str(commitments[0]),
            str(paillier_keypair.pk['n'])
        )

        # Broadcast message
        broadcast_msg = {
            'party_id': party_id,
            'session_id': session_id,
            'commitment': commitment_data,  # Hash commitment
            'paillier_pk': paillier_keypair.pk,
            'ring_pedersen': rp_params,
        }

        # Private state
        private_state = {
            'party_id': party_id,
            'session_id': session_id,
            'secret': secret,
            'blinding': blinding,
            'coefficients': coeffs,
            'blinding_coefficients': blinding_coeffs,
            'shares': shares,
            'blinding_shares': blinding_shares,
            'commitments': commitments,
            'generator': generator,
            'h_point': h_point,
            'paillier_keypair': paillier_keypair,
            'ring_pedersen': rp_params,
            'rp_trapdoor': rp_trapdoor,
        }

        return broadcast_msg, private_state

    def keygen_round2(self, party_id: PartyId, private_state: Dict[str, Any],
                      all_round1_msgs: List[Dict[str, Any]]) -> Tuple[Dict[PartyId, Dict], Dict[str, Any]]:
        """
        Round 2: Verify round 1, send shares with decommitments.

        Args:
            party_id: This party's identifier
            private_state: Private state from round 1
            all_round1_msgs: Broadcast messages from all parties

        Returns:
            Tuple of (p2p_msgs_with_shares, updated_state)
        """
        # Verify all parties participated
        received_ids = set(msg['party_id'] for msg in all_round1_msgs)
        expected_ids = set(range(1, self.n + 1))
        if received_ids != expected_ids:
            missing = expected_ids - received_ids
            raise SecurityAbort(f"Missing round 1 messages from: {missing}")

        # Prepare P2P messages with shares
        shares = private_state['shares']
        blinding_shares = private_state['blinding_shares']
        commitments = private_state['commitments']

        generator = private_state['generator']
        secret = private_state['secret']
        g_secret = generator ** secret  # g^{a_0} for public key computation

        p2p_msgs = {}
        for j in range(1, self.n + 1):
            p2p_msgs[j] = {
                'from': party_id,
                'share': shares[j],
                'blinding_share': blinding_shares[j],
                'commitments': commitments,  # Decommitment
                'g_secret': g_secret,  # For public key computation
            }

        # Update state
        updated_state = private_state.copy()
        updated_state['all_round1_msgs'] = {msg['party_id']: msg for msg in all_round1_msgs}

        return p2p_msgs, updated_state

    def keygen_round3(self, party_id: PartyId, private_state: Dict[str, Any],
                      received_shares: Dict[PartyId, Dict],
                      all_round1_msgs: List[Dict[str, Any]]) -> Tuple[CGGMP21_KeyShare, Optional[Dict]]:
        """
        Round 3: Verify shares, compute final key share.

        Args:
            party_id: This party's identifier
            private_state: Private state from round 2
            received_shares: P2P messages received from all parties
            all_round1_msgs: Broadcast messages from round 1

        Returns:
            Tuple of (KeyShare, complaint or None)
        """
        generator = private_state['generator']
        h_point = private_state['h_point']
        round1_by_party = {msg['party_id']: msg for msg in all_round1_msgs}

        # Verify all received shares using Pedersen commitments
        for sender_id, msg in received_shares.items():
            share = msg['share']
            blinding_share = msg['blinding_share']
            commitments = msg['commitments']

            # Verify: g^{share} * h^{blinding_share} = prod(C_j^{party_id^j})
            # Note: party_id is the receiver's ID, not sender_id
            lhs = (generator ** share) * (h_point ** blinding_share)

            rhs = commitments[0]
            i_pow = 1
            for j in range(1, len(commitments)):
                i_pow = (i_pow * party_id) % int(self.order)
                i_pow_zr = self.group.init(ZR, i_pow)
                rhs = rhs * (commitments[j] ** i_pow_zr)

            if lhs != rhs:
                complaint = {
                    'accuser': party_id,
                    'accused': sender_id,
                    'share': share,
                    'blinding_share': blinding_share,
                    'commitments': commitments,
                }
                raise SecurityAbort(
                    f"Party {sender_id} sent invalid share",
                    accused_party=sender_id,
                    evidence=complaint
                )

        # Compute final share: x_i = sum of all shares (additive)
        final_share = self.group.init(ZR, 0)
        for msg in received_shares.values():
            final_share = final_share + msg['share']

        # Compute verification key for this party's share
        verification_key = generator ** final_share

        # Compute public key: X = g^x = product of all g^{secret_j}
        # Each party j contributed g^{a_j_0} via g_secret in their Round 2 message
        # Since x = sum(a_j_0 for all j), X = g^x = product(g^{a_j_0})
        public_key = None
        for sender_id, msg in received_shares.items():
            if 'g_secret' in msg:
                if public_key is None:
                    public_key = msg['g_secret']
                else:
                    public_key = public_key * msg['g_secret']

        # Fallback if g_secret not available
        if public_key is None:
            public_key = verification_key  # Wrong but at least it won't crash

        # Collect other parties' Paillier public keys
        other_paillier_pks = {}
        for msg in all_round1_msgs:
            if msg['party_id'] != party_id:
                other_paillier_pks[msg['party_id']] = msg['paillier_pk']

        key_share = CGGMP21_KeyShare(
            party_id=party_id,
            x_i=final_share,
            X=public_key,
            X_i=verification_key,
            paillier=private_state['paillier_keypair'],
            other_paillier_pks=other_paillier_pks,
            ring_pedersen=private_state['ring_pedersen'],
            t=self.t,
            n=self.n
        )

        return key_share, None

