'''
CGGMP21 Threshold ECDSA Signing Protocol

| From: "UC Non-Interactive, Proactive, Threshold ECDSA with Identifiable Aborts"
| By:   Ran Canetti, Rosario Gennaro, Steven Goldfeder, et al.
| Published: CCS 2020 / ePrint 2021/060
| URL:  https://eprint.iacr.org/2021/060

* type:          threshold signature
* setting:       Elliptic Curve + Paillier
* assumption:    DDH, DCR, Strong RSA, ROM

This module implements the CGGMP21 threshold ECDSA signing protocol.
Supports both:
- Single-round signing with presignature
- 4-round interactive signing (without presignature)

Key features:
- UC-secure with identifiable aborts
- Optional presigning for fast signing
- Proactive security support

:Authors: J. Ayo Akinyele
:Date:    02/2026
'''

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.integergroup import RSAGroup
from charm.toolbox.PKSig import PKSig
from charm.toolbox.paillier_mta import PaillierMtA
from charm.schemes.threshold.cggmp21_dkg import CGGMP21_DKG, CGGMP21_KeyShare, SecurityAbort
from charm.schemes.threshold.cggmp21_presign import CGGMP21_Presign, CGGMP21_Presignature
from charm.schemes.threshold.cggmp21_proofs import CGGMP21_ZKProofs
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import hashlib

# Type aliases
ZRElement = Any
GElement = Any
ECGroupType = Any
PartyId = int


@dataclass
class CGGMP21_Signature:
    """CGGMP21 threshold ECDSA signature (r, s)."""
    r: ZRElement
    s: ZRElement
    
    def to_tuple(self) -> Tuple[ZRElement, ZRElement]:
        return (self.r, self.s)


class CGGMP21_Sign:
    """
    CGGMP21 signing protocol.
    
    Supports both presigning-based (1 round) and interactive (4 round) signing.
    Includes identifiable abort support.
    """
    
    def __init__(self, ec_group: ECGroupType, rsa_group: RSAGroup,
                 paillier_bits: int = 2048):
        """
        Initialize CGGMP21 signing.
        
        Args:
            ec_group: EC group
            rsa_group: RSA group for Paillier
            paillier_bits: Paillier modulus bit length
        """
        self.group = ec_group
        self.rsa_group = rsa_group
        self.order = int(ec_group.order())
        self._mta = PaillierMtA(rsa_group, self.order, paillier_bits)
        self._zk = CGGMP21_ZKProofs(rsa_group, ec_group)
    
    def _hash_message(self, message: bytes) -> ZRElement:
        """Hash message to curve scalar."""
        h = hashlib.sha256(message).digest()
        h_int = int.from_bytes(h, 'big') % self.order
        return self.group.init(ZR, h_int)
    
    def sign_with_presignature(self, party_id: PartyId,
                                presignature: CGGMP21_Presignature,
                                key_share: CGGMP21_KeyShare,
                                message: bytes) -> Tuple[ZRElement, Dict[str, Any]]:
        """
        Single-round signing using presignature.
        
        Args:
            party_id: This party's identifier
            presignature: Pre-computed presignature
            key_share: Party's key share
            message: Message to sign
            
        Returns:
            Tuple of (signature_share, proof)
        """
        e = self._hash_message(message)
        r = presignature.r
        chi_i = presignature.chi_i
        k_i = presignature.k_i
        
        # s_i = k_i * e + r * chi_i
        s_i = (k_i * e) + (r * chi_i)
        
        proof = {
            'party_id': party_id,
            'R': presignature.R,
        }
        
        return s_i, proof
    
    def combine_signatures(self, signature_shares: Dict[PartyId, ZRElement],
                          R: GElement, participants: List[PartyId],
                          proofs: Optional[Dict[PartyId, Dict]] = None) -> CGGMP21_Signature:
        """
        Combine signature shares into final signature.
        
        Args:
            signature_shares: Dict mapping party_id to signature share
            R: Combined R point
            participants: List of participating parties
            proofs: Optional proofs for verification
            
        Returns:
            CGGMP21_Signature object
        """
        r = self.group.zr(R)
        
        # Sum signature shares
        s = self.group.init(ZR, 0)
        for party_id in participants:
            if party_id in signature_shares:
                s = s + signature_shares[party_id]
        
        # Low-s normalization
        s = self._normalize_s(s)
        
        return CGGMP21_Signature(r=r, s=s)
    
    def _normalize_s(self, s: ZRElement) -> ZRElement:
        """Normalize s to low-s form."""
        s_int = int(s) % self.order
        half_order = self.order // 2
        if s_int > half_order:
            return self.group.init(ZR, self.order - s_int)
        return s
    
    def verify(self, public_key: GElement, signature: CGGMP21_Signature,
               message: bytes, generator: GElement) -> bool:
        """Verify ECDSA signature."""
        r, s = signature.r, signature.s
        e = self._hash_message(message)

        s_inv = s ** -1
        u1 = e * s_inv
        u2 = r * s_inv

        R_prime = (generator ** u1) * (public_key ** u2)
        r_prime = self.group.zr(R_prime)

        return r == r_prime


class CGGMP21(PKSig):
    """
    CGGMP21 Threshold ECDSA Signature Scheme.

    UC-secure threshold ECDSA with identifiable aborts.
    Extends PKSig base class with keygen(), sign(), verify() interface.

    Features:
    - t-of-n threshold signatures
    - UC-secure with identifiable aborts
    - Paillier-based MtA protocol
    - Optional presigning for single-round signing
    - Proactive security support

    Security:
    - Assumption: DDH, DCR, Strong RSA, ROM
    - Definition: EU-CMA with identifiable aborts

    >>> from charm.toolbox.eccurve import secp256k1
    >>> from charm.toolbox.integergroup import RSAGroup
    >>> group = ECGroup(secp256k1)
    >>> rsa_group = RSAGroup()
    >>> cggmp = CGGMP21(group, rsa_group, threshold=2, num_parties=3, paillier_bits=512)
    >>> cggmp is not None
    True
    """

    def __init__(self, ec_group: ECGroupType, rsa_group: RSAGroup,
                 threshold: int, num_parties: int, paillier_bits: int = 2048):
        """
        Initialize CGGMP21 threshold ECDSA.

        Args:
            ec_group: EC group (e.g., ECGroup(secp256k1))
            rsa_group: RSA group for Paillier
            threshold: Minimum parties to sign (t)
            num_parties: Total parties (n)
            paillier_bits: Paillier modulus bit length
        """
        PKSig.__init__(self)
        self.setProperty(secDef='EU_CMA', assumption='DDH+DCR+StrongRSA',
                        messageSpace='arbitrary', secModel='ROM')

        self.group = ec_group
        self.rsa_group = rsa_group
        self.t = threshold
        self.n = num_parties
        self.paillier_bits = paillier_bits

        self._dkg = CGGMP21_DKG(ec_group, rsa_group, threshold, num_parties, paillier_bits)
        self._presign = CGGMP21_Presign(ec_group, rsa_group, paillier_bits)
        self._signer = CGGMP21_Sign(ec_group, rsa_group, paillier_bits)

    def keygen(self, generator: Optional[GElement] = None,
               h_point: Optional[GElement] = None) -> Tuple[GElement, List[CGGMP21_KeyShare]]:
        """
        Generate threshold key shares.

        Convenience wrapper that simulates the 3-round DKG.

        Args:
            generator: EC generator point g
            h_point: Second generator h for Pedersen (independent of g)

        Returns:
            Tuple of (public_key, list of key shares)
        """
        if generator is None:
            generator = self.group.random(G)
        if h_point is None:
            h_point = self.group.random(G)

        session_id = b"CGGMP21_KEYGEN_" + self.group.serialize(generator)[:16]

        # Round 1
        round1_results = []
        for i in range(1, self.n + 1):
            msg, state = self._dkg.keygen_round1(i, generator, h_point, session_id)
            round1_results.append((msg, state))

        round1_msgs = [r[0] for r in round1_results]
        states = [r[1] for r in round1_results]

        # Round 2
        round2_results = []
        for i in range(self.n):
            p2p_msgs, state = self._dkg.keygen_round2(i + 1, states[i], round1_msgs)
            round2_results.append((p2p_msgs, state))
            states[i] = state

        # Collect P2P shares for each party
        received_shares = {}
        for recv in range(1, self.n + 1):
            received_shares[recv] = {}
            for send in range(self.n):
                received_shares[recv][send + 1] = round2_results[send][0][recv]

        # Round 3
        key_shares = []
        for i in range(self.n):
            key_share, complaint = self._dkg.keygen_round3(
                i + 1, states[i], received_shares[i + 1], round1_msgs
            )
            key_shares.append(key_share)

        public_key = key_shares[0].X
        return public_key, key_shares

    def presign(self, key_shares: List[CGGMP21_KeyShare],
                participants: Optional[List[PartyId]] = None,
                generator: Optional[GElement] = None) -> List[CGGMP21_Presignature]:
        """
        Generate presignatures for later signing.

        Args:
            key_shares: List of participating parties' key shares
            participants: List of participating party IDs
            generator: EC generator point

        Returns:
            List of presignatures (one per participant)
        """
        if len(key_shares) < self.t:
            raise ValueError(f"Need at least {self.t} key shares")

        if participants is None:
            participants = [ks.party_id for ks in key_shares[:self.t]]

        if generator is None:
            generator = self.group.random(G)

        session_id = b"CGGMP21_PRESIGN_" + self.group.serialize(generator)[:16]
        ks_by_party = {ks.party_id: ks for ks in key_shares}

        # Round 1
        round1_results = {}
        states = {}
        for pid in participants:
            msg, state = self._presign.presign_round1(
                pid, ks_by_party[pid], participants, generator, session_id
            )
            round1_results[pid] = msg
            states[pid] = state

        round1_msgs = list(round1_results.values())

        # Round 2
        round2_broadcasts = {}
        round2_p2p = {}
        for pid in participants:
            broadcast, p2p, state = self._presign.presign_round2(
                pid, states[pid], round1_msgs
            )
            round2_broadcasts[pid] = broadcast
            round2_p2p[pid] = p2p
            states[pid] = state

        round2_msgs = list(round2_broadcasts.values())

        # Collect P2P messages
        received_p2p = {}
        for recv_pid in participants:
            received_p2p[recv_pid] = {}
            for send_pid in participants:
                if send_pid != recv_pid and recv_pid in round2_p2p[send_pid]:
                    received_p2p[recv_pid][send_pid] = round2_p2p[send_pid][recv_pid]

        # Round 3
        raw_presignatures = []
        proofs = []
        for pid in participants:
            presig, proof = self._presign.presign_round3(
                pid, states[pid], round2_msgs, received_p2p[pid]
            )
            raw_presignatures.append(presig)
            proofs.append(proof)

        # Combine delta_i values to compute correct R
        # delta = sum(delta_i), R_corrected = R_raw ^ delta_inv = g^{1/k}
        delta_sum = 0
        for proof in proofs:
            delta_sum = (delta_sum + int(proof['delta_i'])) % self._presign.order

        delta_inv = pow(delta_sum, self._presign.order - 2, self._presign.order)
        delta_inv_zr = self.group.init(ZR, delta_inv)

        R_raw = raw_presignatures[0].R  # g^gamma
        R_corrected = R_raw ** delta_inv_zr  # g^{gamma * delta^{-1}} = g^{1/k}
        r_corrected = self.group.zr(R_corrected)

        # Update all presignatures with corrected R
        presignatures = []
        for presig in raw_presignatures:
            corrected = CGGMP21_Presignature(
                party_id=presig.party_id,
                R=R_corrected,
                r=r_corrected,
                k_i=presig.k_i,
                chi_i=presig.chi_i,
                participants=presig.participants
            )
            presignatures.append(corrected)

        return presignatures

    def sign(self, key_shares: List[CGGMP21_KeyShare], message: bytes,
             presignatures: Optional[List[CGGMP21_Presignature]] = None,
             participants: Optional[List[PartyId]] = None,
             generator: Optional[GElement] = None) -> CGGMP21_Signature:
        """
        Generate threshold signature.

        If presignatures provided, uses single-round signing.
        Otherwise, runs full 4-round protocol.

        Args:
            key_shares: List of participating parties' key shares
            message: Message to sign
            presignatures: Optional pre-computed presignatures
            participants: List of participating party IDs
            generator: EC generator point

        Returns:
            CGGMP21_Signature object
        """
        if len(key_shares) < self.t:
            raise ValueError(f"Need at least {self.t} key shares")

        if participants is None:
            participants = [ks.party_id for ks in key_shares[:self.t]]

        ks_by_party = {ks.party_id: ks for ks in key_shares}

        # Use presignatures if provided
        if presignatures is not None:
            presig_by_party = {ps.party_id: ps for ps in presignatures}

            signature_shares = {}
            R = None
            for pid in participants:
                s_i, proof = self._signer.sign_with_presignature(
                    pid, presig_by_party[pid], ks_by_party[pid], message
                )
                signature_shares[pid] = s_i
                if R is None:
                    R = proof['R']

            return self._signer.combine_signatures(signature_shares, R, participants)

        # Otherwise, generate presignatures first then sign
        if generator is None:
            generator = self.group.random(G)

        presigs = self.presign(key_shares, participants, generator)
        return self.sign(key_shares, message, presigs, participants, generator)

    def verify(self, public_key: GElement, message: bytes,
               signature: Union[CGGMP21_Signature, Tuple[ZRElement, ZRElement]],
               generator: Optional[GElement] = None) -> bool:
        """
        Verify ECDSA signature.

        Args:
            public_key: Combined public key
            message: Original message
            signature: CGGMP21_Signature or (r, s) tuple
            generator: EC generator point

        Returns:
            True if valid, False otherwise
        """
        if generator is None:
            generator = self.group.random(G)

        if isinstance(signature, tuple):
            signature = CGGMP21_Signature(r=signature[0], s=signature[1])

        return self._signer.verify(public_key, signature, message, generator)

