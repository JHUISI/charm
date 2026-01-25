"""
Thread-safe wrappers for ZKP proof classes.

This module provides thread-safe versions of the ZKP proof classes for use
in multi-threaded applications. The non-interactive proof methods are already
thread-safe (they use only local variables), but the interactive Prover and
Verifier classes maintain state that requires synchronization.

Thread Safety Analysis:
=======================

1. Non-Interactive Methods (ALREADY THREAD-SAFE):
   - SchnorrProof.prove_non_interactive()
   - SchnorrProof.verify_non_interactive()
   - DLEQProof.prove_non_interactive()
   - DLEQProof.verify_non_interactive()
   - RepresentationProof.prove_non_interactive()
   - RepresentationProof.verify_non_interactive()
   
   These methods use only local variables and class methods, so they are
   inherently thread-safe. Multiple threads can call them concurrently.

2. Interactive Classes (REQUIRE SYNCHRONIZATION):
   - SchnorrProof.Prover / SchnorrProof.Verifier
   - DLEQProof.Prover / DLEQProof.Verifier
   - RepresentationProof.Prover / RepresentationProof.Verifier
   
   These classes maintain internal state (_r, _c, etc.) that must not be
   accessed concurrently. Each thread should create its own Prover/Verifier
   instance, OR use the thread-safe wrappers provided here.

Usage:
    # For non-interactive proofs, just use the regular classes:
    proof = SchnorrProof.prove_non_interactive(group, g, h, x)  # Thread-safe
    
    # For interactive proofs in multi-threaded code, use thread-safe wrappers:
    prover = ThreadSafeProver(SchnorrProof.Prover(x, group))
    with prover:
        commitment = prover.create_commitment(g)
        response = prover.create_response(challenge)
"""

import threading
from contextlib import contextmanager
from functools import wraps


class ThreadSafeProver:
    """
    Thread-safe wrapper for interactive Prover classes.
    
    Wraps a Prover instance with a lock to ensure thread-safe access.
    Use as a context manager for automatic lock management.
    
    Example:
        prover = ThreadSafeProver(SchnorrProof.Prover(x, group))
        with prover:
            commitment = prover.create_commitment(g)
            response = prover.create_response(challenge)
    """
    
    def __init__(self, prover):
        """
        Initialize thread-safe prover wrapper.
        
        Args:
            prover: The underlying Prover instance to wrap
        """
        self._prover = prover
        self._lock = threading.RLock()
    
    def __enter__(self):
        """Acquire lock when entering context."""
        self._lock.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock when exiting context."""
        self._lock.release()
        return False
    
    def create_commitment(self, *args, **kwargs):
        """Thread-safe commitment creation."""
        with self._lock:
            return self._prover.create_commitment(*args, **kwargs)
    
    def create_response(self, *args, **kwargs):
        """Thread-safe response creation."""
        with self._lock:
            return self._prover.create_response(*args, **kwargs)


class ThreadSafeVerifier:
    """
    Thread-safe wrapper for interactive Verifier classes.
    
    Wraps a Verifier instance with a lock to ensure thread-safe access.
    Use as a context manager for automatic lock management.
    
    Example:
        verifier = ThreadSafeVerifier(SchnorrProof.Verifier(group))
        with verifier:
            challenge = verifier.create_challenge()
            result = verifier.verify(g, h, commitment, response)
    """
    
    def __init__(self, verifier):
        """
        Initialize thread-safe verifier wrapper.
        
        Args:
            verifier: The underlying Verifier instance to wrap
        """
        self._verifier = verifier
        self._lock = threading.RLock()
    
    def __enter__(self):
        """Acquire lock when entering context."""
        self._lock.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release lock when exiting context."""
        self._lock.release()
        return False
    
    def create_challenge(self, *args, **kwargs):
        """Thread-safe challenge creation."""
        with self._lock:
            return self._verifier.create_challenge(*args, **kwargs)
    
    def verify(self, *args, **kwargs):
        """Thread-safe verification."""
        with self._lock:
            return self._verifier.verify(*args, **kwargs)


def thread_safe_proof(func):
    """
    Decorator to make a proof function thread-safe.
    
    This is mainly for documentation purposes since the non-interactive
    proof methods are already thread-safe by design.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper._thread_safe = True
    return wrapper

