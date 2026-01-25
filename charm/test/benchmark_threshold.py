"""
Benchmark suite for DKLS23 Threshold ECDSA implementation.

Run with: python charm/test/benchmark_threshold.py

This module benchmarks:
- DKG (Distributed Key Generation)
- Presigning (Round 1 and Round 2 only - full protocol WIP)
- Signing (simulated with pre-computed values)
- Full threshold signing flow (DKG only - other phases WIP)

Note: Some benchmarks are limited as the full protocol implementation
is still in development.
"""

import time
import tracemalloc
from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.eccurve import secp256k1


def run_dkg(group, t, n, g):
    """
    Run DKG protocol and return key_shares, public_key.

    This function handles the tuple return from keygen_round3.
    """
    from charm.schemes.threshold.dkls23_dkg import DKLS23_DKG

    dkg = DKLS23_DKG(group, threshold=t, num_parties=n)

    # Round 1
    party_states = [dkg.keygen_round1(i + 1, g) for i in range(n)]
    round1_msgs = [s[0] for s in party_states]
    priv_states = [s[1] for s in party_states]

    # Round 2
    round2_results = [
        dkg.keygen_round2(i + 1, priv_states[i], round1_msgs) for i in range(n)
    ]
    shares_for_others = [r[0] for r in round2_results]
    states_r2 = [r[1] for r in round2_results]

    # Round 3 - keygen_round3 returns (KeyShare, complaint) tuple
    key_shares = {}
    for party_id in range(1, n + 1):
        received = {
            sender + 1: shares_for_others[sender][party_id] for sender in range(n)
        }
        ks, complaint = dkg.keygen_round3(
            party_id, states_r2[party_id - 1], received, round1_msgs
        )
        if complaint is not None:
            raise RuntimeError(f"DKG failed: {complaint}")
        key_shares[party_id] = ks

    public_key = key_shares[1].X
    return key_shares, public_key


def benchmark_dkg(t, n, iterations=10):
    """
    Benchmark Distributed Key Generation.

    Parameters
    ----------
    t : int
        Threshold value
    n : int
        Number of parties
    iterations : int
        Number of iterations to average over

    Returns
    -------
    float
        Average time in milliseconds
    """
    group = ECGroup(secp256k1)
    g = group.random(G)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        key_shares, public_key = run_dkg(group, t, n, g)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    return sum(times) / len(times)


def benchmark_presign(t, n, iterations=10):
    """
    Benchmark presigning rounds 1 and 2.

    Note: Round 3 is not included as the MtA integration is still in development.

    Parameters
    ----------
    t : int
        Threshold value
    n : int
        Number of parties
    iterations : int
        Number of iterations to average over

    Returns
    -------
    float
        Average time in milliseconds for rounds 1-2
    """
    from charm.schemes.threshold.dkls23_presign import DKLS23_Presign

    group = ECGroup(secp256k1)
    g = group.random(G)

    # Setup: generate key shares first
    key_shares, _ = run_dkg(group, t, n, g)
    participants = list(range(1, t + 1))

    times = []
    for _ in range(iterations):
        presign = DKLS23_Presign(group)

        start = time.perf_counter()

        # Round 1
        r1 = {}
        st = {}
        for pid in participants:
            msg, s = presign.presign_round1(pid, key_shares[pid].x_i, participants, g)
            r1[pid], st[pid] = msg, s

        # Round 2
        for pid in participants:
            b, m, s = presign.presign_round2(pid, st[pid], r1)

        end = time.perf_counter()
        times.append((end - start) * 1000)

    return sum(times) / len(times)


def benchmark_sign(t, n, iterations=10):
    """
    Benchmark signing operation (simulated).

    This benchmarks the signing computation with pre-computed values,
    as the full presigning flow is still in development.

    Parameters
    ----------
    t : int
        Threshold value
    n : int
        Number of parties
    iterations : int
        Number of iterations to average over

    Returns
    -------
    float
        Average time in milliseconds
    """
    from charm.schemes.threshold.dkls23_sign import DKLS23_Sign

    group = ECGroup(secp256k1)
    g = group.random(G)
    signer = DKLS23_Sign(group)

    # Simulate signature computation timing
    # (actual full flow requires working presigning)
    message = b"Benchmark signing message"

    times = []
    for _ in range(iterations):
        # Generate simulated values
        k = group.random(ZR)
        x = group.random(ZR)
        R = g**k
        r = group.zr(R)

        start = time.perf_counter()
        # Simulate signature computation
        e = signer._hash_message(message)
        s = (e + r * x) * (k ** (-1))
        end = time.perf_counter()
        times.append((end - start) * 1000)

    return sum(times) / len(times)


def benchmark_full_flow(t, n, num_signatures=5):
    """
    Benchmark complete DKG flow with memory usage tracking.

    Note: Only DKG is fully benchmarked; presigning/signing are placeholders
    until the full protocol is integrated.

    Parameters
    ----------
    t : int
        Threshold value
    n : int
        Number of parties
    num_signatures : int
        Number of DKG runs to measure

    Returns
    -------
    tuple
        (total_time_ms, peak_memory_kb, avg_per_dkg_ms)
    """
    group = ECGroup(secp256k1)
    g = group.random(G)

    tracemalloc.start()
    start = time.perf_counter()

    # Run DKG multiple times to measure memory and performance
    for i in range(num_signatures):
        key_shares, public_key = run_dkg(group, t, n, g)

    end = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    total_ms = (end - start) * 1000
    peak_kb = peak / 1024
    avg_per_run = total_ms / num_signatures

    return total_ms, peak_kb, avg_per_run


def run_benchmarks(t=2, n=3):
    """Run all benchmarks and print formatted results."""
    print(f"\nDKLS23 Threshold ECDSA Benchmarks ({t}-of-{n})")
    print("=" * 50)

    # Run individual benchmarks
    dkg_time = benchmark_dkg(t, n, iterations=10)
    print(f"DKG:      {dkg_time:6.1f} ms (avg over 10 runs)")

    presign_time = benchmark_presign(t, n, iterations=10)
    print(f"Presign:  {presign_time:6.1f} ms (avg over 10 runs, rounds 1-2)")

    sign_time = benchmark_sign(t, n, iterations=10)
    print(f"Sign:     {sign_time:6.1f} ms (avg over 10 runs, simulated)")

    # Full flow benchmark
    total_time, peak_mem, avg_per_run = benchmark_full_flow(t, n, num_signatures=5)
    print(f"Full flow: {total_time:6.1f} ms total (5 DKG runs)")
    print(f"Peak memory: {peak_mem:6.1f} KB")
    print(f"Avg per DKG: {avg_per_run:6.1f} ms")
    print("=" * 50)


if __name__ == "__main__":
    run_benchmarks(t=2, n=3)

