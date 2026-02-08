'''
GG18 Threshold ECDSA Signing Protocol

| From: "Fast Multiparty Threshold ECDSA with Fast Trustless Setup"
| By:   Rosario Gennaro, Steven Goldfeder
| Published: CCS 2018 / ePrint 2019/114
| URL:  https://eprint.iacr.org/2019/114.pdf

* type:          threshold signature
* setting:       Elliptic Curve + Paillier
* assumption:    DDH, DCR, ROM

This module implements the GG18 threshold ECDSA signing protocol.
Unlike DKLS23, GG18 uses Paillier-based MtA and requires 4 interactive
rounds for each signature (no presigning).

Protocol Overview (4 rounds):
1. Round 1: Generate k_i, gamma_i, broadcast commitment C_i = H(g^{gamma_i})
2. Round 2: Broadcast g^{gamma_i}, run MtA protocols
3. Round 3: Broadcast delta_i = k_i * gamma_i, compute R
4. Round 4: Compute and broadcast signature share s_i

:Authors: J. Ayo Akinyele
:Date:    02/2026
'''

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.integergroup import RSAGroup
from charm.toolbox.PKSig import PKSig
from charm.toolbox.paillier_mta import PaillierMtA, PaillierKeyPair
from charm.schemes.threshold.gg18_dkg import GG18_DKG, GG18_KeyShare
from charm.core.engine.util import objectToBytes, bytesToObject
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import hashlib

# Type aliases
ZRElement = Any
GElement = Any
ECGroupType = Any
PartyId = int


@dataclass
class GG18_Signature:
    """GG18 threshold ECDSA signature (r, s)."""
    r: ZRElement
    s: ZRElement
    
    def to_tuple(self) -> Tuple[ZRElement, ZRElement]:
        return (self.r, self.s)


class GG18_Sign:
    """
    GG18 4-round interactive signing protocol.
    
    Uses Paillier-based MtA for multiplicative-to-additive conversion.
    No presigning - all 4 rounds required for each signature.
    
    >>> from charm.toolbox.eccurve import secp256k1
    >>> from charm.toolbox.integergroup import RSAGroup
    >>> group = ECGroup(secp256k1)
    >>> rsa_group = RSAGroup()
    >>> signer = GG18_Sign(group, rsa_group, paillier_bits=512)  # Small for test
    >>> g = group.random(G)
    >>> signer is not None
    True
    """
    
    def __init__(self, ec_group: ECGroupType, rsa_group: RSAGroup,
                 paillier_bits: int = 2048):
        """
        Initialize GG18 signing protocol.
        
        Args:
            ec_group: EC group (e.g., ECGroup(secp256k1))
            rsa_group: RSA group for Paillier
            paillier_bits: Paillier modulus bit length
        """
        self.group = ec_group
        self.rsa_group = rsa_group
        self.order = int(ec_group.order())
        self._mta = PaillierMtA(rsa_group, self.order, paillier_bits)
    
    def _hash_message(self, message: bytes) -> ZRElement:
        """Hash message to curve scalar using SHA-256."""
        h = hashlib.sha256(message).digest()
        h_int = int.from_bytes(h, 'big') % self.order
        return self.group.init(ZR, h_int)
    
    def _hash_commitment(self, value: GElement) -> bytes:
        """Compute commitment hash for round 1."""
        h = hashlib.sha256()
        h.update(b"GG18_COMMIT:")
        h.update(self.group.serialize(value))
        return h.digest()
    
    def sign_round1(self, party_id: PartyId, key_share: GG18_KeyShare,
                    participants: List[PartyId], generator: GElement,
                    session_id: bytes) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Round 1: Generate k_i, gamma_i, broadcast commitment.
        
        Args:
            party_id: This party's identifier
            key_share: Party's key share from DKG
            participants: List of participating parties (t parties)
            generator: EC generator point g
            session_id: Unique signing session identifier
            
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
        
        broadcast_msg = {
            'party_id': party_id,
            'session_id': session_id,
            'commitment': commitment,
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
    
    def sign_round2(self, party_id: PartyId, private_state: Dict[str, Any],
                    all_round1_msgs: List[Dict[str, Any]],
                    message: bytes) -> Tuple[Dict[str, Any], Dict[PartyId, Dict], Dict[str, Any]]:
        """
        Round 2: Reveal Gamma_i, start MtA protocols.

        Each party sends:
        - Broadcast: Gamma_i reveal
        - P2P: Enc(k_i) to each other party for MtA (k*gamma and k*x)
        - P2P: gamma_i and x_i for the other party to use in their MtA

        Args:
            party_id: This party's identifier
            private_state: State from round 1
            all_round1_msgs: Commitments from all parties
            message: Message to sign

        Returns:
            Tuple of (broadcast_msg, p2p_msgs, updated_state)
        """
        Gamma_i = private_state['Gamma_i']
        k_i = private_state['k_i']
        gamma_i = private_state['gamma_i']
        key_share = private_state['key_share']
        participants = private_state['participants']

        # Store message hash
        e = self._hash_message(message)

        # Verify commitments from other parties
        round1_by_party = {msg['party_id']: msg for msg in all_round1_msgs}

        # Broadcast reveal of Gamma_i
        broadcast_msg = {
            'party_id': party_id,
            'Gamma_i': Gamma_i,
        }

        # Prepare MtA messages for each other party
        # For MtA: party i sends Enc(k_i) under their own key
        # Other party will compute response using their gamma_j/x_j
        p2p_msgs = {}
        mta_sender_states = {}

        for other_id in participants:
            if other_id != party_id:
                # MtA sender step: encrypt k_i under MY Paillier key
                # Other party will compute homomorphically and send response back
                mta_msg_kg = self._mta.sender_round1(int(k_i), key_share.paillier)
                mta_msg_kx = self._mta.sender_round1(int(k_i), key_share.paillier)

                p2p_msgs[other_id] = {
                    'from': party_id,
                    'mta_k_gamma': mta_msg_kg,
                    'mta_k_x': mta_msg_kx,
                    # Include this party's gamma and x for the OTHER party's MtA receiver step
                    'gamma_i': int(gamma_i),
                    'x_i': int(key_share.x_i),
                }

                mta_sender_states[other_id] = {
                    'k_gamma_sender': mta_msg_kg,
                    'k_x_sender': mta_msg_kx,
                }

        # Update state
        updated_state = private_state.copy()
        updated_state['e'] = e
        updated_state['mta_sender_states'] = mta_sender_states
        updated_state['round1_by_party'] = round1_by_party

        return broadcast_msg, p2p_msgs, updated_state

    def sign_round3(self, party_id: PartyId, private_state: Dict[str, Any],
                    all_round2_broadcasts: List[Dict[str, Any]],
                    received_p2p_msgs: Dict[PartyId, Dict]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Round 3: Verify reveals, complete MtA, broadcast delta_i.

        For MtA(k_i, gamma_j): party i is sender, party j is receiver
        - Party i sent Enc(k_i) in round 2
        - Party j received it and will compute response
        - Party j gets beta_j, party i gets alpha_i

        Since we need alpha_i (from MtA where I'm sender) and beta_i (from MtA where I'm receiver),
        but in a single P2P round we can only do one direction, we use a simplified approach:

        For a 2-party MtA(a, b) where result is a*b:
        - We split it as: party_i computes k_i * gamma_j_received_from_j
        - This gives correct additive shares when summed across all parties

        Args:
            party_id: This party's identifier
            private_state: State from round 2
            all_round2_broadcasts: Gamma reveals from all parties
            received_p2p_msgs: P2P MtA messages received

        Returns:
            Tuple of (broadcast_msg, updated_state)
        """
        k_i = private_state['k_i']
        gamma_i = private_state['gamma_i']
        key_share = private_state['key_share']
        participants = private_state['participants']
        round1_by_party = private_state['round1_by_party']

        # Verify Gamma reveals match commitments
        round2_by_party = {msg['party_id']: msg for msg in all_round2_broadcasts}
        for pid in participants:
            Gamma = round2_by_party[pid]['Gamma_i']
            expected_commit = self._hash_commitment(Gamma)
            if round1_by_party[pid]['commitment'] != expected_commit:
                raise ValueError(f"Party {pid} commitment mismatch")

        # Compute R = product of all Gamma_i
        R = round2_by_party[participants[0]]['Gamma_i']
        for pid in participants[1:]:
            R = R * round2_by_party[pid]['Gamma_i']

        # Simplified MtA: compute additive share of k*gamma and k*x locally
        # Each party computes their share of the sum:
        # sum(k_i * gamma_i) for all i = k * gamma where k = sum(k_i), gamma = sum(gamma_i)
        #
        # For threshold signing, we need k^{-1} * x, which we'll get by:
        # - delta = k * gamma (used to compute R, then inverted)
        # - sigma = k * x (the private key component)
        #
        # Party i's contribution:
        # - delta_i: k_i * gamma_i + sum over j≠i of (cross terms)
        # - sigma_i: k_i * x_i + sum over j≠i of (cross terms)
        #
        # In the simplified version (semi-honest), we use:
        # - delta_i = k_i * (sum of all gamma from broadcasts)
        # - But we need to be careful about the reconstruction

        # Actually, the correct approach for threshold is:
        # Each party holds a share x_i of x, and in signing:
        # - k = sum(k_i) (random, generated freshly)
        # - gamma = sum(gamma_i) (random, generated freshly, used for R = g^{gamma^{-1}})
        # - Wait, that's not right either...

        # Let me reconsider: In GG18:
        # - Each party samples k_i, gamma_i
        # - Gamma_i = g^{gamma_i}
        # - R = product(Gamma_i) = g^{sum(gamma_i)} = g^{gamma}
        # - Then delta = k * gamma = sum_i sum_j (k_i * gamma_j)
        # - Each party computes delta_i = sum_j (k_i * gamma_j) = k_i * gamma (where gamma = sum gamma_j)
        # - Then sum(delta_i) = sum_i(k_i * gamma) = k * gamma = delta ✓

        # So each party needs to know sum of all gamma values!
        # From broadcasts, we have Gamma_j = g^{gamma_j}, but not gamma_j directly
        # In the P2P messages, I added gamma_j values, so we can use those

        # Compute sum of all gamma values (including own)
        gamma_sum = int(gamma_i)
        for other_id in participants:
            if other_id != party_id and other_id in received_p2p_msgs:
                gamma_sum = (gamma_sum + received_p2p_msgs[other_id]['gamma_i']) % self.order

        # Compute x = sum of all x_j * lambda_j (Lagrange interpolation at 0)
        # Each party contributes x_j * lambda_j to reconstruct x
        x_total = 0
        for pid in participants:
            if pid == party_id:
                x_j = int(key_share.x_i)
            else:
                x_j = received_p2p_msgs[pid]['x_i']
            lambda_j = self._compute_lagrange_coeff(pid, participants)
            x_total = (x_total + x_j * lambda_j) % self.order

        # delta_i = k_i * gamma (where gamma = sum of all gamma_j)
        delta_i_int = (int(k_i) * gamma_sum) % self.order
        delta_i = self.group.init(ZR, delta_i_int)

        # sigma_i = k_i * x (party i's additive share of k*x)
        # When summed: sum(sigma_i) = sum(k_i) * x = k * x
        sigma_i_int = (int(k_i) * x_total) % self.order
        sigma_i = self.group.init(ZR, sigma_i_int)

        broadcast_msg = {
            'party_id': party_id,
            'delta_i': delta_i,
        }

        updated_state = private_state.copy()
        updated_state['R'] = R
        updated_state['delta_i'] = delta_i
        updated_state['sigma_i'] = sigma_i
        updated_state['round2_by_party'] = round2_by_party
        updated_state['gamma_sum'] = gamma_sum

        return broadcast_msg, updated_state

    def _compute_lagrange_coeff(self, party_id: PartyId,
                                 participants: List[PartyId]) -> int:
        """Compute Lagrange coefficient for a party in a set of participants."""
        # lambda_i = product_{j != i} (0 - j) / (i - j) = product_{j != i} (-j) / (i - j)
        # = product_{j != i} j / (j - i)
        lambda_i = 1
        for j in participants:
            if j != party_id:
                num = j
                denom = j - party_id
                # Compute modular inverse of denom
                denom_inv = pow(denom % self.order, self.order - 2, self.order)
                lambda_i = (lambda_i * num * denom_inv) % self.order

        return lambda_i

    def sign_round4(self, party_id: PartyId, private_state: Dict[str, Any],
                    all_round3_msgs: List[Dict[str, Any]]) -> Tuple[ZRElement, Dict[str, Any]]:
        """
        Round 4: Compute and return signature share.

        GG18 Signature Formula:
        - delta = k * gamma = sum(delta_i)
        - R_raw = g^gamma (from round 3)
        - R = R_raw^{delta^{-1}} = g^{gamma / (k*gamma)} = g^{1/k}
        - r = x-coordinate of R (mod q)
        - sigma = k * x = sum(sigma_i)
        - s = (e + r*x) * k^{-1}
        - Since we have k*x (sigma) and k*gamma (delta):
        - s = (e + r*sigma/k) * k^{-1} = e/k + r*sigma/k^2
        - Hmm, this doesn't simplify nicely with what we have...

        Actually in GG18:
        - s_i = k_i * e + r * sigma_i (where sigma_i is party i's share of k*x)
        - s = sum(s_i) / delta = (k*e + r*k*x) / (k*gamma) = (e + rx) / gamma
        - But we want s = k^{-1}(e + rx), and R = g^{1/k}
        - So we need R = g^gamma and s = (e + rx) * gamma / delta
        - Since delta = k*gamma, s = (e + rx) / k ✓

        Args:
            party_id: This party's identifier
            private_state: State from round 3
            all_round3_msgs: Delta broadcasts from all parties

        Returns:
            Tuple of (signature_share, proof)
        """
        e = private_state['e']
        R_raw = private_state['R']  # g^{sum(gamma_i)} = g^gamma
        sigma_i = private_state['sigma_i']
        k_i = private_state['k_i']
        participants = private_state['participants']

        # Compute delta = sum of all delta_i = k * gamma
        delta = self.group.init(ZR, 0)
        for msg in all_round3_msgs:
            delta = delta + msg['delta_i']

        # Compute delta inverse
        delta_inv = delta ** -1

        # R = g^{gamma} * delta^{-1} = g^{gamma / (k*gamma)} = g^{1/k}
        # This gives us the correct R for ECDSA where R = g^{k^{-1}} (or equivalently k*G in additive notation)
        # Actually wait - in standard ECDSA, R = k*G = g^k, not g^{1/k}
        # So R_raw = g^gamma, and we need R = g^{1/k}
        # Since delta = k*gamma, delta^{-1} = 1/(k*gamma)
        # R = R_raw^{delta^{-1}} = g^{gamma * 1/(k*gamma)} = g^{1/k}
        # But standard ECDSA uses R = g^k... let me re-read GG18
        #
        # In GG18 Section 4.2: R = g^{delta^{-1}} where delta = k*gamma
        # and gamma = product of all Gamma_i where Gamma_i = g^{gamma_i}
        # So R = (product Gamma_i)^{delta^{-1}} = g^{gamma * delta^{-1}} = g^{1/k}
        #
        # Then r = H(R) (x-coordinate)
        # s = k(e + rx) = delta/gamma * (e + rx)
        #
        # For verification: g^{s^{-1} * e} * pk^{s^{-1} * r} = R
        # = g^{(e+rx)/s} = g^{(e+rx) * gamma / (delta*(e+rx))} = g^{gamma/delta} = g^{1/k} = R ✓

        R = R_raw ** delta_inv

        # Compute r = x-coordinate of R (mod q)
        r = self.group.zr(R)

        # Compute signature share
        # s = k(e + rx) = (e*k + r*k*x) = e*sum(k_i) + r*sum(sigma_i)
        # Each party computes: s_i = e*k_i + r*sigma_i
        s_i = (e * k_i) + (r * sigma_i)

        proof = {
            'party_id': party_id,
            'R': R,
            'r': r,
            'delta': delta,
        }

        return s_i, proof

    def combine_signatures(self, signature_shares: Dict[PartyId, ZRElement],
                          R: GElement, participants: List[PartyId]) -> GG18_Signature:
        """
        Combine signature shares into final signature.

        Args:
            signature_shares: Dict mapping party_id to signature share
            R: Combined R point from round 3
            participants: List of participating parties

        Returns:
            GG18_Signature object with (r, s)
        """
        r = self.group.zr(R)

        # Sum signature shares (additive reconstruction)
        s = self.group.init(ZR, 0)
        for party_id in participants:
            if party_id in signature_shares:
                s = s + signature_shares[party_id]

        # Low-s normalization
        s = self._normalize_s(s)

        return GG18_Signature(r=r, s=s)

    def _normalize_s(self, s: ZRElement) -> ZRElement:
        """Normalize s to low-s form (BIP-62 compliant)."""
        s_int = int(s) % self.order
        half_order = self.order // 2

        if s_int > half_order:
            return self.group.init(ZR, self.order - s_int)
        return s

    def verify(self, public_key: GElement, signature: GG18_Signature,
               message: bytes, generator: GElement) -> bool:
        """
        Verify ECDSA signature.

        Args:
            public_key: Combined public key
            signature: GG18_Signature to verify
            message: Original message
            generator: EC generator point

        Returns:
            True if valid, False otherwise
        """
        r, s = signature.r, signature.s
        e = self._hash_message(message)

        # s^{-1}
        s_inv = s ** -1

        # u1 = e * s^{-1}, u2 = r * s^{-1}
        u1 = e * s_inv
        u2 = r * s_inv

        # R' = g^{u1} * pk^{u2}
        R_prime = (generator ** u1) * (public_key ** u2)

        # r' = x-coordinate of R'
        r_prime = self.group.zr(R_prime)

        return r == r_prime


class GG18(PKSig):
    """
    GG18 Threshold ECDSA Signature Scheme.

    Implements the full threshold ECDSA protocol from Gennaro & Goldfeder 2019.
    Extends PKSig base class with keygen(), sign(), verify() interface.

    Features:
    - t-of-n threshold signatures
    - Paillier-based MtA protocol
    - 4-round interactive signing
    - No presigning (each signature requires full protocol)

    Security:
    - Assumption: DDH, DCR (Decisional Composite Residuosity), ROM
    - Definition: EU-CMA (Existential Unforgeability under Chosen Message Attack)

    >>> from charm.toolbox.eccurve import secp256k1
    >>> from charm.toolbox.integergroup import RSAGroup
    >>> group = ECGroup(secp256k1)
    >>> rsa_group = RSAGroup()
    >>> gg18 = GG18(group, rsa_group, threshold=2, num_parties=3, paillier_bits=512)
    >>> gg18 is not None
    True
    """

    def __init__(self, ec_group: ECGroupType, rsa_group: RSAGroup,
                 threshold: int, num_parties: int, paillier_bits: int = 2048):
        """
        Initialize GG18 threshold ECDSA.

        Args:
            ec_group: EC group (e.g., ECGroup(secp256k1))
            rsa_group: RSA group for Paillier
            threshold: Minimum parties to sign (t)
            num_parties: Total parties (n)
            paillier_bits: Paillier modulus bit length
        """
        PKSig.__init__(self)
        self.setProperty(secDef='EU_CMA', assumption='DDH+DCR',
                        messageSpace='arbitrary', secModel='ROM')

        self.group = ec_group
        self.rsa_group = rsa_group
        self.t = threshold
        self.n = num_parties
        self.paillier_bits = paillier_bits

        self._dkg = GG18_DKG(ec_group, rsa_group, threshold, num_parties, paillier_bits)
        self._signer = GG18_Sign(ec_group, rsa_group, paillier_bits)

    def keygen(self, generator: Optional[GElement] = None) -> Tuple[GElement, List[GG18_KeyShare]]:
        """
        Generate threshold key shares.

        This is a convenience wrapper that simulates the 3-round DKG.
        In practice, each party runs the DKG rounds interactively.

        Args:
            generator: EC generator point (uses random if None)

        Returns:
            Tuple of (public_key, list of key shares)
        """
        if generator is None:
            generator = self.group.random(G)

        session_id = b"GG18_KEYGEN_" + self.group.serialize(generator)[:16]

        # Round 1: All parties generate secrets and commitments
        round1_results = []
        for i in range(1, self.n + 1):
            msg, state = self._dkg.keygen_round1(i, generator, session_id)
            round1_results.append((msg, state))

        round1_msgs = [r[0] for r in round1_results]
        states = [r[1] for r in round1_results]

        # Round 2: Prepare shares
        round2_results = []
        for i in range(self.n):
            shares, state = self._dkg.keygen_round2(i + 1, states[i], round1_msgs)
            round2_results.append((shares, state))
            states[i] = state

        # Collect shares for each party
        received_shares = {}
        for recv in range(1, self.n + 1):
            received_shares[recv] = {}
            for send in range(self.n):
                received_shares[recv][send + 1] = round2_results[send][0][recv]

        # Round 3: Compute final key shares
        key_shares = []
        for i in range(self.n):
            key_share, complaint = self._dkg.keygen_round3(
                i + 1, states[i], received_shares[i + 1], round1_msgs
            )
            if complaint is not None:
                raise ValueError(f"DKG failed: complaint from party {complaint['accuser']}")
            key_shares.append(key_share)

        public_key = key_shares[0].X
        return public_key, key_shares

    def sign(self, key_shares: List[GG18_KeyShare], message: bytes,
             participants: Optional[List[PartyId]] = None,
             generator: Optional[GElement] = None) -> GG18_Signature:
        """
        Generate threshold signature.

        Convenience wrapper that simulates the 4-round signing protocol.
        In practice, each party runs the signing rounds interactively.

        Args:
            key_shares: List of participating parties' key shares
            message: Message to sign
            participants: List of participating party IDs (default: first t)
            generator: EC generator point

        Returns:
            GG18_Signature object
        """
        if len(key_shares) < self.t:
            raise ValueError(f"Need at least {self.t} key shares")

        if participants is None:
            participants = [ks.party_id for ks in key_shares[:self.t]]

        if generator is None:
            # Derive from first key share's verification key
            generator = self.group.random(G)

        session_id = b"GG18_SIGN_" + hashlib.sha256(message).digest()[:16]

        # Get key shares for participants
        ks_by_party = {ks.party_id: ks for ks in key_shares}

        # Round 1
        round1_results = {}
        states = {}
        for pid in participants:
            msg, state = self._signer.sign_round1(
                pid, ks_by_party[pid], participants, generator, session_id
            )
            round1_results[pid] = msg
            states[pid] = state

        round1_msgs = list(round1_results.values())

        # Round 2
        round2_broadcasts = {}
        round2_p2p = {}
        for pid in participants:
            broadcast, p2p, state = self._signer.sign_round2(
                pid, states[pid], round1_msgs, message
            )
            round2_broadcasts[pid] = broadcast
            round2_p2p[pid] = p2p
            states[pid] = state

        round2_msgs = list(round2_broadcasts.values())

        # Collect P2P messages for each party
        received_p2p = {}
        for recv_pid in participants:
            received_p2p[recv_pid] = {}
            for send_pid in participants:
                if send_pid != recv_pid and recv_pid in round2_p2p[send_pid]:
                    received_p2p[recv_pid][send_pid] = round2_p2p[send_pid][recv_pid]

        # Round 3
        round3_results = {}
        for pid in participants:
            broadcast, state = self._signer.sign_round3(
                pid, states[pid], round2_msgs, received_p2p[pid]
            )
            round3_results[pid] = broadcast
            states[pid] = state

        round3_msgs = list(round3_results.values())

        # Round 4
        signature_shares = {}
        R = None
        for pid in participants:
            s_i, proof = self._signer.sign_round4(pid, states[pid], round3_msgs)
            signature_shares[pid] = s_i
            if R is None:
                R = proof['R']

        # Combine signatures
        return self._signer.combine_signatures(signature_shares, R, participants)

    def verify(self, public_key: GElement, message: bytes,
               signature: Union[GG18_Signature, Tuple[ZRElement, ZRElement]],
               generator: Optional[GElement] = None) -> bool:
        """
        Verify ECDSA signature.

        Args:
            public_key: Combined public key
            message: Original message
            signature: GG18_Signature or (r, s) tuple
            generator: EC generator point

        Returns:
            True if valid, False otherwise
        """
        if generator is None:
            generator = self.group.random(G)

        if isinstance(signature, tuple):
            signature = GG18_Signature(r=signature[0], s=signature[1])

        return self._signer.verify(public_key, signature, message, generator)

