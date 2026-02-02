# Docker Testing Environment for Charm-Crypto

This directory contains Docker-based testing infrastructure for debugging Python 3.12+ hanging issues locally without waiting for GitHub Actions CI.

## 🎯 Purpose

The Docker environment:
- **Mirrors the CI environment** (Ubuntu 22.04, same dependencies)
- **Supports Python 3.11, 3.12, 3.13, 3.14**
- **Includes debugging tools** (gdb, strace, valgrind)
- **Enables fast iteration** (mount local source code)
- **Identifies hanging tests** (pytest-timeout plugin)

## 📋 Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually included with Docker Desktop)
- At least 4GB free disk space

## 🚀 Quick Start

### 1. Build Docker Images

```bash
# Build all Python versions (3.12, 3.13)
docker-compose -f docker-compose.test.yml build

# Or build specific version
docker-compose -f docker-compose.test.yml build py313
```

### 2. Run Tests

```bash
# Run full test suite on Python 3.13
docker-compose -f docker-compose.test.yml run --rm py313 ./docker/test.sh

# Run full test suite on Python 3.12
docker-compose -f docker-compose.test.yml run --rm py312 ./docker/test.sh

# Run with baseline Python 3.11 for comparison
docker-compose -f docker-compose.test.yml --profile baseline run --rm py311 ./docker/test.sh
```

### 3. Interactive Shell

```bash
# Get interactive shell in Python 3.13 environment
docker-compose -f docker-compose.test.yml run --rm py313

# Inside container, you can:
./configure.sh && make              # Build Charm
pip install -e ".[dev]"             # Install dependencies
pytest charm/test/ -v               # Run tests
python                              # Start Python REPL
```

## 🔍 Debugging Hanging Tests

### Method 1: Interactive Debug Script

```bash
# Run interactive debugger
docker-compose -f docker-compose.test.yml run --rm py313 ./docker/debug-test.sh

# Or debug specific test
docker-compose -f docker-compose.test.yml run --rm py313 ./docker/debug-test.sh "test_name"
```

The debug script offers 6 options:
1. **Verbose output** with 10s timeout (quick identification)
2. **strace** - trace system calls to find blocking operations
3. **gdb** - C-level debugging with breakpoints
4. **pdb** - Python debugger for stepping through code
5. **valgrind** - memory profiling and leak detection
6. **Normal** - standard pytest with 30s timeout

### Method 2: Manual Debugging

```bash
# Enter container
docker-compose -f docker-compose.test.yml run --rm py313 bash

# Build Charm
./docker/build.sh

# Run specific test with verbose output
pytest -vvs charm/test/schemes/abenc/abenc_bsw07_test.py --timeout=10

# Run with strace to see system calls
strace -f -o strace.log pytest charm/test/schemes/abenc/abenc_bsw07_test.py

# Analyze strace output
grep -E '(futex|wait|poll|select)' strace.log | tail -20
```

### Method 3: GDB for C Extension Debugging

```bash
# Enter container
docker-compose -f docker-compose.test.yml run --rm py313 bash

# Build with debug symbols
./configure.sh
make clean && make CFLAGS="-g -O0"

# Run test under gdb
gdb --args python -m pytest charm/test/schemes/abenc/abenc_bsw07_test.py -v

# In gdb:
(gdb) run                          # Start test
# When it hangs, press Ctrl+C
(gdb) thread apply all bt          # Show all thread backtraces
(gdb) info threads                 # List all threads
(gdb) thread 2                     # Switch to thread 2
(gdb) bt                           # Backtrace for current thread
```

## 📊 Common Debugging Scenarios

### Scenario 1: Identify Which Test Hangs

```bash
docker-compose -f docker-compose.test.yml run --rm py313 bash
./docker/build.sh
pytest charm/test/ -v --timeout=10 --timeout-method=thread -x
```

The `-x` flag stops at first failure/timeout, showing exactly which test hangs.

### Scenario 2: Compare Python 3.11 vs 3.13

```bash
# Run on Python 3.11 (baseline)
docker-compose -f docker-compose.test.yml --profile baseline run --rm py311 ./docker/test.sh

# Run on Python 3.13 (problematic)
docker-compose -f docker-compose.test.yml run --rm py313 ./docker/test.sh

# Compare results
```

### Scenario 3: Trace System Calls During Hang

```bash
docker-compose -f docker-compose.test.yml run --rm py313 bash
./docker/build.sh

# Run with strace
strace -f -tt -o strace.log pytest charm/test/schemes/abenc/abenc_bsw07_test.py --timeout=30

# Analyze last operations before hang
tail -100 strace.log

# Look for blocking calls
grep -E '(futex|wait|poll|select|read|write).*<unfinished>' strace.log
```

## 🛠️ Helper Scripts

| Script | Purpose |
|--------|---------|
| `docker/build.sh` | Build Charm (mirrors CI build) |
| `docker/test.sh` | Run full test suite (mirrors CI tests) |
| `docker/debug-test.sh` | Interactive debugging menu |

## 📁 File Structure

```
charm/
├── Dockerfile.test              # Docker image definition
├── docker-compose.test.yml      # Multi-version orchestration
└── docker/
    ├── README.md                # This file
    ├── build.sh                 # Build script
    ├── test.sh                  # Test script
    └── debug-test.sh            # Debug script
```

## 💡 Tips

1. **Source code is mounted** - changes to local files are immediately reflected in container
2. **Rebuild after dependency changes** - if you modify `pyproject.toml`, rebuild the image
3. **Use `-x` flag** - stops at first failure for faster debugging
4. **Check container logs** - `docker-compose logs py313`
5. **Clean up** - `docker-compose -f docker-compose.test.yml down -v`

## 🐛 Known Issues

### Issue: "Permission denied" on scripts
```bash
chmod +x docker/*.sh
```

### Issue: Container exits immediately
```bash
# Use interactive mode
docker-compose -f docker-compose.test.yml run --rm py313 bash
```

### Issue: Build fails with "PBC not found"
```bash
# Rebuild image from scratch
docker-compose -f docker-compose.test.yml build --no-cache py313
```

## 📚 Additional Resources

- [pytest-timeout documentation](https://pypi.org/project/pytest-timeout/)
- [GDB Python debugging](https://wiki.python.org/moin/DebuggingWithGdb)
- [strace tutorial](https://strace.io/)
- [Valgrind manual](https://valgrind.org/docs/manual/manual.html)

