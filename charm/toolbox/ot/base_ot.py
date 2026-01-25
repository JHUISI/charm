'''
Simplest Oblivious Transfer (Chou-Orlandi style) for Elliptic Curve Groups

| From: "The Simplest Protocol for Oblivious Transfer"
| By:   Tung Chou and Claudio Orlandi
| Published: LATINCRYPT 2015
| URL:  https://eprint.iacr.org/2015/267

* type:          oblivious transfer (1-out-of-2)
* setting:       Elliptic Curve DDH-hard group
* assumption:    DDH

:Authors: Elton de Souza
:Date:    01/2026
'''

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from hashlib import sha256
import logging

# Module logger
logger = logging.getLogger(__name__)


class SimpleOT:
    """
    Simplest Oblivious Transfer based on Chou-Orlandi for EC groups.

    This implementation is thread-safe - each instance maintains its own
    group reference and state.

    Implements 1-out-of-2 OT where:
    - Sender has two messages (m0, m1)
    - Receiver has a choice bit b
    - Receiver learns m_b without learning m_{1-b}
    - Sender learns nothing about b

    >>> from charm.toolbox.eccurve import secp256k1
    >>> from charm.toolbox.ecgroup import ECGroup
    >>> group = ECGroup(secp256k1)
    >>> sender = SimpleOT(group)
    >>> receiver = SimpleOT(group)
    >>> # Sender setup: generates public parameters
    >>> sender_params = sender.sender_setup()
    >>> # Receiver chooses bit 0
    >>> receiver_response, receiver_state = receiver.receiver_choose(sender_params, 0)
    >>> # Sender transfers encrypted messages
    >>> m0, m1 = b'message zero!!!!', b'message one!!!!!'
    >>> ciphertexts = sender.sender_transfer(receiver_response, m0, m1)
    >>> # Receiver retrieves chosen message
    >>> result = receiver.receiver_retrieve(ciphertexts, receiver_state)
    >>> result == m0
    True
    >>> # Test with choice bit 1
    >>> sender2 = SimpleOT(group)
    >>> receiver2 = SimpleOT(group)
    >>> sender_params2 = sender2.sender_setup()
    >>> receiver_response2, receiver_state2 = receiver2.receiver_choose(sender_params2, 1)
    >>> ciphertexts2 = sender2.sender_transfer(receiver_response2, m0, m1)
    >>> result2 = receiver2.receiver_retrieve(ciphertexts2, receiver_state2)
    >>> result2 == m1
    True

    Security Note
    -------------
    - Each SimpleOT instance should be used for a SINGLE OT operation.
    - Reusing instances with the same keys is NOT recommended for security.
    - The instance generates fresh randomness per transfer but shares the
      sender's key across transfers if sender_setup is not called again.
    - For multiple OT operations, create new SimpleOT instances or use
      OT extension (see OTExtension class).
    - To regenerate keys on an existing instance, call reset_sender() before
      sender_setup(), or simply call sender_setup() again which generates
      fresh keys.

    Security Limitations
    --------------------
    WARNING: This implementation is NOT constant-time and is vulnerable to
    timing attacks. The following operations leak timing information:

    - Modular inversion: Variable-time modular inverse operations
    - Bit extraction: Conditional logic based on secret choice bit values
    - Conditional branching: Control flow depends on secret data

    This implementation is suitable for research and educational purposes only.
    Do NOT use in production environments where side-channel attacks are a concern.
    Production deployments should use constant-time cryptographic implementations
    with proper side-channel mitigations.

    Encryption Note
    ---------------
    This implementation uses AuthenticatedCryptoAbstraction for symmetric
    encryption of OT messages. The current implementation provides AEAD
    (Authenticated Encryption with Associated Data) using AES-CBC with
    HMAC-SHA256 in an Encrypt-then-MAC construction. While this provides
    authentication, it is not as robust as AES-GCM. For production use,
    consider verifying the underlying implementation uses authenticated
    encryption (e.g., AES-GCM) to prevent ciphertext malleability attacks.
    """

    def __init__(self, groupObj):
        """
        Initialize SimpleOT with an elliptic curve group.

        Parameters
        ----------
        groupObj : ECGroup
            An elliptic curve group object from charm.toolbox.ecgroup
        """
        if groupObj is None:
            raise ValueError("groupObj cannot be None")
        self.group = groupObj
        self._a = None  # Sender's private key
        self._A = None  # Sender's public key
        self._g = None  # Generator point

    def _derive_key(self, point):
        """
        Derive a symmetric key from an EC point using SHA-256.

        Parameters
        ----------
        point : ec_element
            An elliptic curve point

        Returns
        -------
        bytes
            32-byte key suitable for symmetric encryption
        """
        point_bytes = self.group.serialize(point)
        return sha256(point_bytes).digest()

    def _validate_point(self, point, name="point"):
        """
        Validate that a point is a valid non-identity element on the curve.

        Parameters
        ----------
        point : ec_element
            An elliptic curve point to validate
        name : str
            Name of the point for error messages

        Raises
        ------
        ValueError
            If the point is invalid, at infinity (identity), or not on the curve

        Note on Subgroup Validation
        ---------------------------
        For curves with cofactor > 1 (e.g., Curve25519 with cofactor 8), an
        additional subgroup membership test is required to prevent small subgroup
        attacks. This check verifies that ``point ** order == identity``.

        However, secp256k1 (the default curve) has **cofactor 1** (prime order
        group), meaning all non-identity points on the curve are already in the
        prime-order subgroup. Therefore, subgroup validation is unnecessary for
        secp256k1 and is not performed here.

        If this implementation is extended to support curves with cofactor > 1,
        add the following check after the on-curve validation::

            # Subgroup membership test (required for curves with cofactor > 1):
            # order = self.group.order()
            # if not (point ** order).isInf():
            #     raise ValueError(f"Invalid {name}: point not in prime-order subgroup")
        """
        # Check for identity element (point at infinity)
        if point.isInf():
            raise ValueError(f"Invalid {name}: point is at infinity (identity element)")

        # Validate point is on curve by serialize/deserialize round-trip
        # The deserialize function validates the point is on the curve
        try:
            serialized = self.group.serialize(point)
            deserialized = self.group.deserialize(serialized)
            if deserialized is None or deserialized is False:
                raise ValueError(f"Invalid {name}: point is not on the curve")
        except Exception as e:
            raise ValueError(f"Invalid {name}: failed to validate point - {e}")

        # Note: Subgroup membership test is NOT performed here because secp256k1
        # has cofactor 1. For curves with cofactor > 1, uncomment the check above.

    def reset_sender(self):
        """
        Reset the sender's state, clearing all keys.

        Call this method before sender_setup() to ensure fresh keys are
        generated. This is useful when reusing a SimpleOT instance for
        multiple OT operations (though creating new instances is preferred).

        Note: sender_setup() also generates fresh keys, so calling
        reset_sender() is optional but makes the intent explicit.
        """
        self._a = None
        self._A = None
        self._g = None
        logger.debug("Sender state reset - keys cleared")

    def sender_setup(self):
        """
        Sender generates public parameters for the OT protocol.

        Returns
        -------
        dict
            Dictionary containing:
            - 'A': sender's public key (g^a)
            - 'g': generator point
        """
        self._a = self.group.random(ZR)
        g = self.group.random(G)
        self._A = g ** self._a
        self._g = g

        logger.debug("Sender setup: a=%s, A=%s, g=%s", self._a, self._A, g)

        return {'A': self._A, 'g': g}

    def receiver_choose(self, sender_params, choice_bit):
        """
        Receiver generates response based on choice bit.

        Parameters
        ----------
        sender_params : dict
            Public parameters from sender_setup containing 'A' and 'g'
        choice_bit : int
            The receiver's choice (0 or 1)

        Returns
        -------
        tuple
            (receiver_response, receiver_state) where:
            - receiver_response: dict with 'B' to send to sender
            - receiver_state: dict with private state for receiver_retrieve

        Raises
        ------
        ValueError
            If choice_bit is not 0 or 1, or if sender's points are invalid
        """
        if choice_bit not in (0, 1):
            raise ValueError("choice_bit must be 0 or 1")

        A = sender_params['A']
        g = sender_params['g']

        # Validate sender's points are valid curve points (not identity or off-curve)
        # This prevents attacks using invalid or small-subgroup points
        self._validate_point(g, "generator g")
        self._validate_point(A, "sender public key A")

        # Receiver picks random b
        b = self.group.random(ZR)
        
        # Compute B based on choice:
        # If choice=0: B = g^b (so B^a = g^(ab) = k0)
        # If choice=1: B = A * g^b (so (B/A)^a = g^(ab) = k1)
        if choice_bit == 0:
            B = g ** b
        else:
            B = A * (g ** b)

        logger.debug("Receiver choose (bit=%d): b=%s, B=%s", choice_bit, b, B)
        
        # The key the receiver will compute: k_choice = A^b
        receiver_state = {
            'b': b,
            'A': A,
            'choice_bit': choice_bit
        }

        return {'B': B}, receiver_state

    def sender_transfer(self, receiver_response, m0, m1):
        """
        Sender encrypts both messages using derived keys.

        Parameters
        ----------
        receiver_response : dict
            Response from receiver_choose containing 'B'
        m0 : bytes
            First message (sent if receiver chose 0)
        m1 : bytes
            Second message (sent if receiver chose 1)

        Returns
        -------
        dict
            Dictionary containing:
            - 'e0': encrypted m0
            - 'e1': encrypted m1

        Raises
        ------
        RuntimeError
            If sender_setup was not called first
        """
        if self._a is None or self._A is None:
            raise RuntimeError("sender_setup must be called before sender_transfer")

        B = receiver_response['B']

        # Validate receiver's point B is a valid curve point (not identity or off-curve)
        # This prevents attacks using invalid or small-subgroup points
        self._validate_point(B, "receiver public key B")

        # Compute keys:
        # k0 = H(B^a) - receiver gets this if they chose 0
        # k1 = H((B/A)^a) = H(B^a / A^a) - receiver gets this if they chose 1
        k0_point = B ** self._a
        k1_point = (B * (self._A ** -1)) ** self._a

        k0 = self._derive_key(k0_point)
        k1 = self._derive_key(k1_point)

        logger.debug("Sender transfer: k0_point=%s, k1_point=%s", k0_point, k1_point)

        # Encrypt messages
        cipher0 = AuthenticatedCryptoAbstraction(k0)
        cipher1 = AuthenticatedCryptoAbstraction(k1)

        e0 = cipher0.encrypt(m0)
        e1 = cipher1.encrypt(m1)

        return {'e0': e0, 'e1': e1}

    def receiver_retrieve(self, sender_ciphertexts, receiver_state):
        """
        Receiver decrypts the chosen message.

        Parameters
        ----------
        sender_ciphertexts : dict
            Ciphertexts from sender_transfer containing 'e0' and 'e1'
        receiver_state : dict
            Private state from receiver_choose

        Returns
        -------
        bytes
            The decrypted chosen message

        Raises
        ------
        ValueError
            If decryption fails (should not happen in honest execution)
        """
        b = receiver_state['b']
        A = receiver_state['A']
        choice_bit = receiver_state['choice_bit']

        # Compute the key: k_choice = A^b
        # This equals:
        # - k0 = (g^a)^b = g^(ab) if choice=0 (since B = g^b, B^a = g^(ab))
        # - k1 = (g^a)^b = g^(ab) if choice=1 (since B = A*g^b, (B/A)^a = g^(ab))
        k_point = A ** b
        k = self._derive_key(k_point)

        logger.debug("Receiver retrieve (choice=%d): k_point=%s", choice_bit, k_point)

        # Decrypt the chosen ciphertext
        cipher = AuthenticatedCryptoAbstraction(k)

        if choice_bit == 0:
            return cipher.decrypt(sender_ciphertexts['e0'])
        else:
            return cipher.decrypt(sender_ciphertexts['e1'])

