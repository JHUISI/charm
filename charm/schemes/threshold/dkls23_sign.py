'''
DKLS23 Signing Protocol and Main Class for Threshold ECDSA

| From: "Two-Round Threshold ECDSA from ECDSA Assumptions"
| By:   Jack Doerner, Yashvanth Kondi, Eysa Lee, abhi shelat
| Published: IEEE S&P 2023
| URL:  https://eprint.iacr.org/2023/765

* type:          threshold signing
* setting:       Elliptic Curve DDH-hard group
* assumption:    DDH + OT security

This module implements the signing phase of the DKLS23 threshold ECDSA
protocol, combining presignatures with messages to produce standard
ECDSA signatures that can be verified by any ECDSA implementation.

Protocol Overview:
1. Sign Round: Each party i computes signature share:
   s_i = k_i * H(m) + r * χ_i (where χ_i is their share of k*x)

2. Combine: Use Lagrange coefficients to combine shares:
   s = ∑ λ_i * s_i mod q

3. Normalize: If s > q/2, set s = q - s (low-s normalization for malleability)

:Authors: Elton de Souza
:Date:    01/2026
'''

from typing import Dict, List, Tuple, Optional, Any, Union

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.eccurve import secp256k1
from charm.toolbox.PKSig import PKSig
from charm.toolbox.threshold_sharing import ThresholdSharing
from charm.toolbox.Hash import Hash
from charm.schemes.threshold.dkls23_dkg import DKLS23_DKG, KeyShare
from charm.schemes.threshold.dkls23_presign import DKLS23_Presign, Presignature

# Type aliases for charm-crypto types
ZRElement = Any  # Scalar field element
GElement = Any   # Group/curve point element
ECGroupType = Any  # ECGroup instance
PartyId = int


class ThresholdSignature:
    """
    Represents a threshold ECDSA signature.
    
    Contains the (r, s) values that form a standard ECDSA signature.
    
    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> r = group.random(ZR)
    >>> s = group.random(ZR)
    >>> sig = ThresholdSignature(r, s)
    >>> sig.r == r and sig.s == s
    True
    """
    
    def __init__(self, r: ZRElement, s: ZRElement) -> None:
        """
        Initialize a threshold signature.

        Args:
            r: The r component (x-coordinate of R point mod q)
            s: The s component (signature value)
        """
        self.r = r
        self.s = s

    def __repr__(self) -> str:
        return f"ThresholdSignature(r=..., s=...)"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ThresholdSignature):
            return self.r == other.r and self.s == other.s
        return False

    def to_der(self) -> bytes:
        """
        Convert to DER encoding for external verification.
        
        Returns:
            DER-encoded signature bytes.
        
        Note: This requires the r and s values to be convertible to integers.
        """
        def int_to_der_integer(val):
            """Convert integer to DER INTEGER encoding."""
            if hasattr(val, '__int__'):
                val = int(val)
            val_bytes = val.to_bytes((val.bit_length() + 7) // 8, 'big')
            # Add leading zero if high bit is set (for positive representation)
            if val_bytes[0] & 0x80:
                val_bytes = b'\x00' + val_bytes
            return bytes([0x02, len(val_bytes)]) + val_bytes
        
        r_der = int_to_der_integer(self.r)
        s_der = int_to_der_integer(self.s)
        sequence = r_der + s_der
        return bytes([0x30, len(sequence)]) + sequence


class DKLS23_Sign:
    """
    DKLS23 Signing Protocol
    
    Combines presignatures with message to produce threshold ECDSA signature.
    
    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> signer = DKLS23_Sign(group)
    >>> # Simulate presignatures for a 2-of-3 setup
    >>> g = group.random(G)
    >>> k = group.random(ZR)  # Combined nonce
    >>> x = group.random(ZR)  # Combined private key
    >>> chi = k * x           # k*x product
    >>> R = g ** k
    >>> r = group.zr(R)
    >>> # Create share components (simplified for testing)
    >>> ts = ThresholdSharing(group)
    >>> k_shares = ts.share(k, 2, 3)
    >>> chi_shares = ts.share(chi, 2, 3)
    >>> presigs = {}
    >>> for pid in [1, 2]:
    ...     presigs[pid] = Presignature(pid, R, r, k_shares[pid], chi_shares[pid], [1, 2])
    >>> # Create key share (simplified)
    >>> key_share = KeyShare(1, ts.share(x, 2, 3)[1], g ** x, g ** ts.share(x, 2, 3)[1], 2, 3)
    >>> message = b"test message"
    >>> sig_share, proof = signer.sign_round1(1, presigs[1], key_share, message, [1, 2])
    >>> sig_share is not None
    True
    """
    
    def __init__(self, groupObj: ECGroupType) -> None:
        """
        Initialize the signing protocol.

        Args:
            groupObj: An ECGroup instance (e.g., ECGroup(secp256k1))

        Raises:
            ValueError: If groupObj is None
        """
        if groupObj is None:
            raise ValueError("groupObj cannot be None")
        self.group = groupObj
        self.order = int(groupObj.order())  # Convert to int for modular arithmetic
        self._sharing = ThresholdSharing(groupObj)

    def _hash_message(self, message: bytes) -> ZRElement:
        """
        Hash message to a scalar using group.hash() with domain separation.

        Uses group.hash() for proper domain separation and consistent
        hash-to-field element conversion.

        Args:
            message: Message bytes to hash

        Returns:
            Hash as a ZR element
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        return self.group.hash((b"ECDSA_MSG:", message), target_type=ZR)

    def sign_round1(self, party_id: PartyId, presignature: Presignature, key_share: KeyShare, message: bytes, participants: List[PartyId], delta_inv: ZRElement, prehashed: bool = False) -> Tuple[ZRElement, Dict[str, Any]]:
        """
        Generate signature share for message.

        Computes s_i = delta^{-1} * (e * gamma_i + r * sigma_i)
        where sigma_i is stored in chi_i (share of gamma*x)

        Args:
            party_id: This party's identifier
            presignature: Presignature object for this party
            key_share: KeyShare object for this party
            message: Message bytes to sign
            participants: List of participating party IDs
            delta_inv: Inverse of delta = sum(delta_i), computed externally (required)
            prehashed: If True, message is already a 32-byte hash (no additional hashing).
                       Use this for protocols like XRPL that provide their own signing hash.

        Returns:
            Tuple of (signature_share, proof)
            - signature_share: Party's contribution to s
            - proof: Placeholder for ZK proof (dict)

        Raises:
            ValueError: If delta_inv is None

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> signer = DKLS23_Sign(group)
        >>> g = group.random(G)
        >>> k_i = group.random(ZR)
        >>> gamma_i = group.random(ZR)
        >>> sigma_i = group.random(ZR)
        >>> delta_i = k_i * gamma_i
        >>> R = g ** group.random(ZR)
        >>> r = group.zr(R)
        >>> ps = Presignature(1, R, r, k_i, sigma_i, [1, 2], gamma_i, delta_i)
        >>> ks = KeyShare(1, group.random(ZR), g, g, 2, 3)
        >>> delta_inv = delta_i ** -1  # Simplified for test
        >>> share, proof = signer.sign_round1(1, ps, ks, b"test", [1, 2], delta_inv)
        >>> share is not None
        True
        """
        # Hash the message: e = H(m)
        if prehashed:
            # Message is already a 32-byte hash
            if len(message) != 32:
                raise ValueError("prehashed message must be exactly 32 bytes")
            h_int = int.from_bytes(message, 'big') % self.order
            e = self.group.init(ZR, h_int)
        else:
            e = self._hash_message(message)

        # Get presignature components
        gamma_i = presignature.gamma_i
        sigma_i = presignature.chi_i  # sigma_i = share of gamma*x
        r = presignature.r

        # Validate required delta_inv parameter
        if delta_inv is None:
            raise ValueError("delta_inv is required for valid signature generation")

        # DKLS23 formula: s_i = delta^{-1} * (e * gamma_i + r * sigma_i)
        s_i = delta_inv * ((e * gamma_i) + (r * sigma_i))

        # Proof placeholder (in full implementation, would include ZK proof)
        proof = {
            'party_id': party_id,
            'R': presignature.R
        }

        return s_i, proof

    def verify_signature_share(self, party_id: PartyId, share: ZRElement, proof: Dict[str, Any], presignature: Presignature, message: bytes) -> bool:
        """
        Verify a signature share is well-formed.

        Args:
            party_id: The party that generated the share
            share: The signature share (s_i value)
            proof: The proof from sign_round1
            presignature: The presignature used
            message: The message being signed

        Returns:
            bool: True if share appears valid, False otherwise
        """
        # Basic validation: check share is a valid ZR element
        if share is None:
            return False

        # Check share is in valid range (0, order)
        try:
            share_int = int(share)
            if share_int <= 0 or share_int >= self.order:
                return False
        except:
            return False

        # Verify proof contains expected party_id
        if proof.get('party_id') != party_id:
            return False

        return True

    def combine_signatures(self, signature_shares: Dict[PartyId, ZRElement], presignature: Presignature, participants: List[PartyId], proofs: Optional[Dict[PartyId, Dict[str, Any]]] = None, message: Optional[bytes] = None) -> 'ThresholdSignature':
        """
        Combine signature shares into final signature.

        In DKLS23, signature shares are additive (not polynomial shares),
        so we use simple sum instead of Lagrange interpolation.

        Args:
            signature_shares: Dict mapping party_id to signature share
            presignature: Any party's presignature (for r value)
            participants: List of participating party IDs
            proofs: Optional dict mapping party_id to proof from sign_round1
            message: Optional message bytes (required if proofs provided)

        Returns:
            ThresholdSignature object with (r, s)

        Raises:
            ValueError: If a signature share fails verification

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> signer = DKLS23_Sign(group)
        >>> # Simulate signature shares
        >>> s1 = group.random(ZR)
        >>> s2 = group.random(ZR)
        >>> shares = {1: s1, 2: s2}
        >>> g = group.random(G)
        >>> R = g ** group.random(ZR)
        >>> r = group.zr(R)
        >>> ps = Presignature(1, R, r, group.random(ZR), group.random(ZR), [1, 2])
        >>> sig = signer.combine_signatures(shares, ps, [1, 2])
        >>> isinstance(sig, ThresholdSignature)
        True
        """
        r = presignature.r

        # DKLS23: Signature shares are additive, so just sum them
        # s = sum(s_i) where s_i = delta^{-1} * (e * gamma_i + r * sigma_i)
        # The delta^{-1} factor ensures correct reconstruction
        s = self.group.init(ZR, 0)

        for party_id in participants:
            if party_id in signature_shares:
                share = signature_shares[party_id]

                # Verify share if proofs provided
                if proofs is not None and message is not None:
                    proof = proofs.get(party_id, {})
                    if not self.verify_signature_share(party_id, share, proof, presignature, message):
                        raise ValueError(f"Invalid signature share from party {party_id}")

                s = s + share

        # Low-s normalization: if s > q/2, set s = q - s
        # This prevents signature malleability
        s = self._normalize_s(s)

        return ThresholdSignature(r, s)

    def _normalize_s(self, s: ZRElement) -> ZRElement:
        """
        Normalize s to low-s form (BIP-62 / BIP-146 compliant).

        If s > order/2, return order - s.
        This prevents signature malleability where (r, s) and (r, order-s)
        are both valid signatures for the same message.

        Args:
            s: The s value to normalize (ZR element)

        Returns:
            Normalized s value as ZR element
        """
        # Convert to integer for comparison
        s_int = int(s) % self.order
        half_order = self.order // 2

        if s_int > half_order:
            # s is in high range, normalize to low-s form
            normalized_s_int = self.order - s_int
            return self.group.init(ZR, normalized_s_int)

        return s

    def verify(self, public_key: GElement, signature: Union['ThresholdSignature', Tuple[ZRElement, ZRElement]], message: bytes, generator: GElement) -> bool:
        """
        Verify ECDSA signature (standard verification).

        This verifies standard ECDSA signatures that can be checked
        by any ECDSA implementation.

        Args:
            public_key: The combined public key (EC point)
            signature: ThresholdSignature or tuple (r, s)
            message: The message that was signed
            generator: Generator point g

        Returns:
            True if valid, False otherwise

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> signer = DKLS23_Sign(group)
        >>> g = group.random(G)
        >>> # Create valid signature manually
        >>> x = group.random(ZR)  # private key
        >>> pk = g ** x           # public key
        >>> k = group.random(ZR)  # nonce
        >>> R = g ** k
        >>> r = group.zr(R)
        >>> message = b"test message"
        >>> e = signer._hash_message(message)
        >>> s = (e + r * x) * (k ** -1)  # Standard ECDSA: s = k^{-1}(e + rx)
        >>> sig = ThresholdSignature(r, s)
        >>> signer.verify(pk, sig, message, g)
        True
        """
        if isinstance(signature, tuple):
            r, s = signature
        else:
            r, s = signature.r, signature.s

        # Hash the message
        e = self._hash_message(message)

        # Compute s^{-1}
        s_inv = s ** -1

        # Compute u1 = e * s^{-1} and u2 = r * s^{-1}
        u1 = e * s_inv
        u2 = r * s_inv

        # Compute R' = u1 * G + u2 * public_key
        R_prime = (generator ** u1) * (public_key ** u2)

        # Get x-coordinate of R'
        r_prime = self.group.zr(R_prime)

        # Verify r == r'
        return r == r_prime


class DKLS23(PKSig):
    """
    DKLS23 Threshold ECDSA - Complete Implementation

    Implements t-of-n threshold ECDSA signatures using the DKLS23 protocol.
    Produces standard ECDSA signatures verifiable by any implementation.

    Curve Agnostic
    --------------
    This implementation supports any elliptic curve group that is DDH-hard
    (Decisional Diffie-Hellman). The curve is specified via the groupObj
    parameter - examples include secp256k1, prime256v1 (P-256/secp256r1),
    secp384r1, secp521r1, etc.

    Example with secp256k1:
    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> dkls = DKLS23(group, threshold=2, num_parties=3, party_id=1)

    Example with prime256v1 (P-256):
    >>> from charm.toolbox.eccurve import prime256v1
    >>> group = ECGroup(prime256v1)
    >>> dkls = DKLS23(group, threshold=2, num_parties=3, party_id=1)

    Full Example
    ------------
    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> dkls = DKLS23(group, threshold=2, num_parties=3)
    >>> g = group.random(G)
    >>>
    >>> # Step 1: Distributed Key Generation
    >>> key_shares, public_key = dkls.distributed_keygen(g)
    >>>
    >>> # Step 2: Generate presignatures (can be done offline)
    >>> presignatures = dkls.presign([1, 2], key_shares, g)
    >>>
    >>> # Step 3: Sign a message
    >>> message = b"Hello, threshold ECDSA!"
    >>> signature = dkls.sign([1, 2], presignatures, key_shares, message, g)
    >>>
    >>> # Step 4: Verify (standard ECDSA verification)
    >>> dkls.verify(public_key, signature, message, g)
    True
    """

    def __init__(self, groupObj: ECGroupType, threshold: int = 2, num_parties: int = 3) -> None:
        """
        Initialize DKLS23 threshold ECDSA.

        Args:
            groupObj: An ECGroup instance (e.g., ECGroup(secp256k1))
            threshold: Minimum number of parties required to sign (t)
            num_parties: Total number of parties (n)

        Raises:
            ValueError: If threshold > num_parties or threshold < 1
        """
        PKSig.__init__(self)
        self.group = groupObj
        self.t = threshold
        self.n = num_parties

        if threshold > num_parties:
            raise ValueError("threshold cannot exceed num_parties")
        if threshold < 1:
            raise ValueError("threshold must be at least 1")

        # Initialize component protocols
        self._dkg = DKLS23_DKG(groupObj, threshold, num_parties)
        self._presign = DKLS23_Presign(groupObj)
        self._sign = DKLS23_Sign(groupObj)
        self._sharing = ThresholdSharing(groupObj)

    def keygen(self, securityparam: Optional[int] = None, generator: Optional[GElement] = None) -> Tuple[Dict[PartyId, KeyShare], GElement]:
        """
        Key generation interface (PKSig compatibility).

        Args:
            securityparam: Security parameter (unused, curve-dependent)
            generator: Generator point g

        Returns:
            Tuple of (key_shares, public_key)
        """
        if generator is None:
            generator = self.group.random(G)
        return self.distributed_keygen(generator)

    def distributed_keygen(self, generator: GElement) -> Tuple[Dict[PartyId, KeyShare], GElement]:
        """
        Run the full DKG protocol.

        Executes all rounds of the distributed key generation protocol
        to produce key shares for all parties and the combined public key.

        Args:
            generator: Generator point g in the EC group

        Returns:
            Tuple of (key_shares_dict, public_key)
            - key_shares_dict: {party_id: KeyShare}
            - public_key: Combined public key (EC point)

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> dkls = DKLS23(group, threshold=2, num_parties=3)
        >>> g = group.random(G)
        >>> key_shares, pk = dkls.distributed_keygen(g)
        >>> len(key_shares) == 3
        True
        >>> all(ks.X == pk for ks in key_shares.values())
        True
        """
        # Generate a shared session ID for all participants (DKG)
        from charm.toolbox.securerandom import OpenSSLRand
        session_id = OpenSSLRand().getRandomBytes(32)

        # Round 1: Each party generates secret and Feldman commitments
        round1_results = {}
        private_states = {}
        for party_id in range(1, self.n + 1):
            broadcast_msg, private_state = self._dkg.keygen_round1(party_id, generator, session_id)
            round1_results[party_id] = broadcast_msg
            private_states[party_id] = private_state

        # Collect all round 1 messages
        all_round1_msgs = list(round1_results.values())

        # Round 2: Generate shares for other parties
        shares_for_others = {}
        states_after_round2 = {}
        for party_id in range(1, self.n + 1):
            shares, state = self._dkg.keygen_round2(
                party_id, private_states[party_id], all_round1_msgs
            )
            shares_for_others[party_id] = shares
            states_after_round2[party_id] = state

        # Collect shares received by each party
        received_shares = {}
        for receiver in range(1, self.n + 1):
            received_shares[receiver] = {}
            for sender in range(1, self.n + 1):
                received_shares[receiver][sender] = shares_for_others[sender][receiver]

        # Round 3: Verify shares and compute final key shares
        key_shares = {}
        for party_id in range(1, self.n + 1):
            ks, complaint = self._dkg.keygen_round3(
                party_id,
                states_after_round2[party_id],
                received_shares[party_id],
                all_round1_msgs
            )
            if complaint is not None:
                raise ValueError(f"DKG failed: party {complaint['accuser']} complained about party {complaint['accused']}")
            key_shares[party_id] = ks

        # All parties should have the same public key
        public_key = key_shares[1].X

        return key_shares, public_key

    def presign(self, participants: List[PartyId], key_shares: Dict[PartyId, KeyShare], generator: GElement) -> Dict[PartyId, Presignature]:
        """
        Run presigning for given participants.

        Executes the 3-round presigning protocol to generate presignatures
        that can later be combined with a message.

        Args:
            participants: List of participating party IDs (must have at least t)
            key_shares: Dict mapping party_id to KeyShare
            generator: Generator point g

        Returns:
            Dict mapping party_id to Presignature

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> dkls = DKLS23(group, threshold=2, num_parties=3)
        >>> g = group.random(G)
        >>> key_shares, pk = dkls.distributed_keygen(g)
        >>> presigs = dkls.presign([1, 2], key_shares, g)
        >>> len(presigs) == 2
        True
        >>> all(p.is_valid() for p in presigs.values())
        True
        """
        if len(participants) < self.t:
            raise ValueError(f"Need at least {self.t} participants, got {len(participants)}")

        # Generate a shared session ID for all participants
        from charm.toolbox.securerandom import OpenSSLRand
        session_id = OpenSSLRand().getRandomBytes(32)

        # Round 1: Each party generates nonce share and prepares MtA
        r1_results = {}
        states = {}
        for pid in participants:
            broadcast, state = self._presign.presign_round1(
                pid, key_shares[pid].x_i, participants, generator, session_id=session_id
            )
            r1_results[pid] = broadcast
            states[pid] = state

        # Round 2: Process MtA and share gamma commitments
        r2_results = {}
        p2p_msgs = {}
        for pid in participants:
            broadcast, p2p, state = self._presign.presign_round2(pid, states[pid], r1_results)
            r2_results[pid] = broadcast
            p2p_msgs[pid] = p2p
            states[pid] = state

        # Collect p2p messages from round 2 for each party
        p2p_received_r2 = {}
        for receiver in participants:
            p2p_received_r2[receiver] = {}
            for sender in participants:
                if sender != receiver:
                    p2p_received_r2[receiver][sender] = p2p_msgs[sender][receiver]

        # Round 3: Process MtA sender completions and send OT data
        r3_p2p_msgs = {}
        for pid in participants:
            p2p_r3, state = self._presign.presign_round3(pid, states[pid], r2_results, p2p_received_r2[pid])
            r3_p2p_msgs[pid] = p2p_r3
            states[pid] = state

        # Collect p2p messages from round 3 for each party
        p2p_received_r3 = {}
        for receiver in participants:
            p2p_received_r3[receiver] = {}
            for sender in participants:
                if sender != receiver:
                    p2p_received_r3[receiver][sender] = r3_p2p_msgs[sender][receiver]

        # Round 4: Complete MtA receiver side and compute presignature
        presignatures = {}
        for pid in participants:
            presig, failed_parties = self._presign.presign_round4(pid, states[pid], p2p_received_r3[pid])
            if failed_parties:
                raise ValueError(f"Presigning failed: parties {failed_parties} had commitment verification failures")
            presignatures[pid] = presig

        return presignatures

    def sign(self, participants: List[PartyId], presignatures: Dict[PartyId, Presignature], key_shares: Dict[PartyId, KeyShare], message: bytes, generator: GElement, prehashed: bool = False) -> 'ThresholdSignature':
        """
        Sign a message using presignatures.

        Combines presignatures with a message to produce a standard ECDSA signature.

        Args:
            participants: List of participating party IDs
            presignatures: Dict mapping party_id to Presignature
            key_shares: Dict mapping party_id to KeyShare
            message: Message bytes to sign
            generator: Generator point g
            prehashed: If True, message is already a 32-byte hash (no additional hashing).
                       Use this for protocols like XRPL that provide their own signing hash.

        Returns:
            ThresholdSignature object with (r, s)

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> dkls = DKLS23(group, threshold=2, num_parties=3)
        >>> g = group.random(G)
        >>> key_shares, pk = dkls.distributed_keygen(g)
        >>> presigs = dkls.presign([1, 2], key_shares, g)
        >>> msg = b"Hello, threshold ECDSA!"
        >>> sig = dkls.sign([1, 2], presigs, key_shares, msg, g)
        >>> isinstance(sig, ThresholdSignature)
        True
        """
        if len(participants) < self.t:
            raise ValueError(f"Need at least {self.t} participants, got {len(participants)}")

        # Step 1: Compute delta = sum of all delta_i shares
        # In DKLS23, delta = k*gamma where gamma is random blinding
        # This is safe to reveal because gamma makes it uniformly random
        delta = self.group.init(ZR, 0)
        for pid in participants:
            delta = delta + presignatures[pid].delta_i

        # Compute delta^{-1} for use in signature shares
        delta_inv = delta ** -1

        # Step 2: Each party generates their signature share
        # s_i = delta^{-1} * (e * gamma_i + r * sigma_i)
        signature_shares = {}
        for pid in participants:
            s_i, proof = self._sign.sign_round1(
                pid, presignatures[pid], key_shares[pid], message, participants, delta_inv, prehashed
            )
            signature_shares[pid] = s_i

        # Step 3: Combine signature shares (simple sum, no Lagrange needed)
        # s = sum(s_i) = delta^{-1} * (e * gamma + r * gamma*x) = k^{-1}(e + rx)
        first_pid = participants[0]
        signature = self._sign.combine_signatures(
            signature_shares, presignatures[first_pid], participants
        )

        return signature

    def verify(self, public_key: GElement, signature: Union['ThresholdSignature', Tuple[ZRElement, ZRElement]], message: bytes, generator: GElement) -> bool:
        """
        Verify signature (standard ECDSA).

        Verifies that the signature is valid for the message and public key.
        Uses standard ECDSA verification, compatible with any ECDSA implementation.

        Args:
            public_key: The combined public key (EC point)
            signature: ThresholdSignature or tuple (r, s)
            message: The message that was signed
            generator: Generator point g

        Returns:
            True if valid, False otherwise

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> dkls = DKLS23(group, threshold=2, num_parties=3)
        >>> g = group.random(G)
        >>> key_shares, pk = dkls.distributed_keygen(g)
        >>> presigs = dkls.presign([1, 2], key_shares, g)
        >>> msg = b"Test message"
        >>> sig = dkls.sign([1, 2], presigs, key_shares, msg, g)
        >>> dkls.verify(pk, sig, msg, g)
        True
        >>> # Verify fails with wrong message
        >>> dkls.verify(pk, sig, b"Wrong message", g)
        False
        """
        return self._sign.verify(public_key, signature, message, generator)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
