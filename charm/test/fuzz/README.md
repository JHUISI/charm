# Fuzzing Infrastructure for Charm-Crypto

This directory contains fuzzing harnesses for security testing using Atheris.

## Prerequisites

```bash
pip install atheris
```

## Running Fuzzers

### Policy Parser Fuzzer

Tests the ABE policy parser with random inputs:

```bash
# Run for 1 million iterations
python charm/test/fuzz/fuzz_policy_parser.py -max_total_time=3600

# Run with corpus
mkdir -p corpus/policy
python charm/test/fuzz/fuzz_policy_parser.py corpus/policy -max_total_time=3600
```

### Serialization Fuzzer

Tests deserialization with random bytes:

```bash
python charm/test/fuzz/fuzz_serialization.py -max_total_time=3600
```

## Crash Reproduction

If a crash is found, Atheris saves the input to a file. Reproduce with:

```bash
python charm/test/fuzz/fuzz_policy_parser.py crash-<hash>
```

## CI Integration

The fuzzing runs are not part of regular CI but should be run periodically:

```bash
# Run all fuzzers for 10 minutes each
for fuzzer in charm/test/fuzz/fuzz_*.py; do
    timeout 600 python $fuzzer -max_total_time=600 || true
done
```

