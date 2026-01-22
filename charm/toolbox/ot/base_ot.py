'''
Simplest Oblivious Transfer (Chou-Orlandi style) for Elliptic Curve Groups

| Based on: "The Simplest Protocol for Oblivious Transfer" - Chou & Orlandi
| Notes: 

* type:          oblivious transfer (1-out-of-2)
* setting:       Elliptic Curve DDH-hard group
* assumption:    DDH

:Authors: Elton de Souza
:Date:    01/2026
'''

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from hashlib import sha256

debug = False

class SimpleOT:
    """
    Simplest Oblivious Transfer based on Chou-Orlandi for EC groups.
    
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
    """
    
    def __init__(self, groupObj):
        """
        Initialize SimpleOT with an elliptic curve group.
        
        Parameters
        ----------
        groupObj : ECGroup
            An elliptic curve group object from charm.toolbox.ecgroup
        """
        global group
        group = groupObj
        self._a = None  # Sender's private key
        self._A = None  # Sender's public key
    
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
        point_bytes = group.serialize(point)
        return sha256(point_bytes).digest()
    
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
        self._a = group.random(ZR)
        g = group.random(G)
        self._A = g ** self._a
        self._g = g
        
        if debug:
            print("Sender setup:")
            print(f"  a (private) = {self._a}")
            print(f"  A (public) = {self._A}")
            print(f"  g = {g}")
        
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
            If choice_bit is not 0 or 1
        """
        if choice_bit not in (0, 1):
            raise ValueError("choice_bit must be 0 or 1")
        
        A = sender_params['A']
        g = sender_params['g']
        
        # Receiver picks random b
        b = group.random(ZR)
        
        # Compute B based on choice:
        # If choice=0: B = g^b (so B^a = g^(ab) = k0)
        # If choice=1: B = A * g^b (so (B/A)^a = g^(ab) = k1)
        if choice_bit == 0:
            B = g ** b
        else:
            B = A * (g ** b)
        
        if debug:
            print(f"Receiver choose (bit={choice_bit}):")
            print(f"  b (private) = {b}")
            print(f"  B = {B}")
        
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

        # Compute keys:
        # k0 = H(B^a) - receiver gets this if they chose 0
        # k1 = H((B/A)^a) = H(B^a / A^a) - receiver gets this if they chose 1
        k0_point = B ** self._a
        k1_point = (B * (self._A ** -1)) ** self._a

        k0 = self._derive_key(k0_point)
        k1 = self._derive_key(k1_point)

        if debug:
            print("Sender transfer:")
            print(f"  k0_point = {k0_point}")
            print(f"  k1_point = {k1_point}")

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

        if debug:
            print(f"Receiver retrieve (choice={choice_bit}):")
            print(f"  k_point = {k_point}")

        # Decrypt the chosen ciphertext
        cipher = AuthenticatedCryptoAbstraction(k)

        if choice_bit == 0:
            return cipher.decrypt(sender_ciphertexts['e0'])
        else:
            return cipher.decrypt(sender_ciphertexts['e1'])

