#!/bin/bash
# Debug script for investigating hanging tests
# Usage: ./docker/debug-test.sh [test_name]

set -e

TEST_NAME="${1:-}"

echo "================================================================================"
echo "Charm-Crypto Test Debugger"
echo "================================================================================"
echo "Python version: $(python --version)"
echo "OpenSSL version: $(openssl version)"
echo ""

# Build Charm if not already built
if [ ! -f "charm/core/math/pairing/relic/relicmodule.so" ]; then
    echo "Building Charm..."
    ./configure.sh
    make
fi

# Install dependencies if needed
if ! python -c "import pytest" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -e ".[dev]"
fi

echo ""
echo "================================================================================"
echo "Debugging Options:"
echo "================================================================================"
echo ""
echo "1. Run with verbose output and short timeout (10s)"
echo "2. Run with strace to trace system calls"
echo "3. Run with gdb for C-level debugging"
echo "4. Run with Python debugger (pdb)"
echo "5. Run with memory profiling (valgrind)"
echo "6. Run normally with 30s timeout"
echo ""

if [ -z "$TEST_NAME" ]; then
    echo "No test name provided. Running all tests with verbose output..."
    OPTION=1
else
    read -p "Select option (1-6): " OPTION
fi

case $OPTION in
    1)
        echo ""
        echo "Running with verbose output and 10s timeout..."
        pytest -vvs \
            ${TEST_NAME:+charm/test/ -k "$TEST_NAME"} \
            ${TEST_NAME:-charm/test/} \
            --timeout=10 \
            --timeout-method=thread \
            --tb=long \
            -x
        ;;
    2)
        echo ""
        echo "Running with strace (system call tracing)..."
        echo "Output will be saved to strace.log"
        strace -f -o strace.log \
            pytest -v \
            ${TEST_NAME:+charm/test/ -k "$TEST_NAME"} \
            ${TEST_NAME:-charm/test/} \
            --timeout=30 \
            --timeout-method=thread \
            -x
        echo ""
        echo "Strace log saved to strace.log"
        echo "To analyze: grep -E '(hang|block|wait|futex)' strace.log"
        ;;
    3)
        echo ""
        echo "Running with gdb (C debugger)..."
        echo "Commands:"
        echo "  - 'run' to start"
        echo "  - 'bt' for backtrace when hung"
        echo "  - 'thread apply all bt' for all thread backtraces"
        echo "  - 'Ctrl+C' to interrupt if hung"
        gdb --args python -m pytest -v \
            ${TEST_NAME:+charm/test/ -k "$TEST_NAME"} \
            ${TEST_NAME:-charm/test/} \
            --timeout=30 \
            --timeout-method=thread \
            -x
        ;;
    4)
        echo ""
        echo "Running with Python debugger (pdb)..."
        pytest -v \
            ${TEST_NAME:+charm/test/ -k "$TEST_NAME"} \
            ${TEST_NAME:-charm/test/} \
            --pdb \
            --timeout=30 \
            --timeout-method=thread \
            -x
        ;;
    5)
        echo ""
        echo "Running with valgrind (memory profiling)..."
        echo "This will be VERY slow..."
        valgrind \
            --leak-check=full \
            --show-leak-kinds=all \
            --track-origins=yes \
            --verbose \
            --log-file=valgrind.log \
            python -m pytest -v \
            ${TEST_NAME:+charm/test/ -k "$TEST_NAME"} \
            ${TEST_NAME:-charm/test/} \
            -x
        echo ""
        echo "Valgrind log saved to valgrind.log"
        ;;
    6)
        echo ""
        echo "Running normally with 30s timeout..."
        pytest -v \
            ${TEST_NAME:+charm/test/ -k "$TEST_NAME"} \
            ${TEST_NAME:-charm/test/} \
            --timeout=30 \
            --timeout-method=thread \
            --tb=long \
            -x
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "================================================================================"
echo "Debugging session completed!"
echo "================================================================================"

