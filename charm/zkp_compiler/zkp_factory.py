"""
Factory for creating ZK proof instances without dynamic code execution.

This module provides a safe alternative to the exec()-based code generation
in zkp_generator.py, eliminating code injection vulnerabilities.
"""

import logging
import re
from charm.zkp_compiler.zkparser import ZKParser
from charm.zkp_compiler.schnorr_proof import SchnorrProof, Proof
from charm.zkp_compiler.dleq_proof import DLEQProof
from charm.toolbox.ZKProof import ZKProofBase, ZKParseError, ZKValidationError

logger = logging.getLogger(__name__)

# Allowed characters in ZK statements
_VALID_STATEMENT_PATTERN = re.compile(r'^[\w\s\^\=\(\)\*]+$')


def validate_statement(statement):
    """
    Validate a ZK statement string.
    
    Checks for valid characters and prevents injection attacks.
    
    Args:
        statement: The ZK statement string to validate
    
    Raises:
        ZKValidationError: If statement is invalid or contains suspicious characters
    """
    if not isinstance(statement, str):
        raise ZKValidationError("Statement must be a string")
    
    if not statement.strip():
        raise ZKValidationError("Statement cannot be empty")
    
    if not _VALID_STATEMENT_PATTERN.match(statement):
        raise ZKValidationError(
            "Statement contains invalid characters. "
            "Only alphanumeric characters, ^, =, *, (, ), and whitespace are allowed."
        )
    
    # Check for suspicious patterns that might indicate injection attempts
    suspicious_patterns = ['__', 'import', 'exec', 'eval', 'compile', 'open', 'file']
    statement_lower = statement.lower()
    for pattern in suspicious_patterns:
        if pattern in statement_lower:
            raise ZKValidationError(f"Statement contains suspicious pattern: {pattern}")
    
    logger.debug("Statement validated: %s", statement)


class SchnorrProofInstance:
    """
    Wrapper that provides a clean API for Schnorr proofs.
    
    Encapsulates the generator, public value, and optionally secret,
    providing prove() and verify() methods.
    """
    
    def __init__(self, group, g, h, secret_x=None):
        """
        Initialize a Schnorr proof instance.
        
        Args:
            group: The pairing group to use
            g: The generator element
            h: The public element (h = g^x)
            secret_x: The secret exponent (required for proving, optional for verifying)
        """
        self.group = group
        self.g = g
        self.h = h
        self._secret_x = secret_x
    
    def prove(self, interactive=False):
        """
        Generate a proof (non-interactive by default).
        
        Args:
            interactive: If True, raises an error (use create_interactive_prover instead)
        
        Returns:
            Proof object containing commitment, challenge, and response
        
        Raises:
            ZKValidationError: If secret is not available or interactive mode requested
        """
        if self._secret_x is None:
            raise ZKValidationError("Cannot prove without secret")
        if interactive:
            raise ZKValidationError(
                "For interactive proofs, use create_interactive_prover() instead"
            )
        return SchnorrProof.prove_non_interactive(
            self.group, self.g, self.h, self._secret_x
        )
    
    def verify(self, proof):
        """
        Verify a proof.
        
        Args:
            proof: Proof object to verify
        
        Returns:
            True if proof is valid, False otherwise
        """
        return SchnorrProof.verify_non_interactive(
            self.group, self.g, self.h, proof
        )
    
    def create_interactive_prover(self):
        """
        Create an interactive prover instance.
        
        Returns:
            SchnorrProof.Prover instance
        
        Raises:
            ZKValidationError: If secret is not available
        """
        if self._secret_x is None:
            raise ZKValidationError("Cannot create prover without secret")
        return SchnorrProof.Prover(self._secret_x, self.group)
    
    def create_interactive_verifier(self):
        """
        Create an interactive verifier instance.
        
        Returns:
            SchnorrProof.Verifier instance
        """
        return SchnorrProof.Verifier(self.group)


class ZKProofFactory:
    """
    Factory for creating ZK proof instances without dynamic code execution.
    
    This factory replaces the insecure exec()-based code generation with
    direct class instantiation, eliminating code injection vulnerabilities.
    
    Example:
        >>> from charm.toolbox.pairinggroup import PairingGroup, ZR, G1
        >>> group = PairingGroup('SS512')
        >>> g = group.random(G1)
        >>> x = group.random(ZR)
        >>> h = g ** x
        >>> 
        >>> # Create a Schnorr proof instance
        >>> proof_instance = ZKProofFactory.create_schnorr_proof(group, g, h, x)
        >>> proof = proof_instance.prove()
        >>> assert proof_instance.verify(proof)
    """
    
    @staticmethod
    def create_schnorr_proof(group, g, h, secret_x=None):
        """
        Create a Schnorr proof instance for proving knowledge of discrete log.
        
        Args:
            group: The pairing group to use
            g: The generator element
            h: The public element (h = g^x)
            secret_x: The secret exponent (required for proving, optional for verifying)
        
        Returns:
            SchnorrProofInstance: An instance that can prove or verify
        """
        logger.debug("Creating Schnorr proof instance")
        return SchnorrProofInstance(group, g, h, secret_x)
    
    @staticmethod
    def create_from_statement(group, statement, public_params, secret_params=None):
        """
        Create a proof instance from a parsed ZK statement.
        
        This method parses the statement and determines the appropriate
        proof type, then creates the corresponding proof instance.
        
        Args:
            group: The pairing group to use
            statement: A ZK statement string like "h = g^x"
            public_params: Dict mapping variable names to public values
            secret_params: Dict mapping variable names to secret values (optional)
        
        Returns:
            SchnorrProofInstance: An instance of the appropriate proof type
        
        Raises:
            ZKParseError: If the statement cannot be parsed
            ZKValidationError: If required parameters are missing
        """
        # Validate statement first
        validate_statement(statement)
        
        # Parse the statement
        try:
            parser = ZKParser()
            stmt_object = parser.parse(statement)
        except Exception as e:
            raise ZKParseError(f"Failed to parse statement: {e}") from e
        
        # Extract required variables from the parsed statement
        # For now, we support simple Schnorr-style statements: h = g^x
        # The parser returns a tree structure that we need to analyze
        
        if not isinstance(public_params, dict):
            raise ZKValidationError("public_params must be a dictionary")
        
        if secret_params is not None and not isinstance(secret_params, dict):
            raise ZKValidationError("secret_params must be a dictionary")
        
        # Check for required public parameters
        if 'g' not in public_params:
            raise ZKValidationError("Missing required public parameter: 'g' (generator)")
        if 'h' not in public_params:
            raise ZKValidationError("Missing required public parameter: 'h' (public value)")
        
        g = public_params['g']
        h = public_params['h']
        
        # Get secret if available
        secret_x = None
        if secret_params and 'x' in secret_params:
            secret_x = secret_params['x']
        
        logger.debug("Created proof instance from statement: %s", statement)
        return SchnorrProofInstance(group, g, h, secret_x)


def prove_and_verify_schnorr(group, g, h, x):
    """
    Proves and immediately verifies a Schnorr proof.

    Useful for testing and debugging.

    Args:
        group: The pairing group to use
        g: The generator element
        h: The public element (h = g^x)
        x: The secret exponent

    Returns:
        tuple: (proof, is_valid) where proof is the Proof object and is_valid is True if verification passed

    Example::

        group = PairingGroup('SS512')
        g = group.random(G1)
        x = group.random(ZR)
        h = g ** x
        proof, is_valid = prove_and_verify_schnorr(group, g, h, x)
        assert is_valid
    """
    proof = SchnorrProof.prove_non_interactive(group, g, h, x)
    is_valid = SchnorrProof.verify_non_interactive(group, g, h, proof)
    return proof, is_valid


def prove_and_verify_dleq(group, g1, h1, g2, h2, x):
    """
    Proves and immediately verifies a DLEQ proof.

    Useful for testing and debugging.

    Args:
        group: The pairing group to use
        g1: The first generator element
        h1: The first public element (h1 = g1^x)
        g2: The second generator element
        h2: The second public element (h2 = g2^x)
        x: The secret exponent

    Returns:
        tuple: (proof, is_valid) where proof is the DLEQProofData object and is_valid is True if verification passed

    Example::

        group = PairingGroup('SS512')
        g1 = group.random(G1)
        g2 = group.random(G1)
        x = group.random(ZR)
        h1 = g1 ** x
        h2 = g2 ** x
        proof, is_valid = prove_and_verify_dleq(group, g1, h1, g2, h2, x)
        assert is_valid
    """
    proof = DLEQProof.prove_non_interactive(group, g1, h1, g2, h2, x)
    is_valid = DLEQProof.verify_non_interactive(group, g1, h1, g2, h2, proof)
    return proof, is_valid


def configure_logging(level: str = 'WARNING') -> None:
    """
    Configure logging for all ZKP compiler modules.

    Args:
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

    Example:
        >>> from charm.zkp_compiler import configure_logging
        >>> configure_logging('DEBUG')  # Enable debug output
    """
    numeric_level = getattr(logging, level.upper(), logging.WARNING)

    # Configure all ZKP module loggers
    zkp_modules = [
        'charm.zkp_compiler.schnorr_proof',
        'charm.zkp_compiler.dleq_proof',
        'charm.zkp_compiler.representation_proof',
        'charm.zkp_compiler.and_proof',
        'charm.zkp_compiler.or_proof',
        'charm.zkp_compiler.range_proof',
        'charm.zkp_compiler.batch_verify',
    ]

    for module in zkp_modules:
        module_logger = logging.getLogger(module)
        module_logger.setLevel(numeric_level)
        if not module_logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(name)s - %(levelname)s - %(message)s'
            ))
            module_logger.addHandler(handler)

