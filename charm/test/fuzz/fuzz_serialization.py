#!/usr/bin/env python
"""
Fuzzing harness for serialization/deserialization in Charm

This fuzzer tests the deserialization functions with random byte inputs
to find crashes, memory corruption, or other issues.

Usage:
    pip install atheris
    python charm/test/fuzz/fuzz_serialization.py

Note: This file is not a pytest test module. It requires atheris to be installed
and should be run directly.
"""

import sys

# Defer atheris import to runtime to avoid pytest collection errors
atheris = None


def setup_module():
    """Import modules after Atheris initialization."""
    global PairingGroup, objectToBytes, bytesToObject
    from charm.toolbox.pairinggroup import PairingGroup
    from charm.core.engine.util import objectToBytes, bytesToObject


def fuzz_pairing_deserialization(data: bytes) -> None:
    """Fuzz target for pairing group deserialization.
    
    Tests bytesToObject with random bytes to find crashes.
    """
    try:
        group = PairingGroup('BN254')
        
        # Try to deserialize random bytes
        bytesToObject(data, group)
        
    except Exception:
        # Expected exceptions are fine
        pass


def fuzz_combined(data: bytes) -> None:
    """Combined fuzz target testing multiple deserialization paths."""
    fdp = atheris.FuzzedDataProvider(data)
    
    try:
        group = PairingGroup('BN254')
        
        # Get random bytes of varying lengths
        payload = fdp.ConsumeBytes(fdp.ConsumeIntInRange(0, 1024))
        
        # Try deserialization
        bytesToObject(payload, group)
        
    except Exception:
        pass


def main():
    """Main entry point."""
    global atheris

    try:
        import atheris as _atheris
        atheris = _atheris
    except ImportError:
        print("ERROR: atheris is required for fuzzing.")
        print("Install with: pip install atheris")
        sys.exit(1)

    atheris.instrument_all()
    setup_module()

    atheris.Setup(sys.argv, fuzz_combined)
    atheris.Fuzz()


if __name__ == "__main__":
    main()

