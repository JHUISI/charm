"""
Base class for Zero-Knowledge Proof systems.

This module provides a base class for implementing zero-knowledge proof schemes
in the Charm cryptographic library. Zero-knowledge proofs allow a prover to
convince a verifier that a statement is true without revealing any additional
information beyond the validity of the statement.

The module defines:
    - Security definitions for ZK proofs (HVZK, ZK, NIZK, SIM)
    - Exception classes for error handling
    - ZKProofBase class for implementing concrete ZK proof schemes
    - Proof dataclass for storing proof components

Security Properties:
    - HVZK: Honest-Verifier Zero-Knowledge - secure against honest verifiers
    - ZK: Zero-Knowledge - secure against malicious verifiers
    - NIZK: Non-Interactive Zero-Knowledge - no interaction required
    - SIM: Simulation Sound - proofs cannot be simulated without witness

Example:
    class SchnorrProof(ZKProofBase):
        def setup(self, group):
            # Initialize with the group
            ...
        def prove(self, statement, witness):
            # Generate Schnorr proof
            ...
        def verify(self, statement, proof):
            # Verify Schnorr proof
            ...
"""
from charm.toolbox.schemebase import *
from charm.toolbox.enum import *
from dataclasses import dataclass
from typing import Any, Optional

# Security definitions for zero-knowledge proofs
zkpSecDefs = Enum('HVZK', 'ZK', 'NIZK', 'SIM')
HVZK, ZK, NIZK, SIM = "HVZK", "ZK", "NIZK", "SIM"


class ZKProofError(Exception):
    """Base exception for the ZKP module.
    
    All ZKP-related exceptions inherit from this class, allowing
    for broad exception catching when needed.
    """
    pass


class ZKParseError(ZKProofError):
    """Error parsing ZK statements.
    
    Raised when a zero-knowledge statement cannot be parsed,
    typically due to malformed input or invalid syntax.
    """
    pass


class ZKValidationError(ZKProofError):
    """Error validating inputs.
    
    Raised when inputs to ZKP operations fail validation,
    such as invalid group elements or malformed witnesses.
    """
    pass


class ZKProofVerificationError(ZKProofError):
    """Proof verification failed.
    
    Raised when a zero-knowledge proof fails verification,
    indicating either an invalid proof or mismatched statement.
    """
    pass


@dataclass
class Proof:
    """Dataclass to hold zero-knowledge proof components.
    
    This class encapsulates all components of a zero-knowledge proof,
    following the standard Sigma protocol structure (commitment, challenge, response).
    
    Attributes:
        commitment: The prover's initial commitment value(s). This is the first
            message in a Sigma protocol, committing the prover to random values.
        challenge: The challenge value from the verifier (or derived via Fiat-Shamir
            for non-interactive proofs). Must be unpredictable to the prover.
        response: The prover's response computed using the witness and challenge.
            This allows the verifier to check the proof without learning the witness.
        proof_type: String identifier for the type of proof (e.g., 'schnorr', 'dleq',
            'or', 'and'). Used for deserialization and validation.
        version: Integer version number for the proof format. Allows for backward
            compatibility when proof formats evolve.
    
    Example:
        proof = Proof(
            commitment=g ** r,
            challenge=hash(commitment, statement),
            response=r + challenge * secret,
            proof_type='schnorr',
            version=1
        )
    """
    commitment: Any
    challenge: Any
    response: Any
    proof_type: str
    version: int = 1


class ZKProofBase(SchemeBase):
    """Base class for zero-knowledge proof schemes.
    
    This class provides the foundation for implementing zero-knowledge proof
    systems in Charm. Concrete implementations should extend this class and
    implement all abstract methods.
    
    A zero-knowledge proof scheme consists of three core algorithms:
        - setup: Initialize the proof system with group parameters
        - prove: Generate a proof that a statement is true given a witness
        - verify: Verify that a proof is valid for a given statement
    
    Additionally, serialization methods are provided for proof persistence
    and network transmission.
    
    Security Properties:
        Implementations should specify their security level using setProperty():
        - HVZK: Secure against honest verifiers only
        - ZK: Secure against malicious verifiers (requires simulation)
        - NIZK: Non-interactive (typically via Fiat-Shamir transform)
        - SIM: Simulation soundness (proofs unforgeable even with simulated proofs)
    
    Example:
        class MyZKProof(ZKProofBase):
            def __init__(self):
                ZKProofBase.__init__(self)
                self.setProperty(secDef='NIZK', assumption='DL', secModel='ROM')
    """
    
    def __init__(self):
        """Initialize the ZKProof base class.

        Calls the parent SchemeBase constructor and sets the scheme type
        to 'ZKProof' for property tracking and type checking.
        """
        SchemeBase.__init__(self)
        SchemeBase._setProperty(self, scheme='ZKProof')

    def setProperty(self, secDef=None, assumption=None, messageSpace=None, secModel=None, **kwargs):
        """Set security properties for this ZK proof scheme.

        Configures the security properties of the proof scheme, including
        the security definition, hardness assumption, and security model.

        Args:
            secDef: Security definition, must be one of: 'HVZK', 'ZK', 'NIZK', 'SIM'.
                Defines the zero-knowledge security level of the scheme.
            assumption: The computational hardness assumption (e.g., 'DL', 'DDH').
                Should be a string representing the underlying assumption.
            messageSpace: Description of the valid message/statement space.
                Can be a type or list of types.
            secModel: Security model, typically 'SM' (standard), 'ROM' (random oracle),
                or 'CRS' (common reference string).
            **kwargs: Additional scheme-specific properties.

        Returns:
            bool: True if properties were set successfully.

        Raises:
            AssertionError: If secDef is not a valid security definition.
        """
        assert secDef is not None and secDef in zkpSecDefs.getList(), \
            "not a valid security definition for this scheme type."
        SchemeBase._setProperty(self, None, zkpSecDefs[secDef], str(assumption),
                                messageSpace, str(secModel), **kwargs)
        return True

    def getProperty(self):
        """Get the security properties of this ZK proof scheme.

        Returns:
            dict: A dictionary containing all configured security properties,
                including scheme type, security definition, assumption,
                message space, and security model.
        """
        baseProp = SchemeBase._getProperty(self)
        return baseProp

    def setup(self, group):
        """Initialize the proof system with group parameters.

        This method should initialize any scheme-specific parameters
        needed for proof generation and verification.

        Args:
            group: The algebraic group to use for the proof system.
                Typically a pairing group or integer group from Charm.

        Returns:
            Implementation-specific setup parameters (e.g., public parameters).

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def prove(self, statement, witness):
        """Generate a zero-knowledge proof.

        Creates a proof that the prover knows a witness satisfying the
        given statement, without revealing the witness itself.

        Args:
            statement: The public statement to prove. The format depends
                on the specific proof type (e.g., public key for Schnorr).
            witness: The secret witness known only to the prover
                (e.g., private key for Schnorr).

        Returns:
            Proof: A Proof object containing commitment, challenge, and response.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
            ZKValidationError: If statement or witness validation fails.
        """
        raise NotImplementedError

    def verify(self, statement, proof):
        """Verify a zero-knowledge proof.

        Checks whether the given proof is valid for the statement,
        confirming that the prover knows a valid witness.

        Args:
            statement: The public statement that was proven.
            proof: The Proof object to verify.

        Returns:
            bool: True if the proof is valid, False otherwise.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
            ZKValidationError: If statement or proof format is invalid.
            ZKProofVerificationError: If verification fails due to invalid proof.
        """
        raise NotImplementedError

    def serialize(self, proof, group):
        """Serialize a proof to bytes.

        Converts a Proof object to a byte representation suitable for
        storage or network transmission.

        Args:
            proof: The Proof object to serialize.
            group: The algebraic group used in the proof, needed for
                serializing group elements.

        Returns:
            bytes: The serialized proof data.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
            ZKValidationError: If proof format is invalid for serialization.
        """
        raise NotImplementedError

    def deserialize(self, data, group):
        """Deserialize bytes to a proof.

        Reconstructs a Proof object from its byte representation.

        Args:
            data: The serialized proof bytes.
            group: The algebraic group used in the proof, needed for
                deserializing group elements.

        Returns:
            Proof: The reconstructed Proof object.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
            ZKParseError: If the data cannot be parsed as a valid proof.
        """
        raise NotImplementedError

