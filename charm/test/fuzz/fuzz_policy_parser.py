#!/usr/bin/env python
"""
Fuzzing harness for PolicyParser in charm.toolbox.policytree

This fuzzer tests the policy parser with random inputs to find crashes,
hangs, or other unexpected behavior.

Usage:
    pip install atheris
    python charm/test/fuzz/fuzz_policy_parser.py

The fuzzer will run continuously until stopped (Ctrl+C) or a crash is found.

Note: This file is not a pytest test module. It requires atheris to be installed
and should be run directly.
"""

import sys

# Defer atheris import to runtime to avoid pytest collection errors
atheris = None


def setup_module():
    """Import modules after Atheris initialization for proper instrumentation."""
    global PolicyParser
    from charm.toolbox.policytree import PolicyParser


def fuzz_policy_parser(data: bytes) -> None:
    """Fuzz target for PolicyParser.
    
    Tests the parser with random byte strings converted to policy strings.
    """
    try:
        # Convert bytes to string, handling encoding errors gracefully
        policy_str = data.decode('utf-8', errors='replace')
        
        # Skip empty strings
        if not policy_str.strip():
            return
            
        # Parse the policy string
        parser = PolicyParser()
        parser.parse(policy_str)
        
    except Exception:
        # Expected exceptions from invalid input are fine
        # We're looking for crashes, hangs, or memory issues
        pass


def main():
    """Main entry point for the fuzzer."""
    global atheris

    try:
        import atheris as _atheris
        atheris = _atheris
    except ImportError:
        print("ERROR: atheris is required for fuzzing.")
        print("Install with: pip install atheris")
        sys.exit(1)

    # Initialize Atheris with instrumentation
    atheris.instrument_all()
    setup_module()

    # Start fuzzing
    atheris.Setup(sys.argv, fuzz_policy_parser)
    atheris.Fuzz()


if __name__ == "__main__":
    main()

