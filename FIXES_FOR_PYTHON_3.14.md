# Specific Code Fixes for Python 3.14 Compatibility

## 1. Fix longintrepr.h Includes

### File: `charm/core/math/pairing/relic/pairingmodule3.h`

**Current (Line 44):**
```c
#include <longintrepr.h>
```

**Fix:**
```c
#if PY_MINOR_VERSION <= 10
  #include <longintrepr.h>
#else
  #include <cpython/longintrepr.h>
#endif
```

### File: `charm/core/math/pairing/miracl/pairingmodule2.h`

**Current (Line 49):**
```c
#include <longintrepr.h>
```

**Fix:**
```c
#if PY_MINOR_VERSION <= 10
  #include <longintrepr.h>
#else
  #include <cpython/longintrepr.h>
#endif
```

### Update Version Checks for Python 3.13+

All header files currently check `PY_MINOR_VERSION <= 10` which assumes Python 3.10 or earlier.
Python 3.13+ may further restrict access to `cpython/longintrepr.h`.

**Recommended approach:**
```c
#if PY_VERSION_HEX < 0x030B0000  /* Python < 3.11 */
  #include <longintrepr.h>
#elif PY_VERSION_HEX < 0x030D0000  /* Python 3.11-3.12 */
  #include <cpython/longintrepr.h>
#else  /* Python 3.13+ */
  /* Consider using PEP 757 APIs instead */
  #include <cpython/longintrepr.h>
#endif
```

## 2. Fix platform.linux_distribution() in setup.py

**Current (Line 40):**
```python
dist = platform.linux_distribution()[0];
```

**Fix Option 1 - Use /etc/os-release:**
```python
def get_linux_distribution():
    try:
        with open('/etc/os-release') as f:
            for line in f:
                if line.startswith('ID='):
                    dist_id = line.split('=')[1].strip().strip('"')
                    return dist_id.capitalize()
    except:
        pass
    return ''

# Then replace line 40:
dist = get_linux_distribution()
```

**Fix Option 2 - Simplify (Recommended):**
```python
# Remove platform-specific path detection and use standard paths
# Modern Python installations use consistent paths
path_to_charm = get_python_lib(1, 1)
```

## 3. Update configure.sh Python Version Detection

**Current (Line 505):**
```bash
for pyversion in python python3 python3.8 python3.7 python3.6 python3.5 python3.4 python3.3 python3.2 python3.1
```

**Fix:**
```bash
for pyversion in python python3 python3.14 python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3.7
```

## 4. Update CI/CD Configurations

### File: `.github/workflows/ci.yml`

**Current (Line 22):**
```yaml
python-version: '3.8'
```

**Fix - Add matrix testing:**
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12', '3.13']
steps:
  - name: Set up Python
    uses: actions/setup-python@v4
    with:
      python-version: ${{ matrix.python-version }}
```

### File: `tox.ini`

**Current:**
```ini
[tox]
envlist= py32
```

**Fix:**
```ini
[tox]
envlist= py310,py311,py312,py313
```

## 5. Add Python Version Classifiers to setup.py

**Add after line 279:**
```python
classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
    'Programming Language :: Python :: 3.14',
    'Programming Language :: C',
],
python_requires='>=3.10',
```

## 6. Future-Proof: Prepare for PEP 757 Migration

The current code in `integermodule.c` directly accesses PyLongObject internals.
Python 3.14 introduces PEP 757 which provides official APIs for this.

**Current approach (integermodule.c lines 85-108):**
```c
void longObjToMPZ(mpz_t m, PyObject * o) {
    PyLongObject *p = (PyLongObject *) PyNumber_Long(o);
    // Direct access to ob_digit...
}
```

**Future approach using PEP 757 (Python 3.14+):**
```c
#if PY_VERSION_HEX >= 0x030E0000  /* Python 3.14+ */
void longObjToMPZ(mpz_t m, PyObject * o) {
    PyLongExport export_data;
    if (PyLong_Export(o, &export_data) < 0) {
        return;  // Handle error
    }
    // Use export_data.digits, export_data.ndigits, etc.
    // Convert to GMP
    PyLong_FreeExport(&export_data);
}
#else
// Keep existing implementation for older Python versions
#endif
```

## 7. Add Compatibility Header (Optional)

Create `charm/core/compat.h` to centralize version-specific code:

```c
#ifndef CHARM_COMPAT_H
#define CHARM_COMPAT_H

#include <Python.h>

/* Python version compatibility macros */
#if PY_VERSION_HEX < 0x030B0000  /* Python < 3.11 */
  #include <longintrepr.h>
  #define CHARM_HAS_LONGINTREPR 1
#elif PY_VERSION_HEX < 0x030E0000  /* Python 3.11-3.13 */
  #include <cpython/longintrepr.h>
  #define CHARM_HAS_LONGINTREPR 1
#else  /* Python 3.14+ */
  /* Use PEP 757 APIs */
  #define CHARM_HAS_LONGINTREPR 0
#endif

#endif /* CHARM_COMPAT_H */
```

Then include this in all modules instead of directly including longintrepr.h.

## Priority Order

1. **CRITICAL (Do First):**
   - Fix pairingmodule3.h and pairingmodule2.h longintrepr.h includes
   - Fix platform.linux_distribution() in setup.py
   - Update configure.sh version detection

2. **HIGH (Do Soon):**
   - Update CI/CD to test Python 3.10+
   - Add python_requires to setup.py
   - Test build on Python 3.13

3. **MEDIUM (Plan For):**
   - Implement PEP 757 support for Python 3.14+
   - Create compatibility header
   - Migrate from distutils

4. **LOW (Nice to Have):**
   - Add comprehensive version classifiers
   - Update documentation
   - Add deprecation warnings for old Python versions

