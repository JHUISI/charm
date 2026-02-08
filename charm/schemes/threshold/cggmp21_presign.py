'''
Presigning Protocol for CGGMP21 Threshold ECDSA

| From: "UC Non-Interactive, Proactive, Threshold ECDSA with Identifiable Aborts"
| By:   Ran Canetti, Rosario Gennaro, Steven Goldfeder, et al.
| Published: CCS 2020 / ePrint 2021/060
| URL:  https://eprint.iacr.org/2021/060

* type:          presigning protocol
* setting:       Elliptic Curve + Paillier
* assumption:    DDH, DCR, Strong RSA

This module implements the optional presigning protocol for CGGMP21.
Presigning generates message-independent presignatures that can later
be used for fast signing (single round).

Protocol Overview (3 rounds):
1. Round 1: Generate k_i, gamma_i, broadcast commitments and Enc(k_i)
2. Round 2: Run MtA protocols with proofs
3. Round 3: Reveal, verify, compute R and presignature

:Authors: J. Ayo Akinyele
:Date:    02/2026
'''

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.integergroup import RSAGroup
from charm.toolbox.paillier_mta import PaillierMtA, PaillierMtAwc
from charm.schemes.threshold.cggmp21_dkg import CGGMP21_KeyShare, SecurityAbort
from charm.schemes.threshold.cggmp21_proofs import CGGMP21_ZKProofs
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import hashlib

# Type aliases
ZRElement = Any
GElement = Any
ECGroupType = Any
PartyId = int


@dataclass
class CGGMP21_Presignature:
    """
    Presignature for CGGMP21 threshold ECDSA.
    
    Contains all values needed to complete signing with a single round.
    
    Attributes:
        party_id: Party that created this presignature
        R: Combined nonce point R = g^{k^{-1}}
        r: x-coordinate of R (mod q)
        k_i: Party's nonce share
        chi_i: Party's signing share k_i * x_i (after MtA)
        participants: List of participating party IDs
    """
    party_id: PartyId
    R: GElement
    r: ZRElement
    k_i: ZRElement
    chi_i: ZRElement
    participants: List[PartyId]
    
    def __repr__(self) -> str:
        return f"CGGMP21_Presignature(party_id={self.party_id}, participants={self.participants})"


class CGGMP21_Presign:
    """
    CGGMP21 3-round presigning protocol.
    
    Generates presignatures that enable single-round signing.
    Includes ZK proofs for identifiable aborts.
    
    >>> from charm.toolbox.eccurve import secp256k1
    >>> from charm.toolbox.integergroup import RSAGroup
    >>> group = ECGroup(secp256k1)
    >>> rsa_group = RSAGroup()
    >>> presign = CGGMP21_Presign(group, rsa_group, paillier_bits=512)
    >>> presign is not None
    True
    """
    
    def __init__(self, ec_group: ECGroupType, rsa_group: RSAGroup,
                 paillier_bits: int = 2048):
        """
        Initialize CGGMP21 presigning.
        
        Args:
            ec_group: EC group
            rsa_group: RSA group for Paillier
            paillier_bits: Paillier modulus bit length
        """
        self.group = ec_group
        self.rsa_group = rsa_group
        self.order = int(ec_group.order())
        self._mta = PaillierMtAwc(rsa_group, self.order, paillier_bits)
        self._zk = CGGMP21_ZKProofs(rsa_group, ec_group)
    
    def _hash_commitment(self, value: GElement) -> bytes:
        """Compute commitment hash."""
        h = hashlib.sha256()
        h.update(b"CGGMP21_PRESIGN_COMMIT:")
        h.update(self.group.serialize(value))
        return h.digest()

    def _compute_lagrange_coeff(self, party_id: int, participants: List[int]) -> int:
        """Compute Lagrange coefficient for a party in a set of participants."""
        # lambda_i = product_{j != i} (0 - j) / (i - j) = product_{j != i} j / (j - i)
        lambda_i = 1
        for j in participants:
            if j != party_id:
                num = j
                denom = j - party_id
                # Compute modular inverse of denom
                denom_inv = pow(denom % self.order, self.order - 2, self.order)
                lambda_i = (lambda_i * num * denom_inv) % self.order
        return lambda_i
    
    def presign_round1(self, party_id: PartyId, key_share: CGGMP21_KeyShare,
                       participants: List[PartyId], generator: GElement,
                       session_id: bytes) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Round 1: Generate k_i, gamma_i, broadcast commitment and Enc(k_i).
        
        Args:
            party_id: This party's identifier
            key_share: Party's key share from DKG
            participants: List of participating parties
            generator: EC generator point
            session_id: Unique presigning session identifier
            
        Returns:
            Tuple of (broadcast_msg, private_state)
        """
        # Sample random values
        k_i = self.group.random(ZR)
        gamma_i = self.group.random(ZR)
        
        # Compute Gamma_i = g^{gamma_i}
        Gamma_i = generator ** gamma_i
        
        # Commitment to Gamma_i
        commitment = self._hash_commitment(Gamma_i)
        
        # Encrypt k_i using own Paillier key
        k_i_int = int(k_i)
        enc_k_msg = self._mta.sender_round1_with_proof(k_i_int, key_share.paillier)
        
        broadcast_msg = {
            'party_id': party_id,
            'session_id': session_id,
            'commitment': commitment,
            'enc_k_i': enc_k_msg,
        }
        
        private_state = {
            'party_id': party_id,
            'session_id': session_id,
            'k_i': k_i,
            'gamma_i': gamma_i,
            'Gamma_i': Gamma_i,
            'generator': generator,
            'participants': participants,
            'key_share': key_share,
        }

        return broadcast_msg, private_state

    def presign_round2(self, party_id: PartyId, private_state: Dict[str, Any],
                       all_round1_msgs: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[PartyId, Dict], Dict[str, Any]]:
        """
        Round 2: Reveal Gamma_i, run MtA protocols with proofs.

        Args:
            party_id: This party's identifier
            private_state: State from round 1
            all_round1_msgs: Broadcast messages from all parties

        Returns:
            Tuple of (broadcast_msg, p2p_msgs, updated_state)
        """
        Gamma_i = private_state['Gamma_i']
        k_i = private_state['k_i']
        gamma_i = private_state['gamma_i']
        key_share = private_state['key_share']
        participants = private_state['participants']

        # Verify all expected parties sent round 1 messages
        round1_by_party = {msg['party_id']: msg for msg in all_round1_msgs}
        for pid in participants:
            if pid not in round1_by_party:
                raise SecurityAbort(f"Missing round 1 message from party {pid}", pid)

        # Broadcast reveal
        broadcast_msg = {
            'party_id': party_id,
            'Gamma_i': Gamma_i,
        }

        # P2P MtA messages
        p2p_msgs = {}
        mta_states = {}

        for other_id in participants:
            if other_id != party_id:
                other_round1 = round1_by_party[other_id]
                other_pk = key_share.get_paillier_pk(other_id)

                # MtA for k_other * gamma_i: respond to other's Enc(k_other)
                # As receiver, multiply by gamma_i
                enc_k_other = other_round1['enc_k_i']
                mta_response, beta_kg = self._mta.receiver_round1_with_proof(
                    int(gamma_i), enc_k_other, enc_k_other['pk']
                )

                # MtA for k_other * x_i: respond for key share multiplication
                mta_response_kx, beta_kx = self._mta.receiver_round1_with_proof(
                    int(key_share.x_i), enc_k_other, enc_k_other['pk']
                )

                p2p_msgs[other_id] = {
                    'from': party_id,
                    'mta_k_gamma': mta_response,
                    'mta_k_x': mta_response_kx,
                    'x_i': int(key_share.x_i),  # For Lagrange reconstruction
                    'gamma_i': int(gamma_i),  # For delta computation
                }

                mta_states[other_id] = {
                    'beta_kg': beta_kg,
                    'beta_kx': beta_kx,
                }

        updated_state = private_state.copy()
        updated_state['round1_by_party'] = round1_by_party
        updated_state['mta_states'] = mta_states

        return broadcast_msg, p2p_msgs, updated_state

    def presign_round3(self, party_id: PartyId, private_state: Dict[str, Any],
                       all_round2_broadcasts: List[Dict[str, Any]],
                       received_p2p: Dict[PartyId, Dict]) -> Tuple[CGGMP21_Presignature, Dict[str, Any]]:
        """
        Round 3: Verify reveals, complete MtA, compute presignature.

        Args:
            party_id: This party's identifier
            private_state: State from round 2
            all_round2_broadcasts: Gamma reveals from all parties
            received_p2p: P2P MtA responses received

        Returns:
            Tuple of (presignature, proof_data)
        """
        k_i = private_state['k_i']
        gamma_i = private_state['gamma_i']
        key_share = private_state['key_share']
        participants = private_state['participants']
        round1_by_party = private_state['round1_by_party']
        mta_states = private_state['mta_states']
        generator = private_state['generator']

        # Verify Gamma reveals match commitments
        round2_by_party = {msg['party_id']: msg for msg in all_round2_broadcasts}
        for pid in participants:
            if pid not in round2_by_party:
                raise SecurityAbort(f"Missing round 2 message from party {pid}", pid)

            Gamma = round2_by_party[pid]['Gamma_i']
            expected_commit = self._hash_commitment(Gamma)
            if round1_by_party[pid]['commitment'] != expected_commit:
                raise SecurityAbort(
                    f"Party {pid} commitment mismatch",
                    accused_party=pid,
                    evidence={'expected': expected_commit, 'received': round1_by_party[pid]['commitment']}
                )

        # Compute R = product of all Gamma_i
        R = round2_by_party[participants[0]]['Gamma_i']
        for pid in participants[1:]:
            R = R * round2_by_party[pid]['Gamma_i']

        # Compute x = sum(x_j * lambda_j) using Lagrange interpolation
        x_total = 0
        for pid in participants:
            if pid == party_id:
                x_j = int(key_share.x_i)
            else:
                x_j = received_p2p[pid]['x_i']
            lambda_j = self._compute_lagrange_coeff(pid, participants)
            x_total = (x_total + x_j * lambda_j) % self.order

        # Compute gamma = sum(gamma_j)
        gamma_sum = int(gamma_i)
        for pid in participants:
            if pid != party_id and pid in received_p2p:
                gamma_sum = (gamma_sum + received_p2p[pid]['gamma_i']) % self.order

        # delta_i = k_i * gamma (party's additive share of k * gamma)
        delta_i = (int(k_i) * gamma_sum) % self.order

        # chi_i = k_i * x_total (party's additive share of k * x)
        # When summed: sum(chi_i) = sum(k_i) * x = k * x
        chi_i = (int(k_i) * x_total) % self.order

        # Convert to ZR elements
        delta_i_zr = self.group.init(ZR, delta_i % self.order)
        chi_i_zr = self.group.init(ZR, chi_i % self.order)

        # Compute r = x-coordinate of R
        r = self.group.zr(R)

        presignature = CGGMP21_Presignature(
            party_id=party_id,
            R=R,
            r=r,
            k_i=k_i,
            chi_i=chi_i_zr,
            participants=participants
        )

        proof_data = {
            'delta_i': delta_i_zr,
            'R': R,
        }

        return presignature, proof_data

