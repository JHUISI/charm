'''
Distributed Key Generation for GG18 Threshold ECDSA

| From: "Fast Multiparty Threshold ECDSA with Fast Trustless Setup"
| By:   Rosario Gennaro, Steven Goldfeder
| Published: CCS 2018 / ePrint 2019/114
| URL:  https://eprint.iacr.org/2019/114.pdf

* type:          distributed key generation
* setting:       Elliptic Curve + Paillier
* assumption:    DDH, DCR

This module implements the DKG protocol for GG18 threshold ECDSA.
Unlike DKLS23, GG18 requires each party to generate a Paillier keypair
for use in the MtA protocol during signing.

Protocol Overview (3 rounds):
1. Round 1: Generate secret, Feldman VSS commitments, and Paillier keypair
2. Round 2: Send VSS shares to other parties
3. Round 3: Verify shares, compute final key share and public key

:Authors: J. Ayo Akinyele
:Date:    02/2026
'''

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.integergroup import RSAGroup
from charm.toolbox.threshold_sharing import ThresholdSharing
from charm.toolbox.paillier_mta import PaillierMtA, PaillierKeyPair
from typing import Dict, List, Tuple, Optional, Any, Set

# Type aliases
ZRElement = Any
GElement = Any
ECGroupType = Any
PartyId = int


class GG18_KeyShare:
    """
    Key share for GG18 threshold ECDSA.
    
    Contains EC key share and Paillier keypair for MtA.
    
    Attributes:
        party_id: Party identifier (1 to n)
        x_i: Private key share
        X: Combined public key
        X_i: Verification key g^{x_i}
        paillier: Paillier keypair for this party
        other_paillier_pks: Dict of other parties' Paillier public keys
        t: Threshold parameter
        n: Total number of parties
    """
    
    def __init__(self, party_id: PartyId, private_share: ZRElement,
                 public_key: GElement, verification_key: GElement,
                 paillier: PaillierKeyPair, other_paillier_pks: Dict[PartyId, Dict],
                 threshold: int, num_parties: int):
        self.party_id = party_id
        self.x_i = private_share
        self.X = public_key
        self.X_i = verification_key
        self.paillier = paillier
        self.other_paillier_pks = other_paillier_pks
        self.t = threshold
        self.n = num_parties
    
    def __repr__(self) -> str:
        return f"GG18_KeyShare(party_id={self.party_id}, t={self.t}, n={self.n})"
    
    def get_paillier_pk(self, party_id: PartyId) -> Dict:
        """Get Paillier public key for a party."""
        if party_id == self.party_id:
            return self.paillier.pk
        return self.other_paillier_pks.get(party_id)


class GG18_DKG:
    """
    GG18 Distributed Key Generation (3 rounds).
    
    Generates threshold ECDSA keys with Paillier keypairs.
    Uses Feldman VSS for verifiable secret sharing.
    
    Curve Agnostic
    --------------
    Supports any DDH-hard elliptic curve group.
    
    >>> from charm.toolbox.eccurve import secp256k1
    >>> from charm.toolbox.integergroup import RSAGroup
    >>> group = ECGroup(secp256k1)
    >>> rsa_group = RSAGroup()
    >>> dkg = GG18_DKG(group, rsa_group, threshold=2, num_parties=3, paillier_bits=512)
    >>> g = group.random(G)
    >>> # Round 1
    >>> r1_results = [dkg.keygen_round1(i+1, g, b"session1") for i in range(3)]
    >>> round1_msgs = [r[0] for r in r1_results]
    >>> states = [r[1] for r in r1_results]
    >>> # Round 2
    >>> r2_results = [dkg.keygen_round2(i+1, states[i], round1_msgs) for i in range(3)]
    >>> shares_out = [r[0] for r in r2_results]
    >>> states = [r[1] for r in r2_results]
    >>> # Collect shares for each party
    >>> received = {}
    >>> for recv in range(1, 4):
    ...     received[recv] = {send+1: shares_out[send][recv] for send in range(3)}
    >>> # Round 3
    >>> key_shares = [dkg.keygen_round3(i+1, states[i], received[i+1], round1_msgs) for i in range(3)]
    >>> # All should have same public key
    >>> key_shares[0][0].X == key_shares[1][0].X == key_shares[2][0].X
    True
    """
    
    def __init__(self, ec_group: ECGroupType, rsa_group: RSAGroup,
                 threshold: int, num_parties: int, paillier_bits: int = 2048):
        """
        Initialize GG18 DKG.
        
        Args:
            ec_group: EC group (e.g., ECGroup(secp256k1))
            rsa_group: RSA group for Paillier
            threshold: Minimum parties to sign (t)
            num_parties: Total parties (n)
            paillier_bits: Paillier modulus bit length
        """
        if ec_group is None:
            raise ValueError("ec_group cannot be None")
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
    
    def keygen_round1(self, party_id: PartyId, generator: GElement,
                      session_id: bytes) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Round 1: Generate secret, commitments, and Paillier keypair.
        
        Args:
            party_id: This party's identifier (1 to n)
            generator: EC generator point g
            session_id: Unique session identifier
            
        Returns:
            Tuple of (broadcast_msg, private_state)
        """
        if session_id is None or len(session_id) == 0:
            raise ValueError("session_id is required")

        # Generate random secret
        secret = self.group.random(ZR)

        # Generate polynomial coefficients
        coeffs = [secret]
        for _ in range(self.t - 1):
            coeffs.append(self.group.random(ZR))

        # Compute Feldman commitments: C_j = g^{a_j}
        commitments = [generator ** coeff for coeff in coeffs]

        # Pre-compute shares for all parties
        shares = {}
        for j in range(1, self.n + 1):
            shares[j] = self._sharing._eval_polynomial(coeffs, j)

        # Generate Paillier keypair
        paillier_keypair = self._paillier_mta.generate_keypair()

        # Broadcast message
        broadcast_msg = {
            'party_id': party_id,
            'session_id': session_id,
            'commitments': commitments,
            'paillier_pk': paillier_keypair.pk,
        }

        # Private state
        private_state = {
            'party_id': party_id,
            'session_id': session_id,
            'secret': secret,
            'coefficients': coeffs,
            'shares': shares,
            'generator': generator,
            'paillier_keypair': paillier_keypair,
        }

        return broadcast_msg, private_state

    def keygen_round2(self, party_id: PartyId, private_state: Dict[str, Any],
                      all_round1_msgs: List[Dict[str, Any]]) -> Tuple[Dict[PartyId, ZRElement], Dict[str, Any]]:
        """
        Round 2: Verify round 1, prepare shares for other parties.

        Args:
            party_id: This party's identifier
            private_state: Private state from round 1
            all_round1_msgs: Broadcast messages from all parties

        Returns:
            Tuple of (shares_for_others, updated_state)
        """
        # Verify we have messages from all parties
        received_ids = set(msg['party_id'] for msg in all_round1_msgs)
        expected_ids = set(range(1, self.n + 1))
        if received_ids != expected_ids:
            raise ValueError(f"Missing round 1 messages from: {expected_ids - received_ids}")

        # Verify commitment lengths
        for msg in all_round1_msgs:
            if len(msg['commitments']) != self.t:
                raise ValueError(f"Party {msg['party_id']} has wrong number of commitments")

        # Prepare shares to send
        shares_to_send = private_state['shares'].copy()

        # Store round 1 messages
        updated_state = private_state.copy()
        updated_state['all_round1_msgs'] = {msg['party_id']: msg for msg in all_round1_msgs}

        return shares_to_send, updated_state

    def keygen_round3(self, party_id: PartyId, private_state: Dict[str, Any],
                      received_shares: Dict[PartyId, ZRElement],
                      all_round1_msgs: List[Dict[str, Any]]) -> Tuple[Optional[GG18_KeyShare], Optional[Dict[str, Any]]]:
        """
        Round 3: Verify shares, compute final key share.

        Args:
            party_id: This party's identifier
            private_state: Private state from round 2
            received_shares: Shares received from all parties
            all_round1_msgs: Broadcast messages from round 1

        Returns:
            Tuple of (KeyShare or None, complaint or None)
        """
        generator = private_state['generator']
        round1_by_party = {msg['party_id']: msg for msg in all_round1_msgs}

        # Verify all received shares
        for sender_id, share in received_shares.items():
            commitments = round1_by_party[sender_id]['commitments']
            if not self._sharing.verify_share(party_id, share, commitments, generator):
                complaint = {
                    'accuser': party_id,
                    'accused': sender_id,
                    'share': share,
                }
                return None, complaint

        # Compute final share: x_i = sum of all shares received
        final_share = self.group.init(ZR, 0)
        for share in received_shares.values():
            final_share = final_share + share

        # Compute verification key
        verification_key = generator ** final_share

        # Compute public key: product of first commitments
        public_key = round1_by_party[1]['commitments'][0]
        for pid in range(2, self.n + 1):
            public_key = public_key * round1_by_party[pid]['commitments'][0]

        # Collect other parties' Paillier public keys
        other_paillier_pks = {}
        for msg in all_round1_msgs:
            if msg['party_id'] != party_id:
                other_paillier_pks[msg['party_id']] = msg['paillier_pk']

        key_share = GG18_KeyShare(
            party_id=party_id,
            private_share=final_share,
            public_key=public_key,
            verification_key=verification_key,
            paillier=private_state['paillier_keypair'],
            other_paillier_pks=other_paillier_pks,
            threshold=self.t,
            num_parties=self.n
        )

        return key_share, None

    def compute_public_key(self, all_commitments: List[List[GElement]]) -> GElement:
        """Compute combined public key from all parties' commitments."""
        if not all_commitments:
            raise ValueError("Need at least one commitment list")

        public_key = all_commitments[0][0]
        for i in range(1, len(all_commitments)):
            public_key = public_key * all_commitments[i][0]

        return public_key

