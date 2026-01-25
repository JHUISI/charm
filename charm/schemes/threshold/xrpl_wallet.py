"""
XRPL Threshold Wallet Integration

This module provides XRPL (XRP Ledger) wallet functionality using the DKLS23
threshold ECDSA implementation. It enables creating threshold-controlled XRPL
wallets where t-of-n parties must cooperate to sign transactions.

XRPL Compatibility:
- Uses secp256k1 curve (same as XRPL)
- 33-byte compressed public key format
- DER-encoded signatures
- Standard XRPL address derivation (SHA-256 → RIPEMD-160 → base58)

Example
-------
>>> from charm.toolbox.eccurve import secp256k1
>>> from charm.toolbox.ecgroup import ECGroup
>>> from charm.schemes.threshold.dkls23_sign import DKLS23
>>> from charm.schemes.threshold.xrpl_wallet import XRPLThresholdWallet
>>>
>>> # Create 2-of-3 threshold ECDSA
>>> group = ECGroup(secp256k1)
>>> dkls = DKLS23(group, threshold=2, num_parties=3)
>>> g = group.random(G)
>>>
>>> # Generate distributed keys
>>> key_shares, public_key = dkls.distributed_keygen(g)
>>>
>>> # Create XRPL wallet from threshold public key
>>> wallet = XRPLThresholdWallet(group, public_key)
>>> address = wallet.get_classic_address()
>>> print(f"XRPL Address: {address}")  # doctest: +SKIP

References
----------
- XRPL Cryptographic Keys: https://xrpl.org/docs/concepts/accounts/cryptographic-keys
- XRPL Address Encoding: https://xrpl.org/docs/concepts/accounts/addresses
- DKLS23: "Two-Round Threshold ECDSA from ECDSA Assumptions"

Note
----
This module provides cryptographic primitives only. For full XRPL integration,
you will need the xrpl-py library for transaction serialization and network
communication. See XRPL_GAPS.md for details on missing functionality.
"""

import hashlib
import base64
from typing import Optional, Tuple

from charm.core.math.elliptic_curve import getGenerator


def get_secp256k1_generator(group):
    """
    Get the standard secp256k1 generator point.

    This returns the fixed generator point specified in the secp256k1 standard,
    NOT a random point. This is required for ECDSA signatures that need to be
    verified by external systems like XRPL.

    Args:
        group: ECGroup instance initialized with secp256k1

    Returns:
        The standard secp256k1 generator point G

    Example:
        >>> from charm.toolbox.eccurve import secp256k1
        >>> from charm.toolbox.ecgroup import ECGroup
        >>> group = ECGroup(secp256k1)
        >>> g = get_secp256k1_generator(group)
        >>> # g is now the standard generator, not a random point
    """
    return getGenerator(group.ec_group)

from charm.toolbox.ecgroup import ECGroup
from charm.core.math.elliptic_curve import ec_element, serialize, ZR, G

# XRPL base58 alphabet (different from Bitcoin's base58)
XRPL_ALPHABET = b'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'


def _base58_encode(data: bytes) -> str:
    """Encode bytes to XRPL base58 format."""
    # Convert bytes to integer
    n = int.from_bytes(data, 'big')

    # Convert to base58
    result = []
    while n > 0:
        n, remainder = divmod(n, 58)
        result.append(XRPL_ALPHABET[remainder:remainder+1])

    # Add leading zeros
    for byte in data:
        if byte == 0:
            result.append(XRPL_ALPHABET[0:1])
        else:
            break

    return b''.join(reversed(result)).decode('ascii')


def _sha256(data: bytes) -> bytes:
    """Compute SHA-256 hash."""
    return hashlib.sha256(data).digest()


def _ripemd160(data: bytes) -> bytes:
    """Compute RIPEMD-160 hash."""
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()


def _double_sha256(data: bytes) -> bytes:
    """Compute double SHA-256 hash (for checksum)."""
    return _sha256(_sha256(data))


def get_compressed_public_key(group: ECGroup, public_key: ec_element) -> bytes:
    """
    Get 33-byte compressed public key from EC point.

    XRPL requires compressed secp256k1 public keys (33 bytes):
    - 0x02 prefix if Y coordinate is even
    - 0x03 prefix if Y coordinate is odd
    - Followed by 32-byte X coordinate

    Args:
        group: The EC group (should be secp256k1)
        public_key: The EC point representing the public key

    Returns:
        33-byte compressed public key
    """
    # Charm's serialize uses compressed format, but wraps in base64 with type prefix
    # Format is "type:base64_data" where type=1 for G (group element)
    serialized = serialize(public_key)

    # Parse the Charm format: "1:base64data"
    if isinstance(serialized, bytes):
        serialized = serialized.decode('ascii')

    parts = serialized.split(':')
    if len(parts) != 2:
        raise ValueError(f"Unexpected serialization format: {serialized}")

    type_id, b64_data = parts
    if type_id != '1':
        raise ValueError(f"Expected type 1 (group element), got {type_id}")

    # Decode base64 to get raw compressed point
    compressed = base64.b64decode(b64_data)

    if len(compressed) != 33:
        raise ValueError(f"Expected 33-byte compressed key, got {len(compressed)} bytes")

    return compressed


def derive_account_id(compressed_pubkey: bytes) -> bytes:
    """
    Derive XRPL Account ID from compressed public key.

    Account ID = RIPEMD160(SHA256(public_key))

    Args:
        compressed_pubkey: 33-byte compressed secp256k1 public key

    Returns:
        20-byte Account ID
    """
    if len(compressed_pubkey) != 33:
        raise ValueError(f"Expected 33-byte compressed public key, got {len(compressed_pubkey)}")

    sha256_hash = _sha256(compressed_pubkey)
    account_id = _ripemd160(sha256_hash)

    return account_id


def encode_classic_address(account_id: bytes) -> str:
    """
    Encode Account ID as XRPL classic address.

    Classic address = base58(0x00 + account_id + checksum)

    Args:
        account_id: 20-byte Account ID

    Returns:
        Classic XRPL address (starts with 'r')
    """
    if len(account_id) != 20:
        raise ValueError(f"Expected 20-byte account ID, got {len(account_id)}")

    # Prefix with 0x00 for account address
    payload = b'\x00' + account_id

    # Calculate checksum (first 4 bytes of double SHA-256)
    checksum = _double_sha256(payload)[:4]

    # Encode with checksum
    return _base58_encode(payload + checksum)


class XRPLThresholdWallet:
    """
    XRPL wallet using threshold ECDSA for signing.

    This class wraps a threshold-generated public key and provides XRPL-specific
    functionality like address derivation and transaction signing coordination.

    Example
    -------
    >>> from charm.toolbox.eccurve import secp256k1
    >>> from charm.toolbox.ecgroup import ECGroup
    >>> from charm.schemes.threshold.dkls23_sign import DKLS23
    >>> group = ECGroup(secp256k1)
    >>> dkls = DKLS23(group, threshold=2, num_parties=3)
    >>> g = group.random(G)
    >>> key_shares, public_key = dkls.distributed_keygen(g)
    >>> wallet = XRPLThresholdWallet(group, public_key)
    >>> len(wallet.get_compressed_public_key()) == 33
    True
    >>> wallet.get_classic_address().startswith('r')
    True
    """

    def __init__(self, group: ECGroup, public_key: ec_element):
        """
        Initialize XRPL threshold wallet.

        Args:
            group: EC group (should be secp256k1 for XRPL)
            public_key: Combined threshold public key from DKG
        """
        self.group = group
        self.public_key = public_key
        self._compressed_pubkey = None
        self._account_id = None
        self._classic_address = None

    def get_compressed_public_key(self) -> bytes:
        """Get 33-byte compressed public key."""
        if self._compressed_pubkey is None:
            self._compressed_pubkey = get_compressed_public_key(self.group, self.public_key)
        return self._compressed_pubkey

    def get_account_id(self) -> bytes:
        """Get 20-byte XRPL Account ID."""
        if self._account_id is None:
            self._account_id = derive_account_id(self.get_compressed_public_key())
        return self._account_id

    def get_classic_address(self) -> str:
        """Get XRPL classic address (starts with 'r')."""
        if self._classic_address is None:
            self._classic_address = encode_classic_address(self.get_account_id())
        return self._classic_address

    def get_account_id_hex(self) -> str:
        """Get Account ID as hex string."""
        return self.get_account_id().hex().upper()

    def get_public_key_hex(self) -> str:
        """Get compressed public key as hex string."""
        return self.get_compressed_public_key().hex().upper()

    def get_x_address(self, tag: Optional[int] = None,
                      is_testnet: bool = False) -> str:
        """
        Get X-address for this wallet.

        X-addresses encode the destination tag into the address,
        which can help prevent forgotten destination tags.

        Args:
            tag: Optional destination tag (0-4294967295)
            is_testnet: True for testnet, False for mainnet

        Returns:
            X-address string

        Raises:
            ImportError: If xrpl-py is not installed
        """
        return get_x_address(self.get_classic_address(), tag=tag,
                            is_testnet=is_testnet)


def sign_xrpl_transaction_hash(
    dkls,
    participants: list,
    presignatures: dict,
    key_shares: dict,
    tx_hash: bytes,
    generator
) -> bytes:
    """
    Sign an XRPL transaction hash using threshold ECDSA.

    This function takes a pre-computed transaction hash and produces a
    DER-encoded signature suitable for XRPL transaction submission.

    Args:
        dkls: DKLS23 instance
        participants: List of participating party IDs
        presignatures: Presignatures from presign()
        key_shares: Key shares from distributed_keygen()
        tx_hash: 32-byte transaction hash (from XRPL transaction serialization)
        generator: Generator point used in key generation

    Returns:
        DER-encoded signature bytes

    Raises:
        ValueError: If tx_hash is not 32 bytes

    Example
    -------
    >>> from charm.toolbox.eccurve import secp256k1
    >>> from charm.toolbox.ecgroup import ECGroup
    >>> from charm.schemes.threshold.dkls23_sign import DKLS23
    >>> group = ECGroup(secp256k1)
    >>> dkls = DKLS23(group, threshold=2, num_parties=3)
    >>> g = group.random(G)
    >>> key_shares, public_key = dkls.distributed_keygen(g)
    >>> presigs = dkls.presign([1, 2], key_shares, g)
    >>> # Simulate a transaction hash (normally from xrpl-py)
    >>> tx_hash = b'\\x00' * 32
    >>> der_sig = sign_xrpl_transaction_hash(dkls, [1, 2], presigs, key_shares, tx_hash, g)
    >>> der_sig[0] == 0x30  # DER SEQUENCE tag
    True
    """
    if len(tx_hash) != 32:
        raise ValueError(f"Transaction hash must be 32 bytes, got {len(tx_hash)}")

    # Sign the hash using threshold ECDSA
    # Use prehashed=True since XRPL provides its own signing hash (SHA-512 truncated to 32 bytes)
    signature = dkls.sign(participants, presignatures, key_shares, tx_hash, generator, prehashed=True)

    # Convert to DER encoding for XRPL
    return signature.to_der()


def format_xrpl_signature(der_signature: bytes, public_key_hex: str) -> dict:
    """
    Format signature for XRPL transaction submission.

    Returns the signature and public key in the format expected by XRPL.

    Args:
        der_signature: DER-encoded signature from sign_xrpl_transaction_hash()
        public_key_hex: Hex-encoded compressed public key

    Returns:
        Dict with 'TxnSignature' and 'SigningPubKey' fields
    """
    return {
        'TxnSignature': der_signature.hex().upper(),
        'SigningPubKey': public_key_hex
    }


# =============================================================================
# Full XRPL Integration (requires xrpl-py)
# =============================================================================

def _check_xrpl_py():
    """Check if xrpl-py is available."""
    try:
        import xrpl
        return True
    except ImportError:
        return False


def get_x_address(classic_address: str, tag: Optional[int] = None,
                  is_testnet: bool = False) -> str:
    """
    Convert classic address to X-address format.

    X-addresses encode the destination tag into the address itself,
    reducing the risk of forgetting to include it.

    Args:
        classic_address: Classic XRPL address (starts with 'r')
        tag: Optional destination tag (0-4294967295)
        is_testnet: True for testnet, False for mainnet

    Returns:
        X-address string

    Raises:
        ImportError: If xrpl-py is not installed

    Example:
        >>> get_x_address('rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh')  # doctest: +SKIP
        'XVPcpSm47b1CZkf5AkKM9a84dQHe3m4sBhsrA4XtnBECTAc'
    """
    try:
        from xrpl.core.addresscodec import classic_address_to_xaddress
    except ImportError:
        raise ImportError(
            "xrpl-py is required for X-address support. "
            "Install with: pip install xrpl-py"
        )

    return classic_address_to_xaddress(classic_address, tag=tag,
                                       is_test_network=is_testnet)


def decode_x_address(x_address: str) -> Tuple[str, Optional[int], bool]:
    """
    Decode X-address to classic address, tag, and network.

    Args:
        x_address: X-address string

    Returns:
        Tuple of (classic_address, tag, is_testnet)

    Raises:
        ImportError: If xrpl-py is not installed
    """
    try:
        from xrpl.core.addresscodec import xaddress_to_classic_address
    except ImportError:
        raise ImportError(
            "xrpl-py is required for X-address support. "
            "Install with: pip install xrpl-py"
        )

    return xaddress_to_classic_address(x_address)


def compute_signing_hash(transaction) -> bytes:
    """
    Compute the signing hash for an XRPL transaction.

    Takes an xrpl-py transaction model or dict and returns the 32-byte
    hash that should be signed.

    Args:
        transaction: xrpl.models.Transaction or dict with transaction fields

    Returns:
        32-byte signing hash

    Raises:
        ImportError: If xrpl-py is not installed

    Example:
        >>> from xrpl.models import Payment  # doctest: +SKIP
        >>> tx = Payment(account='r...', destination='r...', amount='1000000')
        >>> tx_hash = compute_signing_hash(tx)  # doctest: +SKIP
        >>> len(tx_hash) == 32  # doctest: +SKIP
        True
    """
    try:
        from xrpl.transaction import transaction_json_to_binary_codec_form
        from xrpl.core.binarycodec import encode_for_signing
    except ImportError:
        raise ImportError(
            "xrpl-py is required for transaction serialization. "
            "Install with: pip install xrpl-py"
        )

    # Get dict representation
    if hasattr(transaction, 'to_dict'):
        tx_dict = transaction.to_dict()
    else:
        tx_dict = dict(transaction)

    # Convert to binary codec form (lowercase keys -> CamelCase)
    binary_form = transaction_json_to_binary_codec_form(tx_dict)

    # Encode for signing
    blob = encode_for_signing(binary_form)

    # XRPL signing hash = SHA-512 first 32 bytes
    return hashlib.sha512(bytes.fromhex(blob)).digest()[:32]


def sign_xrpl_transaction(
    dkls,
    wallet: 'XRPLThresholdWallet',
    participants: list,
    presignatures: dict,
    key_shares: dict,
    transaction,
    generator
) -> str:
    """
    Sign an XRPL transaction and return the signed transaction blob.

    This is the main end-to-end signing function that takes a transaction
    model, computes the signing hash, signs it with threshold ECDSA, and
    returns the complete signed transaction ready for submission.

    Args:
        dkls: DKLS23 instance
        wallet: XRPLThresholdWallet for this account
        participants: List of participating party IDs
        presignatures: Presignatures from presign()
        key_shares: Key shares from distributed_keygen()
        transaction: xrpl.models.Transaction or dict
        generator: Generator point used in key generation

    Returns:
        Hex-encoded signed transaction blob ready for submission

    Raises:
        ImportError: If xrpl-py is not installed

    Example:
        >>> # Full signing example (requires xrpl-py)  # doctest: +SKIP
        >>> from xrpl.models import Payment
        >>> tx = Payment(
        ...     account=wallet.get_classic_address(),
        ...     destination='rDestination...',
        ...     amount='1000000',
        ...     fee='12',
        ...     sequence=1
        ... )
        >>> signed_blob = sign_xrpl_transaction(
        ...     dkls, wallet, [1, 2], presigs, key_shares, tx, g
        ... )
    """
    try:
        from xrpl.transaction import transaction_json_to_binary_codec_form
        from xrpl.core.binarycodec import encode_for_signing, encode
    except ImportError:
        raise ImportError(
            "xrpl-py is required for transaction signing. "
            "Install with: pip install xrpl-py"
        )

    # Get dict representation
    if hasattr(transaction, 'to_dict'):
        tx_dict = transaction.to_dict()
    else:
        tx_dict = dict(transaction)

    # Convert to binary codec form
    binary_form = transaction_json_to_binary_codec_form(tx_dict)

    # Add signing public key
    binary_form['SigningPubKey'] = wallet.get_public_key_hex()

    # Compute signing hash
    blob = encode_for_signing(binary_form)
    tx_hash = hashlib.sha512(bytes.fromhex(blob)).digest()[:32]

    # Sign with threshold ECDSA
    der_sig = sign_xrpl_transaction_hash(
        dkls, participants, presignatures, key_shares, tx_hash, generator
    )

    # Add signature to transaction
    binary_form['TxnSignature'] = der_sig.hex().upper()

    # Encode final signed transaction
    return encode(binary_form)



class XRPLClient:
    """
    Client for XRPL network communication.

    Provides methods for querying account information and submitting
    transactions to the XRP Ledger network.

    Example:
        >>> client = XRPLClient()  # Mainnet  # doctest: +SKIP
        >>> client = XRPLClient(url='https://s.altnet.rippletest.net:51234/')  # Testnet
        >>> seq = client.get_account_sequence('rAddress...')  # doctest: +SKIP
    """

    # Common XRPL network URLs
    MAINNET_URL = 'https://xrplcluster.com/'
    TESTNET_URL = 'https://s.altnet.rippletest.net:51234/'
    DEVNET_URL = 'https://s.devnet.rippletest.net:51234/'

    def __init__(self, url: Optional[str] = None, is_testnet: bool = False):
        """
        Initialize XRPL client.

        Args:
            url: JSON-RPC URL for XRPL node. If None, uses mainnet/testnet default.
            is_testnet: If True and url is None, use testnet URL
        """
        try:
            from xrpl.clients import JsonRpcClient
        except ImportError:
            raise ImportError(
                "xrpl-py is required for network communication. "
                "Install with: pip install xrpl-py"
            )

        if url is None:
            url = self.TESTNET_URL if is_testnet else self.MAINNET_URL

        self.url = url
        self.is_testnet = is_testnet
        self._client = JsonRpcClient(url)

    @property
    def client(self):
        """Get the underlying xrpl-py JsonRpcClient."""
        return self._client

    def get_account_sequence(self, address: str) -> int:
        """
        Get the next valid sequence number for an account.

        Args:
            address: XRPL account address (classic or X-address)

        Returns:
            Next valid sequence number for transactions

        Raises:
            XRPLRequestFailureException: If the account doesn't exist
        """
        from xrpl.account import get_next_valid_seq_number
        from xrpl.core.addresscodec import is_valid_xaddress, xaddress_to_classic_address

        # Convert X-address to classic if needed
        if is_valid_xaddress(address):
            address, _, _ = xaddress_to_classic_address(address)

        return get_next_valid_seq_number(address, self._client)

    def get_balance(self, address: str) -> int:
        """
        Get the XRP balance for an account in drops.

        Args:
            address: XRPL account address

        Returns:
            Balance in drops (1 XRP = 1,000,000 drops)
        """
        from xrpl.account import get_balance
        from xrpl.core.addresscodec import is_valid_xaddress, xaddress_to_classic_address

        # Convert X-address to classic if needed
        if is_valid_xaddress(address):
            address, _, _ = xaddress_to_classic_address(address)

        return get_balance(address, self._client)

    def does_account_exist(self, address: str) -> bool:
        """
        Check if an account exists and is funded on the ledger.

        Args:
            address: XRPL account address

        Returns:
            True if account exists, False otherwise
        """
        from xrpl.account import does_account_exist
        from xrpl.core.addresscodec import is_valid_xaddress, xaddress_to_classic_address

        if is_valid_xaddress(address):
            address, _, _ = xaddress_to_classic_address(address)

        return does_account_exist(address, self._client)

    def submit_transaction(self, signed_tx_blob: str, fail_hard: bool = False) -> dict:
        """
        Submit a signed transaction to the network.

        Args:
            signed_tx_blob: Hex-encoded signed transaction from sign_xrpl_transaction()
            fail_hard: If True, don't retry or relay to other servers on failure

        Returns:
            Dict with submission result including 'engine_result' and 'tx_json'
        """
        from xrpl.models.requests import SubmitOnly

        request = SubmitOnly(tx_blob=signed_tx_blob, fail_hard=fail_hard)
        response = self._client.request(request)
        return response.result

    def submit_and_wait(self, signed_tx_blob: str,
                        wallet_address: Optional[str] = None) -> dict:
        """
        Submit a signed transaction and wait for validation.

        Args:
            signed_tx_blob: Hex-encoded signed transaction
            wallet_address: Optional address to include in the last_ledger_sequence

        Returns:
            Dict with validated transaction result
        """
        from xrpl.transaction import submit

        response = submit(signed_tx_blob, self._client)
        return response.result

    def autofill_transaction(self, transaction) -> dict:
        """
        Autofill transaction fields (fee, sequence, last_ledger_sequence).

        Takes a transaction and fills in network-specific fields automatically.

        Args:
            transaction: xrpl.models.Transaction or dict

        Returns:
            Dict with autofilled transaction fields
        """
        from xrpl.transaction import autofill

        if hasattr(transaction, 'to_dict'):
            # It's an xrpl model
            autofilled = autofill(transaction, self._client)
            return autofilled.to_dict()
        else:
            # It's a dict, need to convert to model first
            from xrpl.models import Transaction
            from xrpl.transaction import transaction_json_to_binary_codec_form

            # For dict input, manually handle autofill
            tx_dict = dict(transaction)

            # Get sequence if not set
            if 'sequence' not in tx_dict or tx_dict.get('sequence') is None:
                account = tx_dict.get('account') or tx_dict.get('Account')
                tx_dict['sequence'] = self.get_account_sequence(account)

            return tx_dict

    def get_transaction(self, tx_hash: str) -> dict:
        """
        Look up a transaction by its hash.

        Args:
            tx_hash: Transaction hash (hex string)

        Returns:
            Transaction details dict
        """
        from xrpl.models.requests import Tx

        request = Tx(transaction=tx_hash)
        response = self._client.request(request)
        return response.result

    @staticmethod
    def fund_from_faucet(address: str, timeout: int = 60) -> dict:
        """
        Fund an account from the XRPL testnet faucet.

        This only works on testnet/devnet.

        Args:
            address: The address to fund
            timeout: Timeout in seconds (default: 60)

        Returns:
            Dict with faucet response including 'balance' and 'address'

        Raises:
            RuntimeError: If faucet request fails
        """
        import httpx
        import time

        faucet_url = "https://faucet.altnet.rippletest.net/accounts"

        try:
            response = httpx.post(
                faucet_url,
                json={"destination": address},
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()

            # Wait a moment for the transaction to be validated
            time.sleep(2)

            return {
                'address': address,
                'balance': result.get('account', {}).get('balance'),
                'faucet_response': result
            }
        except Exception as e:
            raise RuntimeError(f"Faucet request failed: {e}")



# =============================================================================
# Memo Helper Functions
# =============================================================================

def encode_memo_data(text: str) -> str:
    """
    Encode a text string as hex for XRPL memo data.

    XRPL memos require hex-encoded data.

    Args:
        text: Plain text string to encode

    Returns:
        Uppercase hex-encoded string

    Example:
        >>> encode_memo_data("Hello")
        '48656C6C6F'
    """
    return text.encode('utf-8').hex().upper()


def decode_memo_data(hex_data: str) -> str:
    """
    Decode hex-encoded XRPL memo data to text.

    Args:
        hex_data: Hex-encoded memo data

    Returns:
        Decoded text string

    Example:
        >>> decode_memo_data('48656C6C6F')
        'Hello'
    """
    return bytes.fromhex(hex_data).decode('utf-8')


def create_memo(data: str, memo_type: Optional[str] = None,
                memo_format: Optional[str] = None) -> dict:
    """
    Create an XRPL memo dict with properly encoded fields.

    This helper encodes plain text to hex format as required by XRPL.

    Args:
        data: The memo data (plain text, will be hex-encoded)
        memo_type: Optional memo type (e.g., 'text/plain', will be hex-encoded)
        memo_format: Optional memo format (e.g., 'text/plain', will be hex-encoded)

    Returns:
        Dict suitable for use in xrpl.models.Memo

    Example:
        >>> memo = create_memo("Hello World", memo_type="text/plain")
        >>> memo['memo_data']
        '48656C6C6F20576F726C64'
    """
    memo = {
        'memo_data': encode_memo_data(data)
    }

    if memo_type:
        memo['memo_type'] = encode_memo_data(memo_type)

    if memo_format:
        memo['memo_format'] = encode_memo_data(memo_format)

    return memo


def create_payment_with_memo(
    account: str,
    destination: str,
    amount: str,
    memo_text: str,
    sequence: Optional[int] = None,
    fee: str = "12",
    memo_type: str = "text/plain"
):
    """
    Create an XRPL Payment transaction with a memo.

    This is a convenience function that handles memo encoding.

    Args:
        account: Source account address
        destination: Destination account address
        amount: Amount in drops (1 XRP = 1,000,000 drops)
        memo_text: Plain text memo message
        sequence: Account sequence number (required)
        fee: Transaction fee in drops (default: "12")
        memo_type: Memo type (default: "text/plain")

    Returns:
        xrpl.models.Payment transaction object

    Example:
        >>> tx = create_payment_with_memo(
        ...     account='rSourceAddress...',
        ...     destination='rDestAddress...',
        ...     amount='10000000',  # 10 XRP
        ...     memo_text='Hello from threshold ECDSA!',
        ...     sequence=1
        ... )
    """
    try:
        from xrpl.models import Payment, Memo
    except ImportError:
        raise ImportError(
            "xrpl-py is required. Install with: pip install xrpl-py"
        )

    memo_dict = create_memo(memo_text, memo_type=memo_type)

    return Payment(
        account=account,
        destination=destination,
        amount=amount,
        sequence=sequence,
        fee=fee,
        memos=[Memo(**memo_dict)]
    )


def get_transaction_memos(tx_result: dict) -> list:
    """
    Extract and decode memos from a transaction result.

    Args:
        tx_result: Transaction result dict from XRPL

    Returns:
        List of decoded memo dicts with 'data', 'type', 'format' keys
    """
    memos = []
    tx_memos = tx_result.get('Memos', [])

    for memo_wrapper in tx_memos:
        memo = memo_wrapper.get('Memo', {})
        decoded = {}

        if 'MemoData' in memo:
            try:
                decoded['data'] = decode_memo_data(memo['MemoData'])
            except Exception:
                decoded['data'] = memo['MemoData']  # Keep hex if decode fails

        if 'MemoType' in memo:
            try:
                decoded['type'] = decode_memo_data(memo['MemoType'])
            except Exception:
                decoded['type'] = memo['MemoType']

        if 'MemoFormat' in memo:
            try:
                decoded['format'] = decode_memo_data(memo['MemoFormat'])
            except Exception:
                decoded['format'] = memo['MemoFormat']

        memos.append(decoded)

    return memos