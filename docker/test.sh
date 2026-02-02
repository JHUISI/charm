#!/bin/bash
# Test script for running Charm-Crypto tests in Docker
# This mirrors the CI test execution

set -e

echo "================================================================================"
echo "Charm-Crypto Test Suite"
echo "================================================================================"
echo "Python version: $(python --version)"
echo "OpenSSL version: $(openssl version)"
echo "Working directory: $(pwd)"
echo "================================================================================"
echo ""

# Build Charm
echo "Building Charm..."
./configure.sh
make

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -e ".[dev]"

# Run tests with timeout
echo ""
echo "Running tests with pytest-timeout..."
echo "  - Per-test timeout: 30 seconds"
echo "  - Timeout method: thread"
echo "  - Ignoring: benchmark tests"
echo ""

# Run pytest with same options as CI
pytest -v \
    charm/test/ \
    --ignore=charm/test/benchmark/ \
    --timeout=30 \
    --timeout-method=thread \
    --tb=long \
    --junit-xml=test-results.xml \
    -x \
    "$@"

echo ""
echo "================================================================================"
echo "Tests completed!"
echo "================================================================================"

