#!/bin/bash
# Build script for Charm-Crypto in Docker
# This mirrors the CI build process

set -e

echo "================================================================================"
echo "Building Charm-Crypto"
echo "================================================================================"
echo "Python version: $(python --version)"
echo "GCC version: $(gcc --version | head -n1)"
echo "OpenSSL version: $(openssl version)"
echo "================================================================================"
echo ""

# Clean previous build
echo "Cleaning previous build..."
make clean 2>/dev/null || true
rm -rf build/ dist/ *.egg-info

# Configure
echo ""
echo "Configuring..."
./configure.sh

# Build
echo ""
echo "Building C extensions..."
make

# Install in development mode
echo ""
echo "Installing in development mode..."
pip install -e ".[dev]"

# Verify installation
echo ""
echo "Verifying installation..."
python -c "from charm.toolbox.pairinggroup import PairingGroup; print('✅ Pairing module OK')"
python -c "from charm.toolbox.integergroup import IntegerGroup; print('✅ Integer module OK')"
python -c "from charm.toolbox.ecgroup import ECGroup; print('✅ EC module OK')"

echo ""
echo "================================================================================"
echo "Build completed successfully!"
echo "================================================================================"

