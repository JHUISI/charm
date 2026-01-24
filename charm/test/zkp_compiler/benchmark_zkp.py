"""
Performance benchmarks for ZKP compiler.

Compares proof generation and verification times across different curves:
- BN254 (128-bit security, recommended)
- SS512 (80-bit security, legacy)
- MNT224 (112-bit security)

Run with: python -m charm.test.zkp_compiler.benchmark_zkp
"""

import time
import statistics
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1

from charm.zkp_compiler.schnorr_proof import SchnorrProof
from charm.zkp_compiler.dleq_proof import DLEQProof
from charm.zkp_compiler.representation_proof import RepresentationProof
from charm.zkp_compiler.and_proof import ANDProof
from charm.zkp_compiler.or_proof import ORProof
from charm.zkp_compiler.range_proof import RangeProof


CURVES = ['BN254', 'SS512', 'MNT224']
ITERATIONS = 10


def benchmark_schnorr(group, iterations=ITERATIONS):
    """Benchmark Schnorr proof."""
    g = group.random(G1)
    x = group.random(ZR)
    h = g ** x

    prove_times = []
    verify_times = []

    for _ in range(iterations):
        start = time.perf_counter()
        proof = SchnorrProof.prove_non_interactive(group, g, h, x)
        prove_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        SchnorrProof.verify_non_interactive(group, g, h, proof)
        verify_times.append(time.perf_counter() - start)

    return {
        'prove_mean': statistics.mean(prove_times) * 1000,
        'prove_std': statistics.stdev(prove_times) * 1000 if len(prove_times) > 1 else 0,
        'verify_mean': statistics.mean(verify_times) * 1000,
        'verify_std': statistics.stdev(verify_times) * 1000 if len(verify_times) > 1 else 0,
    }


def benchmark_dleq(group, iterations=ITERATIONS):
    """Benchmark DLEQ proof."""
    g1 = group.random(G1)
    g2 = group.random(G1)
    x = group.random(ZR)
    h1 = g1 ** x
    h2 = g2 ** x

    prove_times = []
    verify_times = []

    for _ in range(iterations):
        start = time.perf_counter()
        proof = DLEQProof.prove_non_interactive(group, g1, h1, g2, h2, x)
        prove_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        DLEQProof.verify_non_interactive(group, g1, h1, g2, h2, proof)
        verify_times.append(time.perf_counter() - start)

    return {
        'prove_mean': statistics.mean(prove_times) * 1000,
        'prove_std': statistics.stdev(prove_times) * 1000 if len(prove_times) > 1 else 0,
        'verify_mean': statistics.mean(verify_times) * 1000,
        'verify_std': statistics.stdev(verify_times) * 1000 if len(verify_times) > 1 else 0,
    }


def benchmark_representation(group, iterations=ITERATIONS):
    """Benchmark Representation proof."""
    g1, g2 = group.random(G1), group.random(G1)
    x1, x2 = group.random(ZR), group.random(ZR)
    h = (g1 ** x1) * (g2 ** x2)
    generators = [g1, g2]
    witnesses = [x1, x2]

    prove_times = []
    verify_times = []

    for _ in range(iterations):
        start = time.perf_counter()
        proof = RepresentationProof.prove_non_interactive(group, generators, h, witnesses)
        prove_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        RepresentationProof.verify_non_interactive(group, generators, h, proof)
        verify_times.append(time.perf_counter() - start)

    return {
        'prove_mean': statistics.mean(prove_times) * 1000,
        'prove_std': statistics.stdev(prove_times) * 1000 if len(prove_times) > 1 else 0,
        'verify_mean': statistics.mean(verify_times) * 1000,
        'verify_std': statistics.stdev(verify_times) * 1000 if len(verify_times) > 1 else 0,
    }


def benchmark_and(group, iterations=ITERATIONS):
    """Benchmark AND proof."""
    g = group.random(G1)
    x, y = group.random(ZR), group.random(ZR)
    h1, h2 = g ** x, g ** y

    statements = [
        {'type': 'schnorr', 'params': {'g': g, 'h': h1, 'x': x}},
        {'type': 'schnorr', 'params': {'g': g, 'h': h2, 'x': y}},
    ]
    statements_public = [
        {'type': 'schnorr', 'params': {'g': g, 'h': h1}},
        {'type': 'schnorr', 'params': {'g': g, 'h': h2}},
    ]

    prove_times = []
    verify_times = []

    for _ in range(iterations):
        start = time.perf_counter()
        proof = ANDProof.prove_non_interactive(group, statements)
        prove_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        ANDProof.verify_non_interactive(group, statements_public, proof)
        verify_times.append(time.perf_counter() - start)

    return {
        'prove_mean': statistics.mean(prove_times) * 1000,
        'prove_std': statistics.stdev(prove_times) * 1000 if len(prove_times) > 1 else 0,
        'verify_mean': statistics.mean(verify_times) * 1000,
        'verify_std': statistics.stdev(verify_times) * 1000 if len(verify_times) > 1 else 0,
    }



def benchmark_or(group, iterations=ITERATIONS):
    """Benchmark OR proof."""
    g = group.random(G1)
    x = group.random(ZR)
    h1 = g ** x  # Prover knows DL of h1
    h2 = g ** group.random(ZR)  # Prover does NOT know DL of h2

    prove_times = []
    verify_times = []

    for _ in range(iterations):
        start = time.perf_counter()
        proof = ORProof.prove_non_interactive(group, g, h1, h2, x, which=0)
        prove_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        ORProof.verify_non_interactive(group, g, h1, h2, proof)
        verify_times.append(time.perf_counter() - start)

    return {
        'prove_mean': statistics.mean(prove_times) * 1000,
        'prove_std': statistics.stdev(prove_times) * 1000 if len(prove_times) > 1 else 0,
        'verify_mean': statistics.mean(verify_times) * 1000,
        'verify_std': statistics.stdev(verify_times) * 1000 if len(verify_times) > 1 else 0,
    }


def benchmark_range(group, iterations=ITERATIONS):
    """Benchmark Range proof."""
    g, h = group.random(G1), group.random(G1)
    value = 42
    randomness = group.random(ZR)
    commitment = RangeProof.create_pedersen_commitment(group, g, h, value, randomness)

    prove_times = []
    verify_times = []

    for _ in range(iterations):
        start = time.perf_counter()
        proof = RangeProof.prove(group, g, h, value, randomness, num_bits=8)
        prove_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        RangeProof.verify(group, g, h, commitment, proof)
        verify_times.append(time.perf_counter() - start)

    return {
        'prove_mean': statistics.mean(prove_times) * 1000,
        'prove_std': statistics.stdev(prove_times) * 1000 if len(prove_times) > 1 else 0,
        'verify_mean': statistics.mean(verify_times) * 1000,
        'verify_std': statistics.stdev(verify_times) * 1000 if len(verify_times) > 1 else 0,
    }


def run_benchmarks():
    """Run all benchmarks and print results."""
    print("=" * 80)
    print("ZKP Compiler Performance Benchmarks")
    print("=" * 80)
    print(f"Iterations per test: {ITERATIONS}")
    print()

    results = {}

    for curve in CURVES:
        print(f"Benchmarking {curve}...")
        group = PairingGroup(curve)
        results[curve] = {
            'schnorr': benchmark_schnorr(group),
            'dleq': benchmark_dleq(group),
            'representation': benchmark_representation(group),
            'and': benchmark_and(group),
            'or': benchmark_or(group),
            'range': benchmark_range(group),
        }

    print()
    print_results_table(results)


def print_results_table(results):
    """Print formatted results table."""
    proof_types = ['schnorr', 'dleq', 'representation', 'and', 'or', 'range']

    # Header
    print("=" * 100)
    print(f"{'Proof Type':<16} {'Curve':<10} {'Prove (ms)':<20} {'Verify (ms)':<20}")
    print("=" * 100)

    for proof_type in proof_types:
        for i, curve in enumerate(CURVES):
            data = results[curve][proof_type]
            prove_str = f"{data['prove_mean']:>8.3f} ± {data['prove_std']:<6.3f}"
            verify_str = f"{data['verify_mean']:>8.3f} ± {data['verify_std']:<6.3f}"

            if i == 0:
                print(f"{proof_type:<16} {curve:<10} {prove_str:<20} {verify_str:<20}")
            else:
                print(f"{'':<16} {curve:<10} {prove_str:<20} {verify_str:<20}")
        print("-" * 100)

    # Summary: fastest curve per proof type
    print()
    print("Summary: Fastest Curve per Proof Type")
    print("-" * 50)
    for proof_type in proof_types:
        best_prove = min(CURVES, key=lambda c: results[c][proof_type]['prove_mean'])
        best_verify = min(CURVES, key=lambda c: results[c][proof_type]['verify_mean'])
        print(f"{proof_type:<16} Prove: {best_prove:<10} Verify: {best_verify:<10}")


if __name__ == '__main__':
    run_benchmarks()