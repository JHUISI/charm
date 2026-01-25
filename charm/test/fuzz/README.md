# Fuzzing Infrastructure for Charm-Crypto

This directory contains fuzzing harnesses for security testing using Atheris.

## Prerequisites

### Linux (Recommended)

```bash
pip install atheris
```

### macOS

Atheris requires LLVM's libFuzzer, which is not included with Apple Clang.
You have two options:

**Option 1: Use Homebrew LLVM**
```bash
brew install llvm
export CLANG_BIN=/opt/homebrew/opt/llvm/bin/clang
export CC=/opt/homebrew/opt/llvm/bin/clang
export CXX=/opt/homebrew/opt/llvm/bin/clang++
pip install atheris
```

**Option 2: Use Docker**
```bash
docker run -it --rm -v $(pwd):/charm python:3.11 bash
cd /charm
pip install atheris pytest pyparsing hypothesis
python charm/test/fuzz/fuzz_policy_parser.py -max_total_time=600
```

**Option 3: Rely on CI**
Fuzzing runs automatically in GitHub Actions on Linux. See the `fuzzing` job
in `.github/workflows/ci.yml`.

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

Fuzzing runs automatically in GitHub Actions CI on a weekly schedule (Sundays at 2am UTC)
or when manually triggered via `workflow_dispatch`. The `fuzzing` job in `.github/workflows/ci.yml`:

- Runs each fuzzer for ~5 minutes (300 seconds)
- Uploads any crash artifacts for investigation
- Uses Linux where Atheris works out of the box
- Does NOT run on every push/PR to save CI resources

To run locally for longer periods:

```bash
# Run all fuzzers for 10 minutes each
for fuzzer in charm/test/fuzz/fuzz_*.py; do
    timeout 600 python $fuzzer -max_total_time=600 || true
done
```

