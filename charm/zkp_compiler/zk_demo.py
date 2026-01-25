#!/usr/bin/env python
"""
Zero-Knowledge Proof Demo - Secure API Migration Guide

This demo shows both the legacy (deprecated) API and the new secure API for
zero-knowledge proofs in Charm-Crypto.

=== RECOMMENDED CURVE: BN254 ===

This demo uses the BN254 (Barreto-Naehrig) curve which provides:
- ~128-bit security level (vs SS512's ~80-bit security)
- Efficient pairing operations
- Widely used in production systems (e.g., Ethereum precompiles)

Available curves and their security levels:
- BN254:   ~128-bit security (RECOMMENDED for production)
- SS512:   ~80-bit security  (legacy, not recommended)
- MNT224:  ~112-bit security (asymmetric curve)
- SS1024:  ~80-bit security  (larger but same security as SS512)

=== MIGRATION GUIDE ===

The legacy API (executeIntZKProof, executeNonIntZKProof) uses insecure dynamic
code execution (exec/compile) which can lead to code injection vulnerabilities.
The new secure API directly implements the ZKP protocols without dynamic code.

OLD (deprecated - security risk):
    from charm.zkp_compiler.zkp_generator import executeIntZKProof
    result = executeIntZKProof(pk, sk, '(h = g^x)', party_info)

NEW (secure - recommended):
    from charm.zkp_compiler.schnorr_proof import SchnorrProof
    proof = SchnorrProof.prove_non_interactive(group, g, h, x)
    is_valid = SchnorrProof.verify_non_interactive(group, g, h, proof)

=== PROOF MODES ===

Interactive Mode:
    - Prover and verifier exchange messages in real-time
    - Requires network socket connection
    - Prover: commitment -> Verifier: challenge -> Prover: response -> Verifier: verify
    - Security: Honest-Verifier Zero-Knowledge (HVZK)

Non-Interactive Mode (Fiat-Shamir):
    - Prover generates complete proof locally using hash function as "random oracle"
    - Proof can be transmitted and verified offline
    - No real-time interaction required
    - Security: Non-Interactive Zero-Knowledge (NIZK) in the Random Oracle Model

Usage:
    # Interactive mode (legacy) - requires two terminals:
    Terminal 1: python zk_demo.py -v          # Start verifier first
    Terminal 2: python zk_demo.py -p          # Then start prover

    # Non-interactive mode (new secure API):
    python zk_demo.py --demo-secure           # Runs complete demo locally
    python zk_demo.py --demo-interactive      # Runs interactive demo locally
    python zk_demo.py --demo-serialization    # Runs serialization demo
"""

from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from charm.core.engine.util import objectToBytes, bytesToObject
from socket import *
import sys
import warnings

# =============================================================================
# NEW SECURE API IMPORTS (Recommended)
# =============================================================================
# These modules implement ZKP protocols directly without exec() or eval()
from charm.zkp_compiler.schnorr_proof import SchnorrProof, Proof
from charm.zkp_compiler.zkp_factory import ZKProofFactory

# =============================================================================
# LEGACY API IMPORTS (Deprecated - uses insecure exec())
# =============================================================================
# WARNING: This import uses dynamic code execution which is a security risk.
# Only use for backwards compatibility with existing code.
from charm.zkp_compiler.zkp_generator import executeIntZKProof


# =============================================================================
# NEW SECURE API DEMOS
# =============================================================================

def demo_non_interactive_proof():
    """
    Demonstrate non-interactive Schnorr proof using the new secure API.

    This is the recommended approach for most use cases:
    - No real-time interaction required
    - Proof can be serialized and transmitted
    - Verifier can verify offline
    - Uses Fiat-Shamir heuristic for security
    """
    print("\n" + "=" * 70)
    print("NON-INTERACTIVE SCHNORR PROOF DEMO (New Secure API)")
    print("=" * 70)

    # Setup: Use BN254 curve (~128-bit security, recommended for production)
    group = PairingGroup('BN254')
    print(f"\n[Setup] Using pairing group: BN254 (~128-bit security)")

    # Prover's secret and public values
    g = group.random(G1)   # Generator (public)
    x = group.random(ZR)   # Secret exponent (prover's secret)
    h = g ** x             # Public value (h = g^x)

    print(f"[Prover] Generated secret x and computed h = g^x")
    print(f"[Prover] Statement to prove: 'I know x such that h = g^x'")

    # =========================================================================
    # PROVER: Generate proof
    # =========================================================================
    print("\n--- Prover generates proof ---")

    # Method 1: Direct API (recommended for simple Schnorr proofs)
    proof = SchnorrProof.prove_non_interactive(group, g, h, x)

    print(f"[Prover] Created proof with:")
    print(f"         - Commitment (u = g^r): {str(proof.commitment)[:50]}...")
    print(f"         - Challenge (c = H(g,h,u)): {str(proof.challenge)[:50]}...")
    print(f"         - Response (z = r + c*x): {str(proof.response)[:50]}...")

    # =========================================================================
    # VERIFIER: Verify proof
    # =========================================================================
    print("\n--- Verifier verifies proof ---")

    # Verifier only needs: g, h (public values) and the proof
    is_valid = SchnorrProof.verify_non_interactive(group, g, h, proof)

    print(f"[Verifier] Checking: g^z == u * h^c")
    print(f"[Verifier] Proof valid: {is_valid}")

    # =========================================================================
    # Demonstrate that wrong secret fails
    # =========================================================================
    print("\n--- Demonstrating invalid proof detection ---")
    wrong_x = group.random(ZR)
    wrong_proof = SchnorrProof.prove_non_interactive(group, g, h, wrong_x)
    is_valid_wrong = SchnorrProof.verify_non_interactive(group, g, h, wrong_proof)
    print(f"[Verifier] Proof with wrong secret valid: {is_valid_wrong} (expected: False)")

    return proof, group, g, h


def demo_interactive_proof():
    """
    Demonstrate interactive Schnorr proof using the new secure API.

    Interactive mode is useful when:
    - Prover and verifier can communicate in real-time
    - You want the verifier to contribute randomness (challenge)
    - Security against malicious verifiers is not required

    Protocol flow:
    1. Prover -> Verifier: commitment (u = g^r)
    2. Verifier -> Prover: challenge (c, random)
    3. Prover -> Verifier: response (z = r + c*x)
    4. Verifier: verify g^z == u * h^c
    """
    print("\n" + "=" * 70)
    print("INTERACTIVE SCHNORR PROOF DEMO (New Secure API)")
    print("=" * 70)

    # Setup: Use BN254 curve (~128-bit security)
    group = PairingGroup('BN254')
    g = group.random(G1)
    x = group.random(ZR)
    h = g ** x

    print(f"\n[Setup] Generator g and public value h = g^x")

    # Create prover and verifier instances
    prover = SchnorrProof.Prover(x, group)
    verifier = SchnorrProof.Verifier(group)

    print("\n--- Interactive Protocol ---")

    # Step 1: Prover creates commitment
    print("\n[Step 1] Prover -> Verifier: commitment")
    commitment = prover.create_commitment(g)
    print(f"         u = g^r: {str(commitment)[:50]}...")

    # Step 2: Verifier creates challenge
    print("\n[Step 2] Verifier -> Prover: challenge")
    challenge = verifier.create_challenge()
    print(f"         c (random): {str(challenge)[:50]}...")

    # Step 3: Prover creates response
    print("\n[Step 3] Prover -> Verifier: response")
    response = prover.create_response(challenge)
    print(f"         z = r + c*x: {str(response)[:50]}...")

    # Step 4: Verifier verifies
    print("\n[Step 4] Verifier: verify")
    is_valid = verifier.verify(g, h, commitment, response)
    print(f"         g^z == u * h^c: {is_valid}")

    return is_valid


def demo_serialization():
    """
    Demonstrate proof serialization for network transmission.

    In real applications, the prover and verifier are on different machines.
    This demo shows how to:
    1. Serialize a proof to bytes for transmission
    2. Deserialize the proof on the receiver side
    3. Verify the deserialized proof
    """
    print("\n" + "=" * 70)
    print("PROOF SERIALIZATION DEMO (Network Transmission)")
    print("=" * 70)

    # Setup: Use BN254 curve (~128-bit security)
    group = PairingGroup('BN254')
    g = group.random(G1)
    x = group.random(ZR)
    h = g ** x

    # =========================================================================
    # PROVER SIDE: Generate and serialize proof
    # =========================================================================
    print("\n--- Prover Side ---")

    # Generate proof
    proof = SchnorrProof.prove_non_interactive(group, g, h, x)
    print(f"[Prover] Generated proof")

    # Serialize proof to bytes
    proof_bytes = SchnorrProof.serialize_proof(proof, group)
    print(f"[Prover] Serialized proof to {len(proof_bytes)} bytes")

    # Also serialize public values (g, h) for transmission
    public_bytes = objectToBytes({'g': g, 'h': h}, group)
    print(f"[Prover] Serialized public values to {len(public_bytes)} bytes")

    # Total message size
    print(f"[Prover] Total transmission: {len(proof_bytes) + len(public_bytes)} bytes")

    # =========================================================================
    # NETWORK TRANSMISSION (simulated)
    # =========================================================================
    print("\n--- Network Transmission (simulated) ---")
    print(f"         Sending {len(proof_bytes) + len(public_bytes)} bytes...")

    # =========================================================================
    # VERIFIER SIDE: Deserialize and verify
    # =========================================================================
    print("\n--- Verifier Side ---")

    # Deserialize public values
    received_public = bytesToObject(public_bytes, group)
    received_g = received_public['g']
    received_h = received_public['h']
    print(f"[Verifier] Deserialized public values")

    # Deserialize proof
    received_proof = SchnorrProof.deserialize_proof(proof_bytes, group)
    print(f"[Verifier] Deserialized proof")

    # Verify
    is_valid = SchnorrProof.verify_non_interactive(group, received_g, received_h, received_proof)
    print(f"[Verifier] Proof verification: {is_valid}")

    return is_valid


def demo_factory_api():
    """
    Demonstrate the ZKProofFactory API for statement-based proof creation.

    The factory provides a higher-level API that:
    - Validates statements for security
    - Creates appropriate proof instances based on the statement
    - Provides a clean prove()/verify() interface
    """
    print("\n" + "=" * 70)
    print("FACTORY API DEMO (Statement-Based)")
    print("=" * 70)

    # Setup: Use BN254 curve (~128-bit security)
    group = PairingGroup('BN254')
    g = group.random(G1)
    x = group.random(ZR)
    h = g ** x

    print(f"\n[Setup] Statement: 'h = g^x'")

    # Method 1: Create proof instance directly
    print("\n--- Method 1: Direct Factory Creation ---")
    instance = ZKProofFactory.create_schnorr_proof(group, g, h, x)
    proof = instance.prove()
    is_valid = instance.verify(proof)
    print(f"[Result] Proof valid: {is_valid}")

    # Method 2: Create from statement string
    print("\n--- Method 2: From Statement String ---")
    instance2 = ZKProofFactory.create_from_statement(
        group,
        "h = g^x",
        public_params={'g': g, 'h': h},
        secret_params={'x': x}
    )
    proof2 = instance2.prove()
    is_valid2 = instance2.verify(proof2)
    print(f"[Result] Proof valid: {is_valid2}")

    return is_valid and is_valid2


# =============================================================================
# LEGACY API DEMO (Deprecated)
# =============================================================================

def legacy_network_demo(argv):
    """
    DEPRECATED: Legacy network demo using executeIntZKProof.

    WARNING: This function uses the deprecated API which relies on insecure
    dynamic code execution (exec/compile). Use the new SchnorrProof API instead.

    This is kept for backwards compatibility with existing deployments.
    """
    HOST, PORT = "", 8090
    party_info = {}

    if argv[1] == '-p':
        print("Operating as prover (LEGACY API)...")
        # WARNING: The legacy API will emit a DeprecationWarning
        prover_sock = socket(AF_INET, SOCK_STREAM)
        prover_sock.connect((HOST, PORT))
        prover_sock.settimeout(15)
        user = 'prover'
        party_info['socket'] = prover_sock
    elif argv[1] == '-v':
        print("Operating as verifier (LEGACY API)...")
        svr = socket(AF_INET, SOCK_STREAM)
        svr.bind((HOST, PORT))
        svr.listen(1)
        verifier_sock, addr = svr.accept()
        print("Connected by ", addr)
        user = 'verifier'
        party_info['socket'] = verifier_sock
    else:
        return False

    # DEPRECATED: Uses a.param file which may not be available
    # Use PairingGroup('BN254') for ~128-bit security (recommended)
    try:
        group = PairingGroup('a.param')
    except Exception:
        print("Warning: 'a.param' not found, using 'BN254' instead (~128-bit security)")
        group = PairingGroup('BN254')

    party_info['party'] = user
    party_info['setting'] = group

    # DEPRECATED STATEMENT FORMAT:
    # The legacy API uses string statements like '(h = g^x) and (j = g^y)'
    # This requires dynamic code generation which is a security risk.
    statement = '(h = g^x) and (j = g^y)'

    if user == 'prover':
        g = group.random(G1)
        x, y = group.random(ZR), group.random(ZR)
        pk = {'h': g ** x, 'g': g, 'j': g ** y}
        sk = {'x': x, 'y': y}

        # DEPRECATED: This function uses exec() internally
        # Migrate to: SchnorrProof.prove_non_interactive(group, g, h, x)
        result = executeIntZKProof(pk, sk, statement, party_info)
        print("Results for PROVER =>", result)

    elif user == 'verifier':
        # Verifier uses placeholder values since it doesn't know secrets
        pk = {'h': 1, 'g': 1, 'j': 1}
        sk = {'x': 1}

        # DEPRECATED: This function uses exec() internally
        # Migrate to: SchnorrProof.verify_non_interactive(group, g, h, proof)
        result = executeIntZKProof(pk, sk, statement, party_info)
        print("Results for VERIFIER =>", result)

    return True


# =============================================================================
# MAIN
# =============================================================================

def print_usage():
    """Print usage information."""
    print("""
Zero-Knowledge Proof Demo

Usage:
    python zk_demo.py [option]

Options:
    --demo-secure        Run non-interactive Schnorr proof demo (NEW API)
    --demo-interactive   Run interactive Schnorr proof demo (NEW API)
    --demo-serialization Run serialization demo (NEW API)
    --demo-factory       Run factory API demo (NEW API)
    --demo-all           Run all secure API demos

    -p                   Run as prover (LEGACY API - deprecated)
    -v                   Run as verifier (LEGACY API - deprecated)

    --help, -h           Show this help message

Examples:
    # Recommended: Use new secure API
    python zk_demo.py --demo-secure
    python zk_demo.py --demo-all

    # Legacy (deprecated): Network demo requires two terminals
    Terminal 1: python zk_demo.py -v
    Terminal 2: python zk_demo.py -p
""")


def main(argv):
    """Main entry point."""
    if len(argv) < 2:
        print_usage()
        return

    option = argv[1]

    if option in ['--help', '-h']:
        print_usage()

    elif option == '--demo-secure':
        demo_non_interactive_proof()
        print("\n✓ Non-interactive demo completed successfully!")

    elif option == '--demo-interactive':
        result = demo_interactive_proof()
        print(f"\n✓ Interactive demo completed: {'SUCCESS' if result else 'FAILED'}")

    elif option == '--demo-serialization':
        result = demo_serialization()
        print(f"\n✓ Serialization demo completed: {'SUCCESS' if result else 'FAILED'}")

    elif option == '--demo-factory':
        result = demo_factory_api()
        print(f"\n✓ Factory API demo completed: {'SUCCESS' if result else 'FAILED'}")

    elif option == '--demo-all':
        print("\n" + "#" * 70)
        print("# RUNNING ALL SECURE API DEMOS")
        print("#" * 70)

        demo_non_interactive_proof()
        demo_interactive_proof()
        demo_serialization()
        demo_factory_api()

        print("\n" + "#" * 70)
        print("# ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("#" * 70)
        print("\nThe new secure API is ready to use. See the migration guide above")
        print("for instructions on updating existing code.")

    elif option in ['-p', '-v']:
        # Legacy API - show deprecation notice
        print("\n" + "!" * 70)
        print("! WARNING: Using deprecated legacy API")
        print("! This API uses insecure dynamic code execution (exec/compile)")
        print("! Please migrate to the new secure API:")
        print("!   python zk_demo.py --demo-secure")
        print("!" * 70 + "\n")

        # Enable deprecation warnings to be visible
        warnings.filterwarnings('always', category=DeprecationWarning)

        legacy_network_demo(argv)

    else:
        print(f"Unknown option: {option}")
        print_usage()


if __name__ == "__main__":
    main(sys.argv)
