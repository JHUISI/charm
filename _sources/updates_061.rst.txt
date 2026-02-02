Changes in v0.61
=======================

This release adds full Python 3.13 and 3.14 support with fixes for removed private APIs.

Python 3.13 Compatibility
^^^^^^^^^^^^^^^^^^^^^^^^^

Python 3.13 removed several private CPython APIs that Charm was using. This release updates
all C extension modules to use the public APIs:

**Fixed Private API Removals:**

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Issue
     - Old API (Removed)
     - New API (Python 3.13+)
   * - Interpreter finalization check
     - ``_Py_IsFinalizing()``
     - ``Py_IsFinalizing()``
   * - Integer to string conversion
     - ``_PyLong_Format()``
     - ``PyObject_Str()``
   * - Unicode string access
     - ``PyUnicode_DATA()``
     - ``PyUnicode_AsUTF8()``

**Technical Details:**

The ``_Py_IsFinalizing()`` function was a private API that checked if the Python interpreter
was shutting down. In Python 3.13, this was replaced with the public ``Py_IsFinalizing()`` API.
The fix adds a compatibility macro (``CHARM_PY_IS_FINALIZING()``) that uses the appropriate
function based on Python version.

The ``_PyLong_Format()`` function was removed in Python 3.13. This was used in the EC module
for converting Python integers to decimal strings for OpenSSL's ``BN_dec2bn()``. The fix uses
``PyObject_Str()`` which is the public API for string conversion.

Python 3.14 Support
^^^^^^^^^^^^^^^^^^^

Python 3.14 is now fully supported in CI/CD pipelines:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Platform
     - Python Versions
   * - Linux
     - 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14
   * - macOS
     - 3.9, 3.10, 3.11, 3.12, 3.13, 3.14
   * - Windows
     - 3.9, 3.10, 3.11, 3.12, 3.13, 3.14

**Wheel Builds:**

The cibuildwheel configuration now builds wheels for Python 3.13 and 3.14::

    CIBW_BUILD: cp38-* cp39-* cp310-* cp311-* cp312-* cp313-* cp314-*

Python 3.12+ Integer Conversion Bug Fix
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This release includes a fix for the integer conversion bug introduced in Python 3.12 where
the internal structure of ``PyLongObject`` changed:

**Python 3.11 and earlier:**

- ``ob_size`` stores the signed digit count
- ``ob_digit`` is the digit array

**Python 3.12 and later:**

- ``long_value.lv_tag`` stores digit count + sign + flags
- ``long_value.ob_digit`` is the digit array

The fix adds new macros (``PythonLongDigitCount``, ``PythonLongIsNegative``, ``PythonLongSetTag``)
that correctly handle both structures.

Bug Fixes
^^^^^^^^^

- Fixed segmentation fault in EC module on Python 3.13
- Fixed ``undefined symbol: _Py_IsFinalizing`` error on Python 3.13
- Fixed negative number handling in ``mpzToLongObj()``
- Fixed hanging tests on Python 3.12+ (RSAGroup.paramgen, chamhash_rsa_hw09, Rabin signature)

Testing Infrastructure
^^^^^^^^^^^^^^^^^^^^^^

- Added Docker-based testing environment for Python 3.12+ debugging
- Added comprehensive integer arithmetic test suite
- All tests now pass on Python 3.8 through 3.14

Supported Versions
^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Component
     - Supported Versions
   * - Python
     - 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14
   * - Operating Systems
     - Linux, macOS, Windows
   * - OpenSSL
     - 3.0+

Upgrade Notes
^^^^^^^^^^^^^

This release is fully backward compatible with v0.60. No code changes are required
when upgrading from v0.60 to v0.61.

**Installation:**

::

    pip install --upgrade charm-crypto-framework

Contributors
^^^^^^^^^^^^

Thanks to all contributors for this release, including fixes for Python 3.13 and 3.14
compatibility issues.

