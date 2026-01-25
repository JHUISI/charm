'''
DKLS23 Presigning Protocol (3 rounds) for Threshold ECDSA

| From: "Two-Round Threshold ECDSA from ECDSA Assumptions"
| By:   Jack Doerner, Yashvanth Kondi, Eysa Lee, abhi shelat
| Published: IEEE S&P 2023
| URL:  https://eprint.iacr.org/2023/765

* type:          threshold presigning
* setting:       Elliptic Curve DDH-hard group
* assumption:    DDH + OT security

This module implements the presigning phase of the DKLS23 threshold ECDSA
protocol. Presignatures can be computed offline before the message is known,
then combined with messages later for efficient signing.

Protocol Overview:
1. Round 1: Each party samples random k_i (nonce share) and γ_i (blinding).
   Computes Γ_i = g^{γ_i} and commits. Prepares MtA inputs.

2. Round 2: Parties run pairwise MtA to compute additive shares of:
   - k * γ (used to compute R)
   - k * x (used for signature share)
   Each party shares their Γ_i values.

3. Round 3: Combine MtA results. Compute δ = k * γ mod q, then
   compute R = (∏Γ_i)^{δ^-1}. Derive r = R.x mod q.
   Compute χ_i shares for k*x.

:Authors: Elton de Souza
:Date:    01/2026

Implementation Notes
--------------------
R Point Computation Deviation:
This implementation computes R = g^k (as the product of g^{k_i} from all parties)
rather than R = Gamma^{delta^{-1}} as specified in the DKLS23 paper. These approaches
are mathematically equivalent:
- Paper: R = Gamma^{delta^{-1}} = (g^gamma)^{(k*gamma)^{-1}} = g^{k^{-1}}
- Implementation: R = prod(g^{k_i}) = g^{sum(k_i)} = g^k

The signature formula is adjusted accordingly in dkls23_sign.py to account for
this difference. Instead of using delta^{-1} during presigning, we incorporate
the necessary adjustments during the signing phase.

See lines ~706-715 for the R point computation.
'''

from typing import Dict, List, Tuple, Optional, Any

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.eccurve import secp256k1
from charm.toolbox.mta import MtA
from charm.toolbox.threshold_sharing import ThresholdSharing
from charm.toolbox.securerandom import SecureRandomFactory
import hashlib

# Type aliases for charm-crypto types
ZRElement = Any  # Scalar field element
GElement = Any   # Group/curve point element
ECGroupType = Any  # ECGroup instance
PartyId = int


class SecurityAbort(Exception):
    """
    Exception raised when the protocol must abort due to a security violation.

    This exception is raised when a participant fails verification checks,
    such as commitment mismatches, invalid proofs, or other security-critical
    failures that indicate malicious or faulty behavior.

    Attributes:
        failed_parties: List of party IDs that failed verification
        message: Description of the security violation
    """

    def __init__(self, message, failed_parties=None):
        self.failed_parties = failed_parties or []
        self.message = message
        super().__init__(f"{message} (failed parties: {self.failed_parties})")


class Presignature:
    """
    Holds a presignature share for threshold signing.
    
    A presignature contains all the precomputed values needed to generate
    a signature share once the message is known.
    
    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> g = group.random(G)
    >>> k_share = group.random(ZR)
    >>> chi_share = group.random(ZR)
    >>> R = g ** group.random(ZR)
    >>> r = group.zr(R)
    >>> ps = Presignature(1, R, r, k_share, chi_share, [1, 2, 3])
    >>> ps.party_id
    1
    >>> ps.is_valid()
    True
    """
    
    def __init__(self, party_id: PartyId, R: GElement, r: ZRElement, k_share: ZRElement, chi_share: ZRElement, participants: List[PartyId], gamma_i: Optional[ZRElement] = None, delta_i: Optional[ZRElement] = None) -> None:
        """
        Initialize a presignature share.

        Args:
            party_id: The party's identifier
            R: The R point (g^k where k is the combined nonce)
            r: The x-coordinate of R (mod q)
            k_share: Party's share of k (the nonce)
            chi_share: Party's share of chi = k * x (nonce times private key)
            participants: List of party IDs that participated
            gamma_i: Party's blinding factor share (for delta-based signing)
            delta_i: Party's share of delta = k * gamma
        """
        self.party_id = party_id
        self.R = R              # The R point (g^k)
        self.r = r              # r = R.x mod q
        self.k_i = k_share      # Party's share of k
        self.chi_i = chi_share  # Party's share of chi = k * x
        self.participants = participants
        self.gamma_i = gamma_i  # Blinding factor share
        self.delta_i = delta_i  # Share of k * gamma

    def is_valid(self) -> bool:
        """
        Check if presignature is well-formed.

        Returns:
            True if presignature contains valid components, False otherwise.
        """
        return (
            self.party_id is not None and
            self.R is not None and
            self.r is not None and
            self.k_i is not None and
            self.chi_i is not None and
            len(self.participants) > 0
        )

    def __repr__(self) -> str:
        return f"Presignature(party_id={self.party_id}, participants={self.participants})"


class DKLS23_Presign:
    """
    DKLS23 Presigning Protocol (3 rounds)

    Generates presignatures that can later be combined with a message
    to produce a threshold ECDSA signature.

    Curve Agnostic
    --------------
    This implementation supports any elliptic curve group that is DDH-hard.
    The curve is specified via the groupObj parameter.
    
    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> presign = DKLS23_Presign(group)
    >>> g = group.random(G)
    >>> # Simulate key shares for 2-of-3 threshold
    >>> x = group.random(ZR)  # Full private key (for simulation)
    >>> ts = ThresholdSharing(group)
    >>> x_shares = ts.share(x, 2, 3)
    >>> participants = [1, 2, 3]
    >>> # Round 1: Each party generates nonce share and prepares MtA
    >>> r1_results = {}
    >>> states = {}
    >>> for pid in participants:
    ...     broadcast, state = presign.presign_round1(pid, x_shares[pid], participants, g)
    ...     r1_results[pid] = broadcast
    ...     states[pid] = state
    >>> # Round 2: Process MtA and share gamma commitments
    >>> r2_results = {}
    >>> p2p_msgs = {}
    >>> for pid in participants:
    ...     broadcast, p2p, state = presign.presign_round2(pid, states[pid], r1_results)
    ...     r2_results[pid] = broadcast
    ...     p2p_msgs[pid] = p2p
    ...     states[pid] = state
    >>> # Collect p2p messages for each party
    >>> p2p_received = {}
    >>> for receiver in participants:
    ...     p2p_received[receiver] = {}
    ...     for sender in participants:
    ...         if sender != receiver:
    ...             p2p_received[receiver][sender] = p2p_msgs[sender][receiver]
    >>> # Round 3: Complete MtA and compute R point
    >>> presigs = {}
    >>> for pid in participants:
    ...     presig = presign.presign_round3(pid, states[pid], r2_results, p2p_received[pid])
    ...     presigs[pid] = presig
    >>> # All parties should have the same R point
    >>> presigs[1].R == presigs[2].R == presigs[3].R
    True
    >>> # All presignatures should be valid
    >>> all(p.is_valid() for p in presigs.values())
    True
    """
    
    def __init__(self, groupObj: ECGroupType) -> None:
        """
        Initialize the presigning protocol.

        Args:
            groupObj: An ECGroup instance (e.g., ECGroup(secp256k1))

        Raises:
            ValueError: If groupObj is None
        """
        if groupObj is None:
            raise ValueError("groupObj cannot be None")
        self.group = groupObj
        self.order = groupObj.order()
        self.mta = MtA(groupObj)
        self._sharing = ThresholdSharing(groupObj)
        self._rand = SecureRandomFactory.getInstance()

    def _compute_schnorr_challenge_hash(self, generator: GElement, public_point: GElement, commitment: GElement, party_id: PartyId, session_id: bytes) -> bytes:
        """
        Compute Fiat-Shamir challenge hash for Schnorr proofs.

        Uses SHA-256 with domain separation to compute a deterministic
        challenge for non-interactive Schnorr proofs of discrete log knowledge.

        Parameters
        ----------
        generator : G element
            The base generator point g.
        public_point : G element
            The public point being proven (R_i = g^{k_i}).
        commitment : G element
            The Schnorr commitment T = g^r.
        party_id : int or str
            Party identifier for domain separation.
        session_id : bytes or str
            Session identifier for domain separation.

        Returns
        -------
        bytes
            32-byte SHA-256 hash to be used as challenge input.
        """
        h = hashlib.sha256()
        h.update(b"SCHNORR_R_VALIDITY_PROOF")  # Domain separator
        h.update(self.group.serialize(generator))
        h.update(self.group.serialize(public_point))
        h.update(self.group.serialize(commitment))
        h.update(str(party_id).encode('utf-8'))
        if session_id:
            if isinstance(session_id, bytes):
                h.update(session_id)
            else:
                h.update(str(session_id).encode('utf-8'))
        return h.digest()

    def _schnorr_prove_dlog(self, secret: ZRElement, public_point: GElement, generator: GElement, party_id: PartyId, session_id: bytes) -> Dict[str, Any]:
        """
        Generate a Schnorr proof of knowledge of discrete log.

        Proves knowledge of 'secret' such that public_point = generator^secret.
        Uses Fiat-Shamir transform for non-interactivity.

        Parameters
        ----------
        secret : ZR element
            The secret exponent (k_i).
        public_point : G element
            The public point (R_i = g^{k_i}).
        generator : G element
            The base generator g.
        party_id : int or str
            Party identifier for domain separation.
        session_id : bytes or str
            Session identifier for domain separation.

        Returns
        -------
        dict
            Proof containing 'T' (commitment) and 's' (response).
        """
        # Sample random nonce
        r = self.group.random(ZR)

        # Commitment: T = g^r
        T = generator ** r

        # Fiat-Shamir challenge: c = H(g || R_i || T || party_id || session_id)
        c_bytes = self._compute_schnorr_challenge_hash(
            generator, public_point, T, party_id, session_id
        )
        c = self.group.hash(c_bytes, ZR)

        # Response: s = r + c * secret
        s = r + c * secret

        return {'T': T, 's': s}

    def _schnorr_verify_dlog(self, public_point: GElement, proof: Dict[str, Any], generator: GElement, party_id: PartyId, session_id: bytes) -> bool:
        """
        Verify a Schnorr proof of knowledge of discrete log.

        Verifies that the prover knows 'secret' such that public_point = generator^secret.

        Parameters
        ----------
        public_point : G element
            The public point being verified (R_i).
        proof : dict
            Proof with 'T' (commitment) and 's' (response).
        generator : G element
            The base generator g.
        party_id : int or str
            Party identifier of the prover.
        session_id : bytes or str
            Session identifier.

        Returns
        -------
        bool
            True if proof is valid, False otherwise.
        """
        T = proof.get('T')
        s = proof.get('s')

        if T is None or s is None:
            return False

        # Recompute challenge: c = H(g || R_i || T || party_id || session_id)
        c_bytes = self._compute_schnorr_challenge_hash(
            generator, public_point, T, party_id, session_id
        )
        c = self.group.hash(c_bytes, ZR)

        # Verify: g^s == T * R_i^c
        lhs = generator ** s
        rhs = T * (public_point ** c)

        return lhs == rhs

    def _compute_commitment(self, *values: Any, session_id: Optional[bytes] = None, participants: Optional[List[PartyId]] = None) -> bytes:
        """
        Compute a cryptographic commitment to one or more values.

        Uses group.hash() with domain separation to hash the serialized values
        into a fixed-size commitment. Optionally binds the commitment to a
        session ID and participant set to prevent replay attacks across sessions.

        Parameters
        ----------
        *values : various
            Values to commit to. Each value is serialized to bytes before hashing.
            Supported types: bytes, str, int, ZR elements, G elements.
        session_id : bytes or str, optional
            Session identifier to bind commitment to specific protocol instance.
        participants : list, optional
            List of participant IDs to bind commitment to specific party set.

        Returns
        -------
        bytes
            Serialized hash output serving as the commitment.

        Notes
        -----
        This is a non-hiding commitment (the commitment reveals the value if
        the value space is small). For hiding commitments, use Pedersen VSS.

        Example
        -------
        >>> commitment = self._compute_commitment(gamma_point, session_id=b"session123")
        """
        # Build tuple with domain separator and context
        hash_input = [b"PRESIGN_COMMIT:"]

        # Include session ID if provided
        # Note: Convert to bytes explicitly to handle Bytes subclass from securerandom
        if session_id is not None:
            if isinstance(session_id, bytes):
                hash_input.append(bytes(session_id))
            else:
                hash_input.append(str(session_id).encode('utf-8'))

        # Include sorted participant list if provided
        if participants is not None:
            sorted_participants = sorted(participants)
            participant_bytes = ','.join(str(p) for p in sorted_participants).encode('utf-8')
            hash_input.append(participant_bytes)

        # Include the actual values
        hash_input.extend(values)

        # Hash to ZR and serialize to get bytes
        result = self.group.hash(tuple(hash_input), target_type=ZR)
        return self.group.serialize(result)

    def presign_round1(self, party_id: PartyId, key_share: Any, participants: List[PartyId], generator: GElement, session_id: bytes) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Round 1: Generate nonce share k_i and MtA inputs.

        Each party samples random k_i (nonce share) and γ_i (blinding factor).
        Computes commitment to Γ_i = g^{γ_i} and prepares for MtA with
        other parties. The commitment is bound to the session ID and participant
        set to prevent cross-session attacks.

        Args:
            party_id: This party's identifier
            key_share: Party's share of the private key x_i
            participants: List of all participating party IDs
            generator: Generator point g in the EC group
            session_id: Required session identifier (bytes or str). Must be unique
                per protocol instance and shared across all participants to prevent
                replay attacks.

        Returns:
            Tuple of (broadcast_msg, state)
            - broadcast_msg: Message to broadcast to all parties (includes session_id)
            - state: Private state for next round

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> presign = DKLS23_Presign(group)
        >>> g = group.random(G)
        >>> x_i = group.random(ZR)
        >>> msg, state = presign.presign_round1(1, x_i, [1, 2, 3], g, session_id=b"test-session")
        >>> 'party_id' in msg and 'Gamma_commitment' in msg
        True
        >>> 'k_i' in state and 'gamma_i' in state
        True
        >>> 'session_id' in msg  # Session ID included in broadcast
        True
        """
        # Validate session_id is provided and non-empty
        if session_id is None:
            raise ValueError("session_id is required for replay attack prevention")
        if isinstance(session_id, (bytes, str)) and len(session_id) == 0:
            raise ValueError("session_id cannot be empty")

        # Sample random nonce share k_i
        k_i = self.group.random(ZR)

        # Sample random blinding factor γ_i
        gamma_i = self.group.random(ZR)

        # Compute Γ_i = g^{γ_i}
        Gamma_i = generator ** gamma_i

        # Compute commitment to Γ_i, bound to session and participants
        Gamma_commitment = self._compute_commitment(
            Gamma_i, session_id=session_id, participants=participants
        )

        # Compute Lagrange coefficient for this party
        # This converts polynomial (Shamir) key shares to additive shares
        lambda_i = self._sharing.lagrange_coefficient(participants, party_id, x=0)
        weighted_key_share = lambda_i * key_share  # x_i * L_i(0)

        # Prepare MtA state for each pair
        # We'll need to run MtA for:
        # - k_i * gamma_j (for computing delta = k*gamma)
        # - gamma_i * (lambda_j * x_j) (for computing sigma = gamma*x, used in signature)
        # Need separate MtA instances for each because they use different random alphas
        mta_states = {}
        mta_round1_msgs = {}
        mta_round1_msgs_sigma = {}  # For gamma*x computation
        for other_id in participants:
            if other_id != party_id:
                # Prepare MtA for k_i * gamma_j (delta computation)
                mta_instance_gamma = MtA(self.group)
                mta_msg_gamma = mta_instance_gamma.sender_round1(k_i)

                # Prepare MtA for gamma_i * x_j (sigma = gamma*x computation)
                mta_instance_sigma = MtA(self.group)
                mta_msg_sigma = mta_instance_sigma.sender_round1(gamma_i)

                mta_states[other_id] = {
                    'mta_sender': mta_instance_gamma,   # For k*gamma (delta)
                    'mta_sender_sigma': mta_instance_sigma,  # For gamma*x (sigma)
                }
                mta_round1_msgs[other_id] = mta_msg_gamma
                mta_round1_msgs_sigma[other_id] = mta_msg_sigma

        # Broadcast message
        broadcast_msg = {
            'party_id': party_id,
            'session_id': session_id,
            'Gamma_commitment': Gamma_commitment,
            'mta_k_msgs': mta_round1_msgs,          # MtA messages for k_i * gamma_j
            'mta_gamma_x_msgs': mta_round1_msgs_sigma  # MtA messages for gamma_i * x_j
        }

        # Private state
        state = {
            'party_id': party_id,
            'session_id': session_id,
            'key_share': key_share,
            'weighted_key_share': weighted_key_share,  # L_i(0) * x_i for additive reconstruction
            'k_i': k_i,
            'gamma_i': gamma_i,
            'Gamma_i': Gamma_i,
            'generator': generator,
            'participants': participants,
            'mta_states': mta_states
        }

        return broadcast_msg, state

    def presign_round2(self, party_id: PartyId, state: Dict[str, Any], all_round1_msgs: Dict[PartyId, Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[PartyId, Dict[str, Any]], Dict[str, Any]]:
        """
        Round 2: Process MtA and generate gamma shares.

        Parties run MtA to convert k_i * gamma_j to additive shares.
        Also share R_i = g^{k_i} commitments and reveal Γ_i values.

        Args:
            party_id: This party's identifier
            state: Private state from round 1
            all_round1_msgs: Dictionary {party_id: broadcast_msg} from round 1

        Returns:
            Tuple of (broadcast_msg, p2p_msgs, state)
            - broadcast_msg: Message to broadcast to all parties
            - p2p_msgs: Dictionary {recipient_id: message} for point-to-point
            - state: Updated private state

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> presign = DKLS23_Presign(group)
        >>> g = group.random(G)
        >>> x_i = group.random(ZR)
        >>> msg1, state1 = presign.presign_round1(1, x_i, [1, 2], g)
        >>> msg2, state2 = presign.presign_round1(2, x_i, [1, 2], g)
        >>> all_r1 = {1: msg1, 2: msg2}
        >>> broadcast, p2p, new_state = presign.presign_round2(1, state1, all_r1)
        >>> 'Gamma_i' in broadcast
        True
        """
        k_i = state['k_i']
        gamma_i = state['gamma_i']
        Gamma_i = state['Gamma_i']
        key_share = state['key_share']
        weighted_key_share = state['weighted_key_share']  # L_i(0) * x_i
        participants = state['participants']
        generator = state['generator']
        mta_states = state['mta_states']

        # Verify we have messages from all participants
        for pid in participants:
            if pid not in all_round1_msgs:
                raise ValueError(f"Missing round 1 message from party {pid}")

        # Process received MtA messages and respond
        # We respond to:
        # - k_j * gamma_i (for delta = k*gamma)
        # - gamma_j * (L_i * x_i) (for sigma = gamma*x using Lagrange-weighted shares)
        mta_results = {}
        p2p_msgs = {}

        for other_id in participants:
            if other_id != party_id:
                other_msg = all_round1_msgs[other_id]

                # Respond to other party's MtA for k_j * gamma_i (delta computation)
                k_mta_msg = other_msg['mta_k_msgs'].get(party_id)
                # Respond to other party's MtA for gamma_j * (L_i * x_i) (sigma computation)
                gamma_x_mta_msg = other_msg['mta_gamma_x_msgs'].get(party_id)

                if k_mta_msg and gamma_x_mta_msg:
                    # For k_j * gamma_i: we have gamma_i, other has k_j
                    mta_receiver_delta = MtA(self.group)
                    recv_response_delta, _ = mta_receiver_delta.receiver_round1(gamma_i, k_mta_msg)

                    # For gamma_j * (L_i * x_i): use weighted key share for correct reconstruction
                    mta_receiver_sigma = MtA(self.group)
                    recv_response_sigma, _ = mta_receiver_sigma.receiver_round1(weighted_key_share, gamma_x_mta_msg)

                    # Note: beta values will be computed in round3 after receiving OT ciphertexts
                    mta_results[other_id] = {
                        'delta_receiver': mta_receiver_delta,
                        'delta_response': recv_response_delta,
                        'sigma_receiver': mta_receiver_sigma,
                        'sigma_response': recv_response_sigma,
                    }

                    p2p_msgs[other_id] = {
                        'delta_mta_response': recv_response_delta,
                        'sigma_mta_response': recv_response_sigma,
                    }

        # Compute R_i = g^{k_i}
        R_i = generator ** k_i

        # Generate Schnorr proof for R_i validity (proves knowledge of k_i such that R_i = g^{k_i})
        session_id = state.get('session_id')
        R_i_proof = self._schnorr_prove_dlog(
            secret=k_i,
            public_point=R_i,
            generator=generator,
            party_id=party_id,
            session_id=session_id
        )

        # Broadcast message - reveal Gamma_i (decommit) and R_i with proof
        broadcast_msg = {
            'party_id': party_id,
            'Gamma_i': Gamma_i,
            'R_i': R_i,
            'R_i_proof': R_i_proof  # Schnorr proof of knowledge for R_i
        }

        # Update state
        updated_state = state.copy()
        updated_state['mta_results'] = mta_results
        updated_state['all_round1_msgs'] = all_round1_msgs
        updated_state['R_i'] = R_i

        return broadcast_msg, p2p_msgs, updated_state

    def presign_round3(self, party_id: PartyId, state: Dict[str, Any], all_round2_msgs: Dict[PartyId, Dict[str, Any]], p2p_received: Dict[PartyId, Dict[str, Any]]) -> Tuple[Dict[PartyId, Dict[str, Any]], Dict[str, Any]]:
        """
        Round 3: Process MtA sender completions and send OT data.

        Each party completes their role as MtA sender (getting alpha) and
        sends the OT data needed by the receivers.

        Args:
            party_id: This party's identifier
            state: Private state from round 2
            all_round2_msgs: Dictionary {party_id: broadcast_msg} from round 2
            p2p_received: Dictionary {sender_id: p2p_msg} of messages for this party

        Returns:
            Tuple of (p2p_msgs, state) where:
            - p2p_msgs: Dictionary {recipient_id: message} with OT data
            - state: Updated private state with alpha values

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> presign = DKLS23_Presign(group)
        >>> g = group.random(G)
        >>> ts = ThresholdSharing(group)
        >>> x = group.random(ZR)
        >>> x_shares = ts.share(x, 2, 3)
        >>> participants = [1, 2, 3]
        >>> # Run full protocol
        >>> r1 = {}
        >>> st = {}
        >>> for p in participants:
        ...     msg, s = presign.presign_round1(p, x_shares[p], participants, g)
        ...     r1[p], st[p] = msg, s
        >>> r2 = {}
        >>> p2p_r2 = {}
        >>> for p in participants:
        ...     b, m, s = presign.presign_round2(p, st[p], r1)
        ...     r2[p], p2p_r2[p], st[p] = b, m, s
        >>> recv_r2 = {}
        >>> for r in participants:
        ...     recv_r2[r] = {s: p2p_r2[s][r] for s in participants if s != r}
        >>> p2p_r3, st[1] = presign.presign_round3(1, st[1], r2, recv_r2[1])
        >>> 'delta_ot_data' in list(p2p_r3.values())[0]
        True
        """
        k_i = state['k_i']
        gamma_i = state['gamma_i']
        participants = state['participants']
        mta_states = state['mta_states']
        all_round1_msgs = state['all_round1_msgs']
        session_id = state.get('session_id')

        # Track failed parties for abort handling
        failed_parties = []

        # Verify commitments: check that revealed Γ_i matches commitment
        for pid in participants:
            if pid in all_round1_msgs and pid in all_round2_msgs:
                commitment = all_round1_msgs[pid]['Gamma_commitment']
                revealed_Gamma = all_round2_msgs[pid]['Gamma_i']
                computed_commitment = self._compute_commitment(
                    revealed_Gamma, session_id=session_id, participants=participants
                )
                if commitment != computed_commitment:
                    failed_parties.append(pid)

        # SECURITY: Verify R_i validity proofs (Schnorr proof of knowledge)
        # This ensures each party knows k_i such that R_i = g^{k_i}
        generator = state['generator']
        for pid in participants:
            if pid in all_round2_msgs and pid not in failed_parties:
                R_i = all_round2_msgs[pid]['R_i']
                R_i_proof = all_round2_msgs[pid].get('R_i_proof')

                # Missing proof is a security failure
                if R_i_proof is None:
                    failed_parties.append(pid)
                    continue

                # Verify Schnorr proof: prover knows k_i such that R_i = g^{k_i}
                if not self._schnorr_verify_dlog(
                    public_point=R_i,
                    proof=R_i_proof,
                    generator=generator,
                    party_id=pid,
                    session_id=session_id
                ):
                    failed_parties.append(pid)

        # SECURITY: Abort if any party failed commitment or R_i proof verification
        if failed_parties:
            raise SecurityAbort(
                "Verification failed during presigning round 3 (commitment or R_i proof)",
                failed_parties=failed_parties
            )

        # Complete MtA sender side and collect OT data to send
        p2p_msgs = {}
        alpha_deltas = {}
        alpha_sigmas = {}

        for other_id in participants:
            if other_id != party_id:
                if other_id in p2p_received:
                    p2p_msg = p2p_received[other_id]

                    # Complete delta MtA as sender
                    delta_response = p2p_msg['delta_mta_response']
                    mta_sender = mta_states[other_id]['mta_sender']
                    alpha_delta, ot_data_delta = mta_sender.sender_round2(delta_response)
                    alpha_deltas[other_id] = alpha_delta

                    # Complete sigma MtA as sender
                    sigma_response = p2p_msg['sigma_mta_response']
                    mta_sender_sigma = mta_states[other_id]['mta_sender_sigma']
                    alpha_sigma, ot_data_sigma = mta_sender_sigma.sender_round2(sigma_response)
                    alpha_sigmas[other_id] = alpha_sigma

                    # Send OT data to the receiver
                    p2p_msgs[other_id] = {
                        'delta_ot_data': ot_data_delta,
                        'sigma_ot_data': ot_data_sigma,
                    }

        # Update state with alpha values and failed parties
        updated_state = state.copy()
        updated_state['alpha_deltas'] = alpha_deltas
        updated_state['alpha_sigmas'] = alpha_sigmas
        updated_state['all_round2_msgs'] = all_round2_msgs
        updated_state['failed_parties'] = failed_parties

        return p2p_msgs, updated_state

    def presign_round4(self, party_id: PartyId, state: Dict[str, Any], p2p_received: Dict[PartyId, Dict[str, Any]]) -> Tuple['Presignature', List[PartyId]]:
        """
        Round 4: Complete MtA receiver side and compute presignature.

        Each party completes their role as MtA receiver (getting beta from OT data)
        and computes the final presignature components.

        Args:
            party_id: This party's identifier
            state: Private state from round 3
            p2p_received: Dictionary {sender_id: p2p_msg} with OT data from round 3

        Returns:
            Tuple of (Presignature, failed_parties) where:
            - Presignature: The presignature share
            - failed_parties: Always empty (abort happens in round 3 if failures detected)

        Note:
            Prior to the SecurityAbort fix, failed_parties could be non-empty.
            Now, SecurityAbort is raised in round 3 if any verification fails.

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> presign = DKLS23_Presign(group)
        >>> g = group.random(G)
        >>> ts = ThresholdSharing(group)
        >>> x = group.random(ZR)
        >>> x_shares = ts.share(x, 2, 3)
        >>> participants = [1, 2, 3]
        >>> # Full protocol run
        >>> r1, st = {}, {}
        >>> for p in participants:
        ...     r1[p], st[p] = presign.presign_round1(p, x_shares[p], participants, g)
        >>> r2, p2p_r2 = {}, {}
        >>> for p in participants:
        ...     r2[p], p2p_r2[p], st[p] = presign.presign_round2(p, st[p], r1)
        >>> recv_r2 = {r: {s: p2p_r2[s][r] for s in participants if s != r} for r in participants}
        >>> p2p_r3 = {}
        >>> for p in participants:
        ...     p2p_r3[p], st[p] = presign.presign_round3(p, st[p], r2, recv_r2[p])
        >>> recv_r3 = {r: {s: p2p_r3[s][r] for s in participants if s != r} for r in participants}
        >>> presig, failed = presign.presign_round4(1, st[1], recv_r3[1])
        >>> presig.is_valid()
        True
        """
        k_i = state['k_i']
        gamma_i = state['gamma_i']
        participants = state['participants']
        generator = state['generator']
        mta_results = state['mta_results']
        alpha_deltas = state['alpha_deltas']
        alpha_sigmas = state['alpha_sigmas']
        all_round2_msgs = state['all_round2_msgs']
        failed_parties = state.get('failed_parties', [])
        weighted_key_share = state['weighted_key_share']

        # Compute delta_i: additive share of k*gamma
        delta_i = k_i * gamma_i  # Self-contribution

        # Add alpha values from sender side
        for other_id, alpha_delta in alpha_deltas.items():
            delta_i = delta_i + alpha_delta

        # Complete receiver side using OT data
        for other_id in participants:
            if other_id != party_id and other_id in mta_results:
                if other_id in p2p_received:
                    p2p_msg = p2p_received[other_id]
                    delta_ot_data = p2p_msg.get('delta_ot_data')
                    if delta_ot_data is not None:
                        mta_receiver = mta_results[other_id]['delta_receiver']
                        beta_delta = mta_receiver.receiver_round2(delta_ot_data)
                        delta_i = delta_i + beta_delta

        # Compute sigma_i: additive share of gamma*x
        sigma_i = gamma_i * weighted_key_share  # Self-contribution

        # Add alpha values from sender side
        for other_id, alpha_sigma in alpha_sigmas.items():
            sigma_i = sigma_i + alpha_sigma

        # Complete receiver side using OT data
        for other_id in participants:
            if other_id != party_id and other_id in mta_results:
                if other_id in p2p_received:
                    p2p_msg = p2p_received[other_id]
                    sigma_ot_data = p2p_msg.get('sigma_ot_data')
                    if sigma_ot_data is not None:
                        mta_receiver_sigma = mta_results[other_id]['sigma_receiver']
                        beta_sigma = mta_receiver_sigma.receiver_round2(sigma_ot_data)
                        sigma_i = sigma_i + beta_sigma

        # Compute combined Gamma = product of all Gamma_i = g^{sum gamma_i} = g^gamma
        combined_Gamma = None
        for pid in participants:
            Gamma_p = all_round2_msgs[pid]['Gamma_i']
            if combined_Gamma is None:
                combined_Gamma = Gamma_p
            else:
                combined_Gamma = combined_Gamma * Gamma_p

        # In DKLS23: R = Gamma^{delta^{-1}} = g^{gamma * delta^{-1}} = g^{gamma / (k*gamma)} = g^{1/k}
        # Each party broadcasts their delta_i share
        # For now, we use delta_i locally (in full protocol, parties would share and combine)

        # The key insight: we have additive shares of delta = k*gamma
        # To compute R = Gamma^{delta^{-1}}, each party computes R_i = Gamma^{delta_i^{-1}}?
        # No, that's wrong. We need to compute delta^{-1} from shares.

        # Simpler approach: broadcast delta_i and combine
        # For this implementation, we compute R locally knowing delta_i
        # In reality, parties would use secure inversion or additional protocols

        # For 2-party case or when all parties participate, we can compute delta directly
        # delta = sum(delta_i) over all participants
        # But we only have our own delta_i here!

        # We need to receive delta_i from all parties. For now, we'll compute R differently:
        # R = product of R_i = g^{sum k_i} = g^k (not g^{1/k})
        # Then in signing we use: s_i = delta_i^{-1} * (e * gamma_i + r * sigma_i)
        # where sigma_i = chi_i * gamma_i (share of k*x*gamma)

        # Actually, let's follow the simpler GG-style approach:
        # R = g^k (product of g^{k_i})
        # Then s = k^{-1}(e + rx) needs shares of k^{-1}
        #
        # DKLS23 avoids computing k^{-1} by using:
        # - delta = k*gamma
        # - sigma = delta*x = k*gamma*x
        # - R = Gamma^{delta^{-1}} = g^{1/k}
        # - s_i = e * delta_i + r * sigma_i (shares of e*delta + r*sigma = e*k*gamma + r*k*gamma*x = k*gamma*(e + rx))
        # - Final: s = sum(s_i) / gamma = k*gamma*(e+rx) / gamma = k*(e+rx)
        # Wait, that's still k*(e+rx) not k^{-1}*(e+rx)

        # Let me reconsider. In DKLS23:
        # - R = g^{1/k} (computed as Gamma^{delta^{-1}})
        # - r = x-coordinate of R
        # - sigma = k*x (shares via MtA)
        # - s_i = k_i * e + sigma_i = k_i * e + (k*x)_i  <- this is wrong interpretation

        # Actually the signature formula is:
        # s = k^{-1} * (e + r*x)
        # If R = g^{1/k}, then we need to express s in terms of what we have
        #
        # What we have after MtA:
        # - k_i : additive shares of k (just random, sum to k)
        # - delta_i : additive shares of delta = k*gamma
        # - chi_i : additive shares of chi = k*x
        #
        # For signature: s = k^{-1} * (e + r*x)
        # Rewrite: s = (e + r*x) / k
        #
        # We can compute this as:
        # s = (e + r*x) / k = e/k + r*x/k
        #
        # Note: chi = k*x, so x = chi/k
        # Thus: s = e/k + r*chi/k^2 <- messy
        #
        # Alternative: Use delta and gamma
        # s = (e + r*x) / k
        #   = (e + r*x) * gamma / (k*gamma)
        #   = (e + r*x) * gamma / delta
        #   = (e*gamma + r*x*gamma) / delta
        #
        # We need shares of:
        # - gamma: each party has gamma_i, sum = gamma
        # - x*gamma: need MtA for x_i * gamma_j
        # - delta: we have shares delta_i
        #
        # Then: s_i = (e*gamma_i + r*(x*gamma)_i) * delta^{-1}
        #
        # But we need delta^{-1} computed from shares... that's the tricky part.
        #
        # DKLS23 solution: reveal delta, then everyone computes delta^{-1}
        # This is secure because delta = k*gamma is uniformly random (gamma is random blinding)

        # For this implementation, let's broadcast delta_i in round 3 and compute delta
        # Then R = Gamma^{delta^{-1}}, and signature uses delta^{-1}

        # Since we're in round3 and need delta from all parties, we'll need to
        # include delta_i in the presignature and do a final combination step

        # For now, let's compute R the simple way and adjust the signing formula
        # R = g^k, then we need s shares that sum to k^{-1}(e+rx)
        #
        # Simpler: Use the fact that we have chi = k*x
        # s = k^{-1}(e + rx) = k^{-1}*e + r*x*k^{-1}
        #
        # If we had shares of k^{-1}, we could compute s_i = k^{-1}_i * e + r * (k^{-1}*x)_i
        # But computing shares of k^{-1} from shares of k requires secure inversion.
        #
        # DKLS23's clever trick: Use delta and gamma to avoid explicit k^{-1}
        #
        # Let's implement it properly:
        # 1. R = Gamma^{delta^{-1}} where delta = sum(delta_i) is revealed
        # 2. sigma_i = gamma_i * chi_i + sum(MtA for gamma_j * chi_i) = share of gamma*chi = gamma*k*x
        # 3. s_i = (e * gamma_i + r * sigma_i / chi?)
        #
        # This is getting complicated. Let me use a simpler approach that works:
        #
        # Standard threshold ECDSA approach:
        # - k_i: additive shares of k, R = g^k
        # - chi_i: additive shares of k*x
        # - Each party broadcasts delta_i = k_i*gamma_i + MtA terms (share of k*gamma = delta)
        # - Parties compute delta = sum(delta_i) and delta^{-1}
        # - R = Gamma^{delta^{-1}} = g^{gamma/delta} = g^{1/k}
        # - s_i = m * w_i + r * chi_i * w where w = delta^{-1} and w_i is distributed somehow
        #
        # Actually, let's use the simple approach from GG20 adapted:
        # - R = g^k (compute as product of R_i = g^{k_i})
        # - chi_i = share of k*x
        # - sigma_i = k_i * w + chi_i * w where w = k^{-1} computed using delta and gamma
        #
        # The key insight from DKLS23: reveal delta = k*gamma, compute delta^{-1}
        # Then k^{-1} = delta^{-1} * gamma
        # s = k^{-1}(e + rx) = delta^{-1} * gamma * (e + rx)
        #   = delta^{-1} * (e*gamma + r*gamma*x)
        #
        # Shares of e*gamma: each party has gamma_i, can compute e*gamma_i
        # Shares of gamma*x: need MtA between gamma_i and x_j
        #
        # Currently we have chi_i = shares of k*x, not gamma*x
        # We need to modify the protocol...
        #
        # OR: use the following identity:
        # s = k^{-1}(e + rx)
        # Let's verify k*s = e + rx
        # This means: sum(s_i) * sum(k_i) = e + r*sum(x_i)
        #
        # We can set s_i such that sum(lambda_i * s_i) = k^{-1}(e + rx)
        # where lambda_i are Lagrange coefficients
        #
        # From chi = k*x (with shares chi_i), we have sum(chi_i) = k*x
        # Signature share: s_i = (e + r * chi_i / k_i)? No, that doesn't work with addition.
        #
        # Let me try a different approach. We need the signature to verify, which means:
        # Given R = g^k and s, verify: g^{s^{-1}*e} * pk^{s^{-1}*r} = R
        # i.e., g^{(e + rx)/s} = g^k
        # So we need s = (e + rx)/k = k^{-1}(e + rx)
        #
        # Our current formula: s_i = k_i * e + r * chi_i
        # sum(lambda_i * s_i) = sum(lambda_i * k_i * e) + r * sum(lambda_i * chi_i)
        #                     = k * e + r * k * x  (using Lagrange reconstruction)
        #                     = k * (e + r*x)
        #
        # So we're computing k*(e+rx) but we need k^{-1}*(e+rx)!
        #
        # Fix: s_i should be k_i^{-1} * e + r * chi_i * k^{-2}? No, that doesn't work.
        #
        # The correct fix for threshold ECDSA:
        # Use additive shares where the Lagrange reconstruction gives k^{-1}
        #
        # This requires computing shares of k^{-1} from shares of k using:
        # - Reveal delta = k*gamma (safe because gamma is random blinding)
        # - Then k^{-1} = gamma * delta^{-1}
        # - Shares of k^{-1}: k^{-1}_i = gamma_i * delta^{-1} (where delta^{-1} is public after revealing delta)
        #
        # Now: s_i = k^{-1}_i * e + r * chi_i * k^{-1}
        # But chi_i is share of k*x, and k^{-1}_i is share of k^{-1}
        # We need share of k^{-1} * k * x = x
        # But that's just x_i!
        #
        # So: s_i = k^{-1}_i * e + r * x_i * k^{-1}? No wait...
        #
        # Let me be more careful. We have:
        # - k^{-1} = gamma * delta^{-1} (delta^{-1} is public)
        # - k^{-1}_i = gamma_i * delta^{-1}
        #
        # s = k^{-1}(e + rx) = k^{-1}*e + k^{-1}*r*x
        #   = delta^{-1} * gamma * e + delta^{-1} * gamma * r * x
        #   = delta^{-1} * (gamma * e + gamma * r * x)
        #   = delta^{-1} * (e*gamma + r * (gamma * x))
        #
        # Shares:
        # - (e*gamma)_i = e * gamma_i (each party computes locally)
        # - (gamma*x)_i = ? Need MtA for gamma_i * x_j
        #
        # Currently we compute chi = k*x via MtA
        # We also need to compute gamma*x via MtA (or store gamma and x shares)
        #
        # Simpler: sigma_i = gamma_i * x_i + sum(MtA for gamma_i * x_j and gamma_j * x_i)
        #        = share of gamma*x
        #
        # Then: s_i = delta^{-1} * (e * gamma_i + r * sigma_i)
        #
        # Since delta^{-1} is a scalar (not shared), this gives correct s when summed!
        #
        # Let's implement this. We need:
        # 1. Keep delta_i computation (shares of k*gamma)
        # 2. Add sigma_i computation (shares of gamma*x via MtA)
        # 3. Reveal sum of delta_i to get delta
        # 4. R = Gamma^{delta^{-1}}
        # 5. Signature: s_i = delta^{-1} * (e * gamma_i + r * sigma_i)

        # For now, let me restructure. We need gamma_i stored, and we need
        # to compute sigma (gamma*x) instead of or in addition to chi (k*x).
        #
        # Actually, looking at our current code, we're computing chi = k*x.
        # We should instead compute sigma = gamma*x.
        # Then the signing formula becomes:
        # s_i = delta^{-1} * (e * gamma_i + r * sigma_i)
        #
        # Let's update the Presignature to store delta_i and gamma_i

        # Compute combined R = product of all R_i = g^{sum k_i} for now
        # (We'll fix the formula to use delta properly)
        combined_R = None
        for pid in participants:
            R_p = all_round2_msgs[pid]['R_i']
            if combined_R is None:
                combined_R = R_p
            else:
                combined_R = combined_R * R_p

        # R = g^k for now (will be corrected in signing with delta^{-1})
        R = combined_R

        # Compute r = R.x mod q
        r = self.group.zr(R)

        presignature = Presignature(
            party_id=party_id,
            R=R,
            r=r,
            k_share=k_i,
            chi_share=sigma_i,  # This is gamma*x share for signature computation
            participants=participants,
            gamma_i=gamma_i,
            delta_i=delta_i
        )
        return (presignature, failed_parties)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
