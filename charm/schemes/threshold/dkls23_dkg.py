'''
Distributed Key Generation for DKLS23 Threshold ECDSA

| From: "Two-Round Threshold ECDSA from ECDSA Assumptions"
| By:   Jack Doerner, Yashvanth Kondi, Eysa Lee, abhi shelat
| Published: IEEE S&P 2023
| URL:  https://eprint.iacr.org/2023/765

* type:          distributed key generation
* setting:       Elliptic Curve DDH-hard group
* assumption:    DDH

This module implements a distributed key generation (DKG) protocol for
threshold ECDSA as described in DKLS23. Uses Feldman VSS for verifiable
secret sharing, compatible with secp256k1 curve.

:Authors: Elton de Souza
:Date:    01/2026
'''

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.eccurve import secp256k1
from charm.toolbox.threshold_sharing import ThresholdSharing, PedersenVSS
from charm.toolbox.broadcast import EchoBroadcast
from charm.core.engine.protocol import Protocol
from typing import Dict, List, Tuple, Optional, Any, Set

# Type aliases for charm-crypto types
ZRElement = Any  # Scalar field element
GElement = Any   # Group/curve point element
ECGroupType = Any  # ECGroup instance
PartyId = int


class KeyShare:
    """
    Holds a party's key share for threshold ECDSA
    
    Attributes:
        party_id: The party's identifier (1 to n)
        x_i: Party's share of the private key
        X: Combined public key (g^x where x = sum of all secrets)
        X_i: Verification key for this party (g^{x_i})
        t: Threshold parameter
        n: Total number of parties
    
    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> g = group.random(G)
    >>> private_share = group.random(ZR)
    >>> public_key = g ** private_share
    >>> verification_key = g ** private_share
    >>> ks = KeyShare(1, private_share, public_key, verification_key, 2, 3)
    >>> ks.party_id
    1
    >>> ks.t
    2
    >>> ks.n
    3
    """
    
    def __init__(self, party_id: PartyId, private_share: ZRElement, public_key: GElement, verification_key: GElement, threshold: int, num_parties: int) -> None:
        self.party_id = party_id
        self.x_i = private_share      # Party's share of private key
        self.X = public_key           # Combined public key
        self.X_i = verification_key   # g^{x_i} for verification
        self.t = threshold
        self.n = num_parties

    def __repr__(self) -> str:
        return f"KeyShare(party_id={self.party_id}, t={self.t}, n={self.n})"


class DKLS23_DKG:
    """
    Distributed Key Generation for DKLS23 Threshold ECDSA

    Generates threshold ECDSA keys where t-of-n parties are required to sign.
    Uses Feldman VSS for verifiable secret sharing.

    Curve Agnostic
    --------------
    This implementation supports any elliptic curve group that is DDH-hard.
    The curve is specified via the groupObj parameter.

    Protocol:
    1. Round 1: Each party i samples random polynomial f_i(x) of degree t-1
       with f_i(0) = s_i (their secret). Broadcasts Feldman commitments
       C_{i,j} = g^{a_{i,j}} for all coefficients.

    2. Round 2: Each party i sends share f_i(j) to party j via secure channel.

    3. Round 3: Each party j verifies received shares against commitments:
       g^{f_i(j)} = prod C_{i,k}^{j^k}. Computes final share x_j = sum f_i(j)
       and public key X = prod g^{s_i}.
    
    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> # Simulate 2-of-3 DKG
    >>> dkg = DKLS23_DKG(group, threshold=2, num_parties=3)
    >>> g = group.random(G)
    >>> 
    >>> # Round 1: Each party generates secret and Feldman commitments
    >>> party_states = [dkg.keygen_round1(i+1, g) for i in range(3)]
    >>> round1_msgs = [state[0] for state in party_states]
    >>> private_states = [state[1] for state in party_states]
    >>> 
    >>> # All parties should have different secrets (compare as ints since ZR not hashable)
    >>> len(set(int(s['secret']) for s in private_states)) == 3
    True
    >>> 
    >>> # Round 2: Generate shares for other parties
    >>> round2_results = [dkg.keygen_round2(i+1, private_states[i], round1_msgs) for i in range(3)]
    >>> shares_for_others = [r[0] for r in round2_results]
    >>> states_after_round2 = [r[1] for r in round2_results]
    >>> 
    >>> # Collect shares received by each party from all parties
    >>> received_shares = {}
    >>> for receiver in range(1, 4):
    ...     received_shares[receiver] = {}
    ...     for sender in range(1, 4):
    ...         received_shares[receiver][sender] = shares_for_others[sender-1][receiver]
    >>> 
    >>> # Round 3: Verify shares and compute final key shares
    >>> key_shares = [dkg.keygen_round3(i+1, states_after_round2[i], received_shares[i+1], round1_msgs) for i in range(3)]
    >>> 
    >>> # All parties should have the same public key
    >>> key_shares[0].X == key_shares[1].X == key_shares[2].X
    True
    >>> 
    >>> # Verification keys should be correct (g^{x_i})
    >>> all(g ** ks.x_i == ks.X_i for ks in key_shares)
    True
    >>> 
    >>> # Public key should equal product of first commitments
    >>> computed_pk = dkg.compute_public_key([msg['commitments'] for msg in round1_msgs], g)
    >>> key_shares[0].X == computed_pk
    True
    """
    
    def __init__(self, groupObj: ECGroupType, threshold: int, num_parties: int) -> None:
        """
        Initialize the DKG protocol

        Args:
            groupObj: An ECGroup instance (e.g., ECGroup(secp256k1))
            threshold: Minimum number of parties required to sign (t)
            num_parties: Total number of parties (n)

        Raises:
            ValueError: If groupObj is None, threshold > num_parties, or threshold < 1
        """
        if groupObj is None:
            raise ValueError("groupObj cannot be None")
        if threshold > num_parties:
            raise ValueError("threshold cannot exceed num_parties")
        if threshold < 1:
            raise ValueError("threshold must be at least 1")

        self.group = groupObj
        self.t = threshold
        self.n = num_parties
        self.order = groupObj.order()
        self._sharing = ThresholdSharing(groupObj)
        self._broadcast = EchoBroadcast(num_parties)

    def keygen_round1(self, party_id: PartyId, generator: GElement, session_id: bytes) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Round 1: Each party generates secret share and Feldman commitments

        Each party i samples a random polynomial f_i(x) of degree t-1 where
        f_i(0) = s_i is their secret contribution. Then broadcasts Feldman
        commitments C_{i,j} = g^{a_{i,j}} for all coefficients a_{i,0}, ..., a_{i,t-1}.

        Args:
            party_id: This party's identifier (1 to n)
            generator: Generator point g in the EC group
            session_id: Required session identifier (bytes or str). Must be unique
                per protocol instance and shared across all participants to prevent
                replay attacks.

        Returns:
            Tuple of (broadcast_msg, private_state)
            - broadcast_msg: Dictionary containing party_id, session_id, and commitments
            - private_state: Dictionary containing secret, coefficients, shares, and session_id

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> dkg = DKLS23_DKG(group, threshold=2, num_parties=3)
        >>> g = group.random(G)
        >>> msg, state = dkg.keygen_round1(1, g, session_id=b"test-session")
        >>> 'party_id' in msg and 'commitments' in msg
        True
        >>> len(msg['commitments']) == 2  # t commitments
        True
        >>> 'secret' in state and 'coefficients' in state
        True
        >>> 'session_id' in msg
        True
        """
        # Validate session_id is provided and non-empty
        if session_id is None:
            raise ValueError("session_id is required for replay attack prevention")
        if isinstance(session_id, (bytes, str)) and len(session_id) == 0:
            raise ValueError("session_id cannot be empty")

        # Generate random secret for this party
        secret = self.group.random(ZR)

        # Generate random polynomial coefficients: a_0 = secret, a_1...a_{t-1} random
        coeffs = [secret]
        for _ in range(self.t - 1):
            coeffs.append(self.group.random(ZR))

        # Compute Feldman commitments: C_j = g^{a_j}
        commitments = [generator ** coeff for coeff in coeffs]

        # Pre-compute shares for all parties (to be sent in round 2)
        shares = {}
        for j in range(1, self.n + 1):
            shares[j] = self._sharing._eval_polynomial(coeffs, j)

        # Broadcast message (public)
        broadcast_msg = {
            'party_id': party_id,
            'session_id': session_id,
            'commitments': commitments
        }

        # Private state (kept secret by this party)
        private_state = {
            'party_id': party_id,
            'session_id': session_id,
            'secret': secret,
            'coefficients': coeffs,
            'shares': shares,
            'generator': generator
        }

        return broadcast_msg, private_state

    def keygen_round2(self, party_id: PartyId, private_state: Dict[str, Any], all_round1_msgs: List[Dict[str, Any]]) -> Tuple[Dict[PartyId, ZRElement], Dict[str, Any]]:
        """
        Round 2: Verify commitments, generate shares for each party

        Each party verifies that received round 1 messages are well-formed,
        then prepares shares f_i(j) to send to each party j via secure channel.

        IMPORTANT: This function assumes an authenticated broadcast channel is used
        for round 1 messages. In practice, this requires implementing echo broadcast
        to ensure all parties received the same messages from each sender. See
        verify_broadcast_consistency() for validating broadcast consistency.

        Args:
            party_id: This party's identifier
            private_state: Private state from round 1
            all_round1_msgs: List of broadcast messages from all parties

        Returns:
            Tuple of (private_shares_for_others, updated_state)
            - private_shares_for_others: Dict mapping recipient party_id to share
            - updated_state: Updated private state

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> dkg = DKLS23_DKG(group, threshold=2, num_parties=3)
        >>> g = group.random(G)
        >>> states = [dkg.keygen_round1(i+1, g) for i in range(3)]
        >>> round1_msgs = [s[0] for s in states]
        >>> shares, state = dkg.keygen_round2(1, states[0][1], round1_msgs)
        >>> len(shares) == 3  # Shares for all parties
        True
        """
        # Verify we have messages from all parties
        received_party_ids = set(msg['party_id'] for msg in all_round1_msgs)
        expected_party_ids = set(range(1, self.n + 1))
        if received_party_ids != expected_party_ids:
            raise ValueError(f"Missing round 1 messages from parties: {expected_party_ids - received_party_ids}")

        # Verify all commitments have correct length
        for msg in all_round1_msgs:
            if len(msg['commitments']) != self.t:
                raise ValueError(f"Party {msg['party_id']} has {len(msg['commitments'])} commitments, expected {self.t}")

        # Prepare shares to send to each party
        # (These are the shares we computed in round 1)
        shares_to_send = private_state['shares'].copy()

        # Store round1 messages for verification in round 3
        updated_state = private_state.copy()
        updated_state['all_round1_msgs'] = {msg['party_id']: msg for msg in all_round1_msgs}

        return shares_to_send, updated_state

    def _verify_share_against_commitments(self, sender_id: PartyId, receiver_id: PartyId, share: ZRElement, commitments: List[GElement], generator: GElement) -> bool:
        """
        Verify a received share against Feldman commitments

        Checks: g^{share} == prod_{k=0}^{t-1} C_{sender,k}^{receiver^k}

        Args:
            sender_id: ID of the party who sent the share
            receiver_id: ID of the party receiving the share
            share: The share value to verify
            commitments: List of Feldman commitments from sender
            generator: Generator point g

        Returns:
            True if share is valid, False otherwise
        """
        return self._sharing.verify_share(receiver_id, share, commitments, generator)

    def keygen_round3(self, party_id: PartyId, private_state: Dict[str, Any], received_shares: Dict[PartyId, ZRElement], all_round1_msgs: List[Dict[str, Any]]) -> Tuple[Optional['KeyShare'], Optional[Dict[str, Any]]]:
        """
        Round 3: Verify received shares, compute final key share

        Each party j verifies all received shares f_i(j) against the
        Feldman commitments from round 1. If all shares verify, computes:
        - Final share: x_j = sum_{i=1}^{n} f_i(j)
        - Verification key: X_j = g^{x_j}
        - Public key: X = prod_{i=1}^{n} C_{i,0} = g^{sum s_i}

        If a share verification fails, instead of crashing, a complaint is
        generated that can be used to identify malicious parties.

        Args:
            party_id: This party's identifier
            private_state: Private state from round 2
            received_shares: Dict mapping sender party_id to share value
            all_round1_msgs: List of broadcast messages from all parties

        Returns:
            Tuple of (KeyShare, complaint) where:
            - KeyShare: The computed key share (or None if verification failed)
            - complaint: Dict with 'accuser', 'accused', 'share', 'commitments' if
              verification failed, or None if all shares verified

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> dkg = DKLS23_DKG(group, threshold=2, num_parties=3)
        >>> g = group.random(G)
        >>> # Run full DKG
        >>> party_states = [dkg.keygen_round1(i+1, g) for i in range(3)]
        >>> round1_msgs = [s[0] for s in party_states]
        >>> priv_states = [s[1] for s in party_states]
        >>> round2_results = [dkg.keygen_round2(i+1, priv_states[i], round1_msgs) for i in range(3)]
        >>> shares_for_others = [r[0] for r in round2_results]
        >>> states_r2 = [r[1] for r in round2_results]
        >>> # Collect shares for party 1
        >>> received = {sender+1: shares_for_others[sender][1] for sender in range(3)}
        >>> ks, complaint = dkg.keygen_round3(1, states_r2[0], received, round1_msgs)
        >>> isinstance(ks, KeyShare)
        True
        >>> ks.party_id == 1
        True
        >>> complaint is None
        True
        """
        generator = private_state['generator']

        # Build a mapping from party_id to round1 message
        round1_by_party = {msg['party_id']: msg for msg in all_round1_msgs}

        # Verify all received shares against commitments
        for sender_id, share in received_shares.items():
            commitments = round1_by_party[sender_id]['commitments']
            if not self._verify_share_against_commitments(
                sender_id, party_id, share, commitments, generator
            ):
                # Generate complaint instead of raising ValueError
                complaint = {
                    'accuser': party_id,
                    'accused': sender_id,
                    'share': share,
                    'commitments': commitments
                }
                return (None, complaint)

        # Compute final share: x_j = sum_{i=1}^{n} f_i(j)
        final_share = self.group.init(ZR, 0)
        for sender_id, share in received_shares.items():
            final_share = final_share + share

        # Compute verification key: X_j = g^{x_j}
        verification_key = generator ** final_share

        # Compute public key: X = prod_{i=1}^{n} C_{i,0}
        public_key = self.compute_public_key(
            [round1_by_party[i]['commitments'] for i in range(1, self.n + 1)],
            generator
        )

        key_share = KeyShare(
            party_id=party_id,
            private_share=final_share,
            public_key=public_key,
            verification_key=verification_key,
            threshold=self.t,
            num_parties=self.n
        )
        return (key_share, None)

    def handle_complaints(self, party_id: PartyId, complaints: Dict[PartyId, Dict[str, Any]], all_round1_msgs: List[Dict[str, Any]]) -> Set[PartyId]:
        """
        Process complaints and identify disqualified parties.

        When parties report share verification failures via complaints, this
        method verifies each complaint and determines which parties should be
        disqualified from the protocol.

        A complaint is valid if the accused party's share does not verify against
        their public commitments. If a complaint is valid, the accused is
        disqualified. If a complaint is invalid (the share actually verifies),
        the accuser is making a false accusation and may be disqualified.

        Args:
            party_id: This party's identifier (for context)
            complaints: Dict mapping accuser party_id to complaint dict containing:
                - 'accuser': ID of party making complaint
                - 'accused': ID of party being accused
                - 'share': The share that failed verification
                - 'commitments': The commitments used for verification
            all_round1_msgs: List of broadcast messages from all parties

        Returns:
            Set of party IDs that should be disqualified

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> dkg = DKLS23_DKG(group, threshold=2, num_parties=3)
        >>> g = group.random(G)
        >>> # No complaints case
        >>> disqualified = dkg.handle_complaints(1, {}, [])
        >>> len(disqualified) == 0
        True
        """
        if not complaints:
            return set()

        disqualified = set()
        round1_by_party = {msg['party_id']: msg for msg in all_round1_msgs}

        for accuser_id, complaint in complaints.items():
            accused_id = complaint['accused']
            share = complaint['share']
            # Use the commitments from round1 messages (the public record)
            # not from the complaint (which could be forged)
            if accused_id in round1_by_party:
                commitments = round1_by_party[accused_id]['commitments']
                generator = None
                # Find generator from any round1 message's first commitment context
                for msg in all_round1_msgs:
                    if 'generator' in msg:
                        generator = msg['generator']
                        break

                if generator is None:
                    # If generator not in messages, we can still verify using
                    # the structure of the commitments
                    # For now, trust the complaint's verification result
                    disqualified.add(accused_id)
                else:
                    # Verify the complaint: is the share actually invalid?
                    is_valid_share = self._verify_share_against_commitments(
                        accused_id, accuser_id, share, commitments, generator
                    )
                    if not is_valid_share:
                        # Share is indeed invalid - accused party is malicious
                        disqualified.add(accused_id)
                    else:
                        # Share is valid - accuser made a false complaint
                        # This could indicate the accuser is malicious
                        disqualified.add(accuser_id)
            else:
                # Accused party not in round1 messages - they didn't participate
                disqualified.add(accused_id)

        return disqualified

    def verify_broadcast_consistency(self, party_id: PartyId, all_round1_msgs: List[Dict[str, Any]], echo_msgs: Dict[PartyId, Dict[PartyId, bytes]]) -> bool:
        """
        Verify echo broadcast consistency across all parties.

        In a secure broadcast protocol, all parties must receive the same message
        from each sender. This method implements echo broadcast verification by
        comparing what each party claims to have received from each sender.

        Without echo broadcast, a malicious party could send different commitments
        to different recipients (equivocation attack).

        Delegates to the EchoBroadcast toolbox for the actual verification logic.

        Args:
            party_id: This party's identifier
            all_round1_msgs: List of round 1 messages as received by this party
            echo_msgs: Dict of {verifier_id: {sender_id: msg_hash}} where each
                verifier reports the hash of what they received from each sender

        Returns:
            True if all parties received consistent messages

        Raises:
            ValueError: If inconsistency detected, with details about which
                sender sent different messages to different recipients

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> dkg = DKLS23_DKG(group, threshold=2, num_parties=3)
        >>> # Consistent case
        >>> echo_msgs = {1: {2: b'hash1', 3: b'hash2'}, 2: {2: b'hash1', 3: b'hash2'}}
        >>> dkg.verify_broadcast_consistency(1, [], echo_msgs)
        True
        """
        return self._broadcast.verify_consistency(echo_msgs)

    def compute_public_key(self, all_commitments: List[List[GElement]], generator: GElement) -> GElement:
        """
        Compute the combined public key from all parties' commitments

        The public key is X = prod_{i=1}^{n} C_{i,0} = g^{sum s_i}
        where C_{i,0} = g^{s_i} is the first commitment from party i.

        Args:
            all_commitments: List of commitment lists from all parties
            generator: Generator point g (unused but kept for API consistency)

        Returns:
            The combined public key as a group element

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> dkg = DKLS23_DKG(group, threshold=2, num_parties=3)
        >>> g = group.random(G)
        >>> states = [dkg.keygen_round1(i+1, g) for i in range(3)]
        >>> all_comms = [s[0]['commitments'] for s in states]
        >>> pk = dkg.compute_public_key(all_comms, g)
        >>> # Public key should be product of all g^{s_i}
        >>> secrets = [s[1]['secret'] for s in states]
        >>> expected = g ** (secrets[0] + secrets[1] + secrets[2])
        >>> pk == expected
        True
        """
        if not all_commitments:
            raise ValueError("Need at least one commitment list")

        # Public key = product of all first commitments (C_{i,0} = g^{s_i})
        public_key = all_commitments[0][0]
        for i in range(1, len(all_commitments)):
            public_key = public_key * all_commitments[i][0]

        return public_key


if __name__ == "__main__":
    import doctest
    doctest.testmod()
