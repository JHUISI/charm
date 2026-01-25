"""
Charm ZKP Compiler Module
=========================

This module provides zero-knowledge proof implementations for Charm-Crypto.

Recommended (Secure) API
------------------------
The following modules provide secure, production-ready ZKP implementations:

- :mod:`charm.zkp_compiler.schnorr_proof` - Schnorr protocol (discrete log)
- :mod:`charm.zkp_compiler.dleq_proof` - DLEQ/Chaum-Pedersen protocol
- :mod:`charm.zkp_compiler.representation_proof` - Knowledge of representation
- :mod:`charm.zkp_compiler.and_proof` - AND composition of proofs
- :mod:`charm.zkp_compiler.or_proof` - OR composition (CDS94)
- :mod:`charm.zkp_compiler.range_proof` - Range proofs via bit decomposition
- :mod:`charm.zkp_compiler.batch_verify` - Batch verification utilities
- :mod:`charm.zkp_compiler.zkp_factory` - Factory for creating proofs
- :mod:`charm.zkp_compiler.thread_safe` - Thread-safe wrappers

Deprecated (Legacy) API
-----------------------
The following module is DEPRECATED and will be removed in v0.80:

- :mod:`charm.zkp_compiler.zkp_generator` - Uses insecure exec()/compile()

Example Migration
-----------------
Old (deprecated)::

    from charm.zkp_compiler.zkp_generator import executeIntZKProof
    result = executeIntZKProof(public, secret, statement, party_info)

New (recommended)::

    from charm.zkp_compiler.schnorr_proof import SchnorrProof
    proof = SchnorrProof.prove_non_interactive(group, g, h, x)
    is_valid = SchnorrProof.verify_non_interactive(group, g, h, proof)

Curve Recommendation
--------------------
Use BN254 curve for ~128-bit security (recommended for production)::

    from charm.toolbox.pairinggroup import PairingGroup
    group = PairingGroup('BN254')

See Also
--------
- doc/zkp_proof_types_design.md for detailed documentation
- charm/zkp_compiler/zk_demo.py for usage examples
"""

# Secure API exports (recommended)
from charm.zkp_compiler.schnorr_proof import SchnorrProof, Proof
from charm.zkp_compiler.dleq_proof import DLEQProof
from charm.zkp_compiler.representation_proof import RepresentationProof
from charm.zkp_compiler.and_proof import ANDProof
from charm.zkp_compiler.or_proof import ORProof
from charm.zkp_compiler.range_proof import RangeProof
from charm.zkp_compiler.batch_verify import BatchVerifier, batch_verify_schnorr, batch_verify_dleq
from charm.zkp_compiler.zkp_factory import (
    ZKProofFactory,
    configure_logging,
    prove_and_verify_schnorr,
    prove_and_verify_dleq,
)
from charm.zkp_compiler.thread_safe import ThreadSafeProver, ThreadSafeVerifier

__all__ = [
    # Proof types
    'SchnorrProof',
    'DLEQProof',
    'RepresentationProof',
    'ANDProof',
    'ORProof',
    'RangeProof',
    'Proof',
    # Utilities
    'BatchVerifier',
    'batch_verify_schnorr',
    'batch_verify_dleq',
    'ZKProofFactory',
    'ThreadSafeProver',
    'ThreadSafeVerifier',
    # Convenience functions
    'configure_logging',
    'prove_and_verify_schnorr',
    'prove_and_verify_dleq',
]