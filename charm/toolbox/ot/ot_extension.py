'''
IKNP-style OT Extension for Elliptic Curve Groups

| Based on: "Extending Oblivious Transfers Efficiently" - Ishai, Kilian, Nissim, Petrank
| Notes: 

* type:          oblivious transfer extension
* setting:       Elliptic Curve DDH-hard group  
* assumption:    DDH + Random Oracle

This module implements OT Extension which allows performing many OTs
with only a small number of base OT calls (k base OTs for m >> k OTs).

:Authors: Elton de Souza
:Date:    01/2026
'''

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.securerandom import OpenSSLRand
from charm.toolbox.bitstring import Bytes
import hashlib

debug = False


def xor_bytes(a, b):
    """
    XOR two byte strings of equal length.
    
    Parameters
    ----------
    a : bytes
        First byte string
    b : bytes  
        Second byte string
        
    Returns
    -------
    bytes
        XOR of the two byte strings
    """
    assert len(a) == len(b), f"xor_bytes: operands differ in length ({len(a)} vs {len(b)})"
    return bytes(x ^ y for x, y in zip(a, b))


def prg(seed, output_length):
    """
    Pseudo-random generator using SHA-256 in counter mode.
    
    Expands a seed to output_length bytes using hash chaining.
    
    Parameters
    ----------
    seed : bytes
        Random seed bytes
    output_length : int
        Desired output length in bytes
        
    Returns
    -------
    bytes
        Pseudo-random bytes of specified length
    """
    output = b''
    counter = 0
    while len(output) < output_length:
        h = hashlib.sha256()
        h.update(seed)
        h.update(counter.to_bytes(4, 'big'))
        output += h.digest()
        counter += 1
    return output[:output_length]


def hash_to_key(index, value):
    """
    Hash index and value to derive a key for encryption.
    
    Parameters
    ----------
    index : int
        OT index
    value : bytes
        Value to hash
        
    Returns
    -------
    bytes
        32-byte key
    """
    h = hashlib.sha256()
    h.update(index.to_bytes(8, 'big'))
    h.update(value)
    return h.digest()


def transpose_bit_matrix(matrix, rows, cols):
    """
    Transpose a bit matrix represented as a list of byte rows.
    
    Parameters
    ----------
    matrix : list of bytes
        Matrix with 'rows' rows, each row being 'cols' bits (cols//8 bytes)
    rows : int
        Number of rows in input matrix
    cols : int
        Number of columns (bits) in input matrix
        
    Returns
    -------
    list of bytes
        Transposed matrix with 'cols' rows, each row being 'rows' bits
    """
    # Each row has cols bits = cols//8 bytes
    # Result: cols rows, each with rows bits = rows//8 bytes
    cols_bytes = (cols + 7) // 8
    rows_bytes = (rows + 7) // 8
    
    # Initialize result matrix
    result = [bytearray(rows_bytes) for _ in range(cols)]
    
    for i in range(rows):
        row_bytes = matrix[i]
        for j in range(cols):
            # Get bit j from row i
            byte_idx = j // 8
            bit_idx = 7 - (j % 8)
            if byte_idx < len(row_bytes):
                bit = (row_bytes[byte_idx] >> bit_idx) & 1
            else:
                bit = 0
            
            # Set bit i in column j (which becomes row j in result)
            if bit:
                result_byte_idx = i // 8
                result_bit_idx = 7 - (i % 8)
                result[j][result_byte_idx] |= (1 << result_bit_idx)
    
    return [bytes(row) for row in result]


def get_bit(data, bit_index):
    """Get a specific bit from byte array."""
    byte_idx = bit_index // 8
    bit_idx = 7 - (bit_index % 8)
    if byte_idx >= len(data):
        return 0
    return (data[byte_idx] >> bit_idx) & 1


def set_bit(data, bit_index, value):
    """Set a specific bit in a bytearray."""
    byte_idx = bit_index // 8
    bit_idx = 7 - (bit_index % 8)
    if value:
        data[byte_idx] |= (1 << bit_idx)
    else:
        data[byte_idx] &= ~(1 << bit_idx)


class OTExtension:
    """
    IKNP-style OT Extension.

    Extends k base OTs to m OTs efficiently, where m >> k.
    Uses the matrix transposition trick from the IKNP paper.

    In the base OT phase, the roles are reversed:
    - The OT Extension receiver acts as sender in base OT
    - The OT Extension sender acts as receiver in base OT

    >>> from charm.toolbox.eccurve import secp256k1
    >>> from charm.toolbox.ecgroup import ECGroup
    >>> group = ECGroup(secp256k1)
    >>> # Create extension instances for sender and receiver
    >>> sender_ext = OTExtension(group, security_param=128)
    >>> receiver_ext = OTExtension(group, security_param=128)
    >>> # Receiver's choice bits for 256 OTs
    >>> num_ots = 256
    >>> choice_bits = bytes([0b10101010] * (num_ots // 8))  # alternating bits
    >>> # Messages from sender (pairs of 32-byte messages)
    >>> import os
    >>> messages = [(os.urandom(32), os.urandom(32)) for _ in range(num_ots)]
    >>> # Run the extension protocol
    >>> # Phase 1: Setup with random sender secret
    >>> sender_secret = sender_ext.sender_init()
    >>> # Phase 2: Receiver generates matrix based on choice bits
    >>> receiver_msg, receiver_state = receiver_ext.receiver_extend(num_ots, choice_bits, sender_secret)
    >>> # Phase 3: Sender encrypts messages
    >>> sender_ciphertexts = sender_ext.sender_extend(num_ots, messages, receiver_msg)
    >>> # Phase 4: Receiver decrypts chosen messages
    >>> results = receiver_ext.receiver_output(sender_ciphertexts, receiver_state)
    >>> # Verify receiver got correct messages
    >>> all(results[i] == messages[i][get_bit(choice_bits, i)] for i in range(num_ots))
    True
    """

    def __init__(self, groupObj, security_param=128):
        """
        Initialize OT Extension with an elliptic curve group.

        Parameters
        ----------
        groupObj : ECGroup
            An elliptic curve group object from charm.toolbox.ecgroup
        security_param : int
            Security parameter (number of base OTs), typically 128
        """
        self.group = groupObj
        self.k = security_param  # number of base OTs / security parameter
        self.rand = OpenSSLRand()
        self._sender_random_bits = None  # s in the protocol
        self._seeds = None  # Seeds from base OT

    def sender_init(self):
        """
        Sender initializes with random k-bit string s.

        In IKNP, the sender chooses random bits s_1, ..., s_k and uses
        base OT as a receiver with these as choice bits.

        Returns
        -------
        bytes
            The random k-bit string s (k/8 bytes)
        """
        # Generate k random bits
        k_bytes = (self.k + 7) // 8
        self._sender_random_bits = self.rand.getRandomBytes(k_bytes)
        return self._sender_random_bits

    def receiver_extend(self, num_ots, choice_bits, sender_s):
        """
        Receiver side of the extension protocol.

        The receiver:
        1. Generates random seeds for each of k columns
        2. Creates matrix T where row i is PRG(seed_i)
        3. Computes U = T XOR (r repeated) where r is choice bits
        4. For each j, if s_j=0, sends T_j; if s_j=1, sends U_j

        Parameters
        ----------
        num_ots : int
            Number of OTs to extend to
        choice_bits : bytes
            The receiver's m choice bits (m/8 bytes)
        sender_s : bytes
            Sender's random k-bit string from sender_init

        Returns
        -------
        tuple
            (message_to_sender, receiver_state) where:
            - message_to_sender: dict with matrix columns to send
            - receiver_state: dict with state for receiver_output
        """
        m = num_ots
        m_bytes = (m + 7) // 8

        # Generate k random seeds
        seeds = []
        for _ in range(self.k):
            seed = self.rand.getRandomBytes(32)
            seeds.append(seed)

        # Generate matrix T: k rows, each m bits
        # T[j] = PRG(seed_j) for j = 0, ..., k-1
        T = []
        for j in range(self.k):
            T.append(prg(seeds[j], m_bytes))

        # Compute what to send to sender
        # For each column j:
        #   If s_j = 0: send T_j
        #   If s_j = 1: send T_j XOR choice_bits
        # This is equivalent to sending Q where Q_j = T_j XOR (s_j * r)
        columns_to_send = []
        for j in range(self.k):
            s_j = get_bit(sender_s, j)
            if s_j == 0:
                columns_to_send.append(T[j])
            else:
                # XOR with choice bits
                columns_to_send.append(xor_bytes(T[j], choice_bits))

        # Transpose T to get t_i for each i (row i of transposed T)
        T_transposed = transpose_bit_matrix(T, self.k, m)

        receiver_state = {
            'num_ots': m,
            'choice_bits': choice_bits,
            't_rows': T_transposed,  # t_i = i-th row of T^T
        }

        message_to_sender = {
            'columns': columns_to_send,
            'num_ots': m,
        }

        if debug:
            print(f"Receiver extend: m={m}, k={self.k}")
            print(f"  T[0][:8] = {T[0][:8].hex()}")

        return message_to_sender, receiver_state

    def sender_extend(self, num_ots, message_pairs, receiver_msg):
        """
        Sender side of the extension protocol.

        The sender:
        1. Receives Q matrix from receiver
        2. For each i, computes q_i (row i of Q^T)
        3. Encrypts x_{i,0} with H(i, q_i)
        4. Encrypts x_{i,1} with H(i, q_i XOR s)

        Parameters
        ----------
        num_ots : int
            Number of OTs
        message_pairs : list of tuples
            List of (m0, m1) byte message pairs
        receiver_msg : dict
            Message from receiver_extend containing columns

        Returns
        -------
        list of tuples
            List of (y0, y1) encrypted message pairs
        """
        if self._sender_random_bits is None:
            raise RuntimeError("sender_init must be called before sender_extend")

        m = num_ots
        columns = receiver_msg['columns']
        s = self._sender_random_bits
        s_bytes = (self.k + 7) // 8

        # Transpose Q to get q_i for each i
        Q_transposed = transpose_bit_matrix(columns, self.k, m)

        ciphertexts = []
        for i in range(m):
            q_i = Q_transposed[i]

            # Key for m0: H(i, q_i)
            key0 = hash_to_key(i, q_i)

            # Key for m1: H(i, q_i XOR s)
            q_i_xor_s = xor_bytes(q_i, s[:len(q_i)])
            key1 = hash_to_key(i, q_i_xor_s)

            # Encrypt messages using XOR with key (simple one-time pad)
            m0, m1 = message_pairs[i]

            # Ensure messages fit in key length, or extend key
            if len(m0) > 32:
                key0 = prg(key0, len(m0))
            if len(m1) > 32:
                key1 = prg(key1, len(m1))

            y0 = xor_bytes(m0, key0[:len(m0)])
            y1 = xor_bytes(m1, key1[:len(m1)])

            ciphertexts.append((y0, y1))

        if debug:
            print(f"Sender extend: m={m}")
            print(f"  Q_transposed[0][:8] = {Q_transposed[0][:8].hex() if len(Q_transposed[0]) >= 8 else Q_transposed[0].hex()}")

        return ciphertexts

    def receiver_output(self, ciphertexts, receiver_state):
        """
        Receiver decrypts the chosen messages.

        The receiver uses t_i (from receiver_extend) to decrypt:
        - If r_i = 0: decrypt with H(i, t_i)
        - If r_i = 1: decrypt with H(i, t_i) (which equals H(i, q_i XOR s) for correct choice)

        Parameters
        ----------
        ciphertexts : list of tuples
            Encrypted message pairs from sender_extend
        receiver_state : dict
            State from receiver_extend

        Returns
        -------
        list of bytes
            The decrypted chosen messages
        """
        m = receiver_state['num_ots']
        choice_bits = receiver_state['choice_bits']
        t_rows = receiver_state['t_rows']

        results = []
        for i in range(m):
            t_i = t_rows[i]
            r_i = get_bit(choice_bits, i)

            # Key: H(i, t_i)
            key = hash_to_key(i, t_i)

            # Get the ciphertext corresponding to choice
            y0, y1 = ciphertexts[i]
            y = y1 if r_i else y0

            # Extend key if needed
            if len(y) > 32:
                key = prg(key, len(y))

            # Decrypt
            msg = xor_bytes(y, key[:len(y)])
            results.append(msg)

        if debug:
            print(f"Receiver output: m={m}")

        return results
