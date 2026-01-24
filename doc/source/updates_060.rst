Changes in v0.60
=======================

This release includes significant updates to dependencies, Python compatibility improvements, and new cryptographic schemes.

.. warning::

   This release contains **breaking changes**. Please review the migration guide below before upgrading.

Breaking Changes and Migration Guide
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This section documents changes that may require modifications to existing code when upgrading from v0.50 to v0.60.

Python Version Requirements
"""""""""""""""""""""""""""

**Python 2.x and Python 3.5-3.7 are no longer supported.**

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Aspect
     - Old (v0.50)
     - New (v0.60)
   * - Minimum Python
     - 2.7 / 3.x
     - **3.8+**
   * - Tested versions
     - 2.7, 3.5-3.9
     - 3.8, 3.9, 3.10, 3.11, 3.12

**Migration**: Upgrade to Python 3.8 or later before installing v0.60.

Package Name Change
"""""""""""""""""""

The PyPI package name has been updated to follow Python packaging conventions:

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Aspect
     - Old (v0.50)
     - New (v0.60)
   * - Package name
     - ``Charm-Crypto``
     - ``charm-crypto``
   * - Import name
     - ``charm``
     - ``charm`` (unchanged)

**Migration**: Update pip commands and requirements files::

    # Old
    pip install Charm-Crypto

    # New
    pip install charm-crypto

The import name remains ``charm``, so existing Python code continues to work without changes.

Dependency Version Changes
""""""""""""""""""""""""""

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - Dependency
     - Old (v0.50)
     - New (v0.60)
     - Impact
   * - PBC Library
     - 0.5.14
     - **1.0.0**
     - Low (API compatible)
   * - pyparsing
     - ``>=2.1.5,<2.4.1``
     - ``>=2.1.5,<4.0``
     - Low (more permissive)
   * - OpenSSL
     - 1.0.x / 1.1.x
     - **1.1.x / 3.x**
     - Medium

**OpenSSL Migration**: Ensure OpenSSL 1.1.0+ or 3.x is installed:

- macOS: ``brew install openssl@3``
- Ubuntu/Debian: ``apt install libssl-dev``
- Fedora/RHEL: ``dnf install openssl-devel``

Removed Features
""""""""""""""""

1. **Python 2.x support removed** - All Python 2 compatibility code has been removed from C extension modules.

2. **UninstallCommand removed** - The custom ``python setup.py uninstall`` command has been removed due to use of deprecated ``platform.linux_distribution()``.

   **Migration**: Use standard pip uninstall::

       pip uninstall charm-crypto

3. **distribute_setup.py removed** - The legacy setuptools bootstrap script has been removed.

   **Migration**: Use modern pip/setuptools::

       pip install --upgrade pip setuptools wheel
       pip install charm-crypto

CTR Counter Module Change
"""""""""""""""""""""""""

The low-level ``_counter`` module now returns ``bytes`` instead of ``str`` from counter operations.

**Impact**: Medium - Only affects code that directly uses the ``_counter`` module.

**Migration**: If you use the ``_counter`` module directly, ensure your code handles ``bytes`` objects::

    # The counter now returns bytes
    counter_value = counter()  # Returns bytes, not str

Most users access CTR mode through ``SymmetricCryptoAbstraction`` which handles this internally.

Internal Implementation Changes (Non-Breaking)
""""""""""""""""""""""""""""""""""""""""""""""

The following changes are internal and should not affect user code:

- Hash functions now use OpenSSL EVP API instead of deprecated low-level functions
- Windows PRNG seeding uses ``RAND_poll()`` instead of deprecated ``RAND_screen()``
- Integer module uses ``PyLong_*`` functions (Python 3 native) instead of ``PyInt_*``

Migration Checklist
"""""""""""""""""""

Before upgrading from v0.50 to v0.60:

1. ☐ Verify Python version is 3.8+: ``python --version``
2. ☐ Verify OpenSSL version is 1.1.0+: ``openssl version``
3. ☐ Update package name in requirements: ``Charm-Crypto`` → ``charm-crypto``
4. ☐ Remove any ``python setup.py uninstall`` usage (use ``pip uninstall``)
5. ☐ Check for direct ``_counter`` module usage (ensure code handles ``bytes``)
6. ☐ Rebuild from source if using custom builds

Dependency Updates
^^^^^^^^^^^^^^^^^^^^^^^^

- **PBC Library upgraded from 0.5.14 to 1.0.0** - The Pairing-Based Cryptography library has been updated to its latest release (June 2025). This is a drop-in replacement with no API changes, maintaining full backward compatibility with existing pairing-based schemes.
- Updated documentation and build scripts to reflect PBC 1.0.0 URLs and paths
- Updated CI/CD pipeline for PBC 1.0.0 builds
- **pyparsing constraint relaxed** - Now allows pyparsing 2.x and 3.x (``>=2.1.5,<4.0``)
- **OpenSSL 3.x support** - Full compatibility with OpenSSL 3.x across all C extension modules

Python Compatibility
^^^^^^^^^^^^^^^^^^^^^^^^

- **Python 3.8+ required** - Minimum Python version is now 3.8
- **Python 3.12+ support** - Fixed ``PyLongObject`` internal structure changes in Python 3.12+ (Issues #326, #313)
- Added ``PY_SSIZE_T_CLEAN`` macro definition for Python 3.10+ compatibility
- Fixed ``Py_SET_SIZE`` behavior changes in Python 3.12+
- Optimized ``longObjToMPZ`` by removing temporary variables
- Fixed ``PyLong_SHIFT`` definition for Windows 64-bit builds
- Added support for Python 3.11 and 3.12 in testing
- Modernized CTR counter module to use Python 3 Bytes API

New Schemes
^^^^^^^^^^^^^^^^^^^^^^^^

- **CP-ABE with Privacy Protection and Accountability** - Implemented CP hiding ABE scheme from "Attribute Based Encryption with Privacy Protection and Accountability for CloudIoT"
- **User Collusion Avoidance CP-ABE** - Implemented scheme with efficient attribute revocation for cloud storage
- **PS Signature Schemes** - Added Pointcheval-Sanders signature implementations
- **Certificateless Public Key Cryptography** - Added CLPKC scheme
- **Lamport OTS** - Implemented Lamport One-Time Signature scheme

Build System
^^^^^^^^^^^^^^^^^^^^^^^^

- **Modern Python packaging** - Added ``pyproject.toml`` following PEP 517/518 standards
- Added GitHub Actions CI/CD workflow replacing Travis CI
- Updated ``configure.sh`` to support ARM64/AARCH64 architectures (Apple Silicon, etc.)
- Updated ``configure.sh`` to detect Python 3.8-3.12
- Fixed multiple definition errors in benchmark module
- Improved Relic library integration
- Added type stubs (``.pyi`` files) for C extension modules

Bug Fixes
^^^^^^^^^^^^^^^^^^^^^^^^

- Fixed segmentation faults in EC and pairing modules (PY_SSIZE_T_CLEAN)
- Fixed ``downcaseTokens`` function missing from ``policytree.py``
- Fixed ``coeff`` key handling in ``recoverCoefficients`` method
- Fixed integer hashing issues
- Improved EC bignum conversion
- Use ``math.gcd`` instead of deprecated ``fractions.gcd``
- Support all-AND policy expressions for testing ABE schemes
- Fixed AEC.c cipher mode issues with Python 3.10+
- Removed deprecated ``platform.linux_distribution()`` usage

Documentation
^^^^^^^^^^^^^^^^^^^^^^^^

- Updated README with comprehensive Linux/Unix build instructions
- Added platform-specific installation guides for Ubuntu/Debian, Fedora/RHEL/CentOS, Arch Linux
- Updated links to point to jhuisi.github.io
- Added macOS tutorial for Apple Silicon

Contributors
^^^^^^^^^^^^^^^^^^^^^^^^

Thanks to all contributors for this release, including bug fixes, new schemes, and compatibility improvements.

