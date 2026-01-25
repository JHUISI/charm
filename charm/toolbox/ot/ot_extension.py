'''
IKNP-style OT Extension for Elliptic Curve Groups

| From: "Extending Oblivious Transfers Efficiently"
| By:   Yuval Ishai, Joe Kilian, Kobbi Nissim, Erez Petrank
| Published: CRYPTO 2003
| URL:  https://www.iacr.org/archive/crypto2003/27290145/27290145.pdf

* type:          oblivious transfer extension
* setting:       Symmetric primitives (hash, PRG, XOR)
* assumption:    Random Oracle (SHA-256)

This module implements OT Extension which allows performing many OTs
with only a small number of base OT calls (k base OTs for m >> k OTs).

:Authors: Elton de Souza
:Date:    01/2026
'''

from charm.toolbox.securerandom import OpenSSLRand
from charm.toolbox.bitstring import Bytes
from charm.toolbox.ot.base_ot import SimpleOT
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
import hashlib
import logging

# Module logger
logger = logging.getLogger(__name__)


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
        h.update(b"PRG:")  # Domain separator
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
    h.update(b"KEY:")  # Domain separator
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

    The protocol flow is:

    1. Base OT Setup (receiver acts as sender, sender acts as receiver):
       - receiver_ext.receiver_setup_base_ots() -> base_ot_setups
       - sender_ext.sender_setup_base_ots()
       - sender_ext.sender_respond_base_ots(base_ot_setups) -> responses
       - receiver_ext.receiver_transfer_seeds(responses) -> ciphertexts
       - sender_ext.sender_receive_seeds(ciphertexts)

    2. Extension Phase:
       - sender_ext.sender_init()
       - receiver_ext.receiver_extend(num_ots, choice_bits) -> msg, state
       - sender_ext.sender_extend(num_ots, messages, msg) -> ciphertexts
       - receiver_ext.receiver_output(ciphertexts, state) -> results
    """

    def __init__(self, groupObj, security_param=128, base_ot=None):
        """
        Initialize OT Extension with an elliptic curve group.

        Parameters
        ----------
        groupObj : ECGroup
            An elliptic curve group object from charm.toolbox.ecgroup
        security_param : int
            Security parameter (number of base OTs), typically 128
        base_ot : SimpleOT or compatible, optional
            Base OT protocol instance. If None, a SimpleOT instance is created.
        """
        self.group = groupObj
        self.k = security_param  # number of base OTs / security parameter
        self.rand = OpenSSLRand()
        self._sender_random_bits = None  # s in the protocol
        self._sender_seeds = None  # Seeds received from base OT (one per column)
        self._receiver_seed_pairs = None  # Seed pairs for receiver (both per column)
        self._base_ot_complete = False
        self._base_ot_states = None  # Sender's base OT receiver states
        self._base_ot_instances = None  # Receiver's base OT sender instances
        self._sender_ot_instances = None  # Sender's base OT receiver instances

        # Initialize base OT protocol
        if base_ot is None:
            self.base_ot = SimpleOT(groupObj)
        else:
            self.base_ot = base_ot

    def sender_setup_base_ots(self):
        """
        Sender-side base OT setup (acts as receiver in base OT).

        Generates random k-bit string s and prepares for k base OTs
        where sender will receive seed_j^{s_j} for each j.

        Returns
        -------
        dict
            Confirmation that sender is ready for base OT
        """
        # Generate k random bits for s
        k_bytes = (self.k + 7) // 8
        self._sender_random_bits = self.rand.getRandomBytes(k_bytes)

        # Prepare to receive k base OTs
        self._sender_seeds = [None] * self.k
        self._base_ot_states = [None] * self.k

        return {'ready': True, 'k': self.k}

    def receiver_setup_base_ots(self):
        """
        Receiver-side base OT setup (acts as sender in base OT).

        Generates k pairs of random seeds that will be transferred via base OT.

        Returns
        -------
        list of dict
            List of k base OT setup messages to send to OT-ext sender
        """
        # Generate k pairs of random seeds
        self._receiver_seed_pairs = []
        base_ot_setups = []

        for j in range(self.k):
            seed0 = self.rand.getRandomBytes(32)
            seed1 = self.rand.getRandomBytes(32)
            self._receiver_seed_pairs.append((seed0, seed1))

            # Create a fresh base OT instance for this transfer
            ot_instance = SimpleOT(self.group)
            sender_params = ot_instance.sender_setup()
            base_ot_setups.append({
                'j': j,
                'params': sender_params,
                'ot_instance': ot_instance
            })

        self._base_ot_instances = [setup['ot_instance'] for setup in base_ot_setups]
        return [{'j': s['j'], 'params': s['params']} for s in base_ot_setups]

    def sender_respond_base_ots(self, base_ot_setups):
        """
        Sender responds to receiver's base OT setup (acts as receiver, choosing based on s).

        Parameters
        ----------
        base_ot_setups : list of dict
            Base OT parameters from receiver_setup_base_ots()

        Returns
        -------
        list of dict
            Receiver responses for each base OT
        """
        responses = []
        self._sender_ot_instances = []

        for setup in base_ot_setups:
            j = setup['j']
            params = setup['params']
            s_j = get_bit(self._sender_random_bits, j)

            # Act as receiver in base OT with choice bit s_j
            ot_instance = SimpleOT(self.group)
            response, state = ot_instance.receiver_choose(params, s_j)

            self._sender_ot_instances.append(ot_instance)
            self._base_ot_states[j] = state
            responses.append({'j': j, 'response': response})

        return responses

    def receiver_transfer_seeds(self, sender_responses):
        """
        Receiver completes base OT by transferring seeds.

        Parameters
        ----------
        sender_responses : list of dict
            Responses from sender_respond_base_ots()

        Returns
        -------
        list of dict
            Encrypted seed ciphertexts for each base OT
        """
        ciphertexts = []

        for resp in sender_responses:
            j = resp['j']
            response = resp['response']
            seed0, seed1 = self._receiver_seed_pairs[j]

            # Transfer both seeds via base OT
            # Convert Bytes objects to native bytes for symcrypto compatibility
            ot_instance = self._base_ot_instances[j]
            cts = ot_instance.sender_transfer(response, bytes(seed0), bytes(seed1))
            ciphertexts.append({'j': j, 'ciphertexts': cts})

        self._base_ot_complete = True
        return ciphertexts

    def sender_receive_seeds(self, seed_ciphertexts):
        """
        Sender receives seeds from base OT.

        Parameters
        ----------
        seed_ciphertexts : list of dict
            Encrypted seeds from receiver_transfer_seeds()
        """
        for ct in seed_ciphertexts:
            j = ct['j']
            ciphertexts = ct['ciphertexts']
            state = self._base_ot_states[j]

            # Retrieve the seed corresponding to s_j
            ot_instance = self._sender_ot_instances[j]
            seed = ot_instance.receiver_retrieve(ciphertexts, state)
            self._sender_seeds[j] = seed

        self._base_ot_complete = True

    def sender_init(self):
        """
        Initialize sender for extension phase.

        Must be called AFTER base OT setup is complete.

        Returns
        -------
        dict
            Confirmation that sender is ready (no secrets exposed)

        Raises
        ------
        RuntimeError
            If base OT setup has not been completed
        """
        if not self._base_ot_complete:
            raise RuntimeError("Base OT setup must be completed before sender_init")
        if self._sender_seeds is None or None in self._sender_seeds:
            raise RuntimeError("Sender seeds not properly received from base OT")

        return {'ready': True, 'k': self.k}

    def receiver_extend(self, num_ots, choice_bits):
        """
        Receiver side of the extension protocol.

        Uses seeds from base OT setup instead of receiving s directly.

        Parameters
        ----------
        num_ots : int
            Number of OTs to extend to
        choice_bits : bytes
            The receiver's m choice bits (m/8 bytes)

        Returns
        -------
        tuple
            (message_to_sender, receiver_state)

        Raises
        ------
        RuntimeError
            If base OT setup has not been completed
        """
        if not self._base_ot_complete:
            raise RuntimeError("Base OT setup must be completed before receiver_extend")

        m = num_ots
        m_bytes = (m + 7) // 8

        # Build T matrices from both seed pairs
        T0 = []  # T^0: columns from seed_j^0
        T1 = []  # T^1: columns from seed_j^1

        for j in range(self.k):
            seed0, seed1 = self._receiver_seed_pairs[j]
            T0.append(prg(seed0, m_bytes))
            T1.append(prg(seed1, m_bytes))

        # Compute U_j = T_j^0 ⊕ T_j^1 ⊕ choice_bits
        # This ensures: Q_j = T_j^{s_j} when sender computes Q_j = recv_j ⊕ (s_j · U_j)
        U = []
        for j in range(self.k):
            u_j = xor_bytes(xor_bytes(T0[j], T1[j]), choice_bits)
            U.append(u_j)

        # For receiver's keys: t_i is ALWAYS row i of T^0 transposed
        # This is because:
        # - Sender computes Q_j = T_j^0 ⊕ (s_j · r), so q_i = t_i^0 ⊕ (r_i · s)
        # - If r_i = 0: key0 = H(i, q_i) = H(i, t_i^0), key1 = H(i, t_i^0 ⊕ s)
        #   Receiver wants m0, can compute H(i, t_i^0) ✓
        # - If r_i = 1: key0 = H(i, t_i^0 ⊕ s), key1 = H(i, t_i^0)
        #   Receiver wants m1, can compute H(i, t_i^0) ✓
        T0_transposed = transpose_bit_matrix(T0, self.k, m)
        t_rows = T0_transposed  # Always use T^0

        receiver_state = {
            'num_ots': m,
            'choice_bits': choice_bits,
            't_rows': t_rows,
        }

        message_to_sender = {
            'U': U,  # Send U matrix instead of Q
            'num_ots': m,
        }

        logger.debug("Receiver extend: m=%d, k=%d", m, self.k)

        return message_to_sender, receiver_state

    def sender_extend(self, num_ots, message_pairs, receiver_msg):
        """
        Sender side of the extension protocol.

        The sender:
        1. Receives U matrix from receiver
        2. Computes T from seeds: T_j = PRG(seed_j^{s_j})
        3. Computes Q_j = T_j ⊕ (s_j · U_j)
        4. For each i, computes q_i (row i of Q^T)
        5. Encrypts x_{i,0} with H(i, q_i)
        6. Encrypts x_{i,1} with H(i, q_i XOR s)

        Parameters
        ----------
        num_ots : int
            Number of OTs
        message_pairs : list of tuples
            List of (m0, m1) byte message pairs
        receiver_msg : dict
            Message from receiver_extend containing U matrix

        Returns
        -------
        list of tuples
            List of (y0, y1) encrypted message pairs

        Raises
        ------
        RuntimeError
            If base OT or sender_init was not completed
        """
        if not self._base_ot_complete:
            raise RuntimeError("Base OT setup must be completed before sender_extend")
        if self._sender_random_bits is None:
            raise RuntimeError("sender_init must be called before sender_extend")

        m = num_ots
        m_bytes = (m + 7) // 8
        U = receiver_msg['U']
        s = self._sender_random_bits

        # Build T from received seeds: T_j = PRG(seed_j^{s_j})
        T = []
        for j in range(self.k):
            T.append(prg(self._sender_seeds[j], m_bytes))

        # Compute Q_j = T_j ⊕ (s_j · U_j)
        Q = []
        for j in range(self.k):
            s_j = get_bit(s, j)
            if s_j == 0:
                Q.append(T[j])
            else:
                Q.append(xor_bytes(T[j], U[j]))

        # Transpose Q to get q_i for each i
        Q_transposed = transpose_bit_matrix(Q, self.k, m)

        ciphertexts = []
        for i in range(m):
            q_i = Q_transposed[i]

            # Key for m0: H(i, q_i)
            key0 = hash_to_key(i, q_i)

            # Key for m1: H(i, q_i XOR s)
            q_i_xor_s = xor_bytes(q_i, s[:len(q_i)])
            key1 = hash_to_key(i, q_i_xor_s)

            # Encrypt messages using authenticated encryption (AEAD)
            m0, m1 = message_pairs[i]

            # Use first 16 bytes of key for AES (AuthenticatedCryptoAbstraction requirement)
            cipher0 = AuthenticatedCryptoAbstraction(key0)
            cipher1 = AuthenticatedCryptoAbstraction(key1)

            y0 = cipher0.encrypt(m0)
            y1 = cipher1.encrypt(m1)

            ciphertexts.append((y0, y1))

        if Q_transposed:
            q0_hex = Q_transposed[0][:8].hex() if len(Q_transposed[0]) >= 8 else Q_transposed[0].hex()
            logger.debug("Sender extend: m=%d, Q_transposed[0][:8]=%s", m, q0_hex)

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

            # Decrypt with authentication
            cipher = AuthenticatedCryptoAbstraction(key)
            try:
                msg = cipher.decrypt(y)
            except ValueError as e:
                raise ValueError(f"Authentication failed for OT index {i}: ciphertext may have been tampered") from e
            results.append(msg)

        logger.debug("Receiver output: m=%d", m)

        return results
