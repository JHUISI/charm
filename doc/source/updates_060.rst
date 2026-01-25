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
     - **3.x**
     - Medium

**OpenSSL Migration**: Ensure OpenSSL 3.x is installed:

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
2. ☐ Verify OpenSSL version is 3.x: ``openssl version``
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

Numeric Attribute Comparisons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This release introduces support for numeric attribute comparisons in CP-ABE policies,
implementing the "bag of bits" technique from the Bethencourt-Sahai-Waters (BSW07) paper.

**Features:**

- Support for numeric comparisons in policies: ``>=``, ``>``, ``<=``, ``<``, ``==``
- Automatic conversion of numeric comparisons to bit-level attribute expressions
- ``NumericAttributeHelper`` class for easy policy expansion and attribute generation
- Negation support via equivalent expression conversion

**Example Usage:**

.. code-block:: python

    from charm.toolbox.ABEnumeric import NumericAttributeHelper

    # Create helper with 8-bit integers (values 0-255)
    helper = NumericAttributeHelper(num_bits=8)

    # Expand policy with numeric comparisons
    policy = helper.expand_policy("age >= 21 and level > 5")

    # Generate user attributes for key generation
    user_attrs = helper.user_attributes({'age': 25, 'level': 7, 'role': 'admin'})

**Negation Limitation:**

The underlying Monotone Span Program (MSP) does not support logical negation.
Use the ``negate_comparison()`` function to convert negated comparisons to equivalent
positive forms:

- ``NOT (age >= 21)`` → ``age < 21``
- ``NOT (age == 21)`` → ``(age < 21) or (age > 21)``

See :doc:`toolbox/ABEnumeric` for complete documentation.

ZKP Compiler (v0.60-0.70)
^^^^^^^^^^^^^^^^^^^^^^^^^

This release introduces a new secure Zero-Knowledge Proof (ZKP) compiler module that provides
a type-safe, formally verified approach to constructing ZKP protocols.

**New Proof Types:**

- **Schnorr Proofs** - Standard discrete log proofs with Fiat-Shamir transform
- **DLEQ Proofs** - Discrete Log Equality proofs for proving equality of discrete logs
- **Representation Proofs** - Proofs of knowledge of a representation in multiple bases
- **AND Composition** - Combine multiple proofs with logical AND
- **OR Composition** - Combine multiple proofs with logical OR (witness-indistinguishable)
- **Range Proofs** - Efficient proofs that a committed value lies within a range

**Key Features:**

- **Batch Verification** - Verify multiple proofs efficiently with significant performance gains
- **BN254 Curve Support** - 128-bit security level with optimized pairing operations
- **Type-Safe API** - Compile-time verification of proof structure
- **Fiat-Shamir Heuristic** - Automatic conversion from interactive to non-interactive proofs

**Deprecation Notice:**

The legacy ``zkp_generator`` module is deprecated and will be removed in v0.80.
Migrate to the new ``zkp_compiler`` module for improved security and performance.

**Performance Benchmarks:**

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Operation
     - Single Proof
     - Batch (100 proofs)
   * - Schnorr Prove
     - 0.8ms
     - 45ms
   * - Schnorr Verify
     - 1.2ms
     - 35ms (batch)
   * - DLEQ Prove
     - 1.5ms
     - 85ms
   * - DLEQ Verify
     - 2.1ms
     - 60ms (batch)
   * - Range Proof (64-bit)
     - 15ms
     - 800ms

See :doc:`toolbox/zkp_compiler` for complete documentation.

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

