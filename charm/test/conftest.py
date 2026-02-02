"""
Pytest configuration for Charm test suite.

This module provides custom pytest hooks and fixtures for version-specific
test skipping and other test configuration.
"""

import sys
import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "skip_py312plus: Skip test on Python 3.12+ due to known issues"
    )
    config.addinivalue_line(
        "markers",
        "slow: Mark test as slow-running"
    )


def pytest_collection_modifyitems(config, items):
    """
    Automatically skip tests marked with skip_py312plus on Python 3.12+.
    
    This hook runs after test collection and modifies the test items
    to add skip markers based on the Python version.
    """
    if sys.version_info >= (3, 12):
        skip_py312plus = pytest.mark.skip(
            reason="Test skipped on Python 3.12+ due to known hanging/compatibility issues"
        )
        for item in items:
            if "skip_py312plus" in item.keywords:
                item.add_marker(skip_py312plus)

