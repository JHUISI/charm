Changes in v0.60
=======================

This release includes significant updates to dependencies, Python compatibility improvements, and new cryptographic schemes.

Dependency Updates
^^^^^^^^^^^^^^^^^^^^^^^^

- **PBC Library upgraded from 0.5.14 to 1.0.0** - The Pairing-Based Cryptography library has been updated to its latest release (June 2025). This is a drop-in replacement with no API changes, maintaining full backward compatibility with existing pairing-based schemes.
- Updated documentation and build scripts to reflect PBC 1.0.0 URLs and paths
- Updated CI/CD pipeline for PBC 1.0.0 builds

Python Compatibility
^^^^^^^^^^^^^^^^^^^^^^^^

- **Python 3.12+ support** - Fixed ``PyLongObject`` internal structure changes in Python 3.12+ (Issues #326, #313)
- Added ``PY_SSIZE_T_CLEAN`` macro definition for Python 3.10+ compatibility
- Fixed ``Py_SET_SIZE`` behavior changes in Python 3.12+
- Optimized ``longObjToMPZ`` by removing temporary variables
- Fixed ``PyLong_SHIFT`` definition for Windows 64-bit builds
- Added support for Python 3.11 and 3.12 in testing

New Schemes
^^^^^^^^^^^^^^^^^^^^^^^^

- **CP-ABE with Privacy Protection and Accountability** - Implemented CP hiding ABE scheme from "Attribute Based Encryption with Privacy Protection and Accountability for CloudIoT"
- **User Collusion Avoidance CP-ABE** - Implemented scheme with efficient attribute revocation for cloud storage
- **PS Signature Schemes** - Added Pointcheval-Sanders signature implementations
- **Certificateless Public Key Cryptography** - Added CLPKC scheme
- **Lamport OTS** - Implemented Lamport One-Time Signature scheme

Build System
^^^^^^^^^^^^^^^^^^^^^^^^

- Added GitHub Actions CI/CD workflow replacing Travis CI
- Updated ``configure.sh`` to support ARM64/AARCH64 architectures (Apple Silicon, etc.)
- Fixed multiple definition errors in benchmark module
- Improved Relic library integration

Bug Fixes
^^^^^^^^^^^^^^^^^^^^^^^^

- Fixed ``downcaseTokens`` function missing from ``policytree.py``
- Fixed ``coeff`` key handling in ``recoverCoefficients`` method
- Fixed integer hashing issues
- Improved EC bignum conversion
- Use ``math.gcd`` instead of deprecated ``fractions.gcd``
- Support all-AND policy expressions for testing ABE schemes
- Fixed AEC.c cipher mode issues with Python 3.10+

Documentation
^^^^^^^^^^^^^^^^^^^^^^^^

- Updated README with comprehensive Linux/Unix build instructions
- Added platform-specific installation guides for Ubuntu/Debian, Fedora/RHEL/CentOS, Arch Linux
- Updated links to point to jhuisi.github.io

Contributors
^^^^^^^^^^^^^^^^^^^^^^^^

Thanks to all contributors for this release, including bug fixes, new schemes, and compatibility improvements.

