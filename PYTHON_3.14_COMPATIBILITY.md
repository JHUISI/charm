# Python 3.14 Compatibility Guide for Charm-Crypto

## Current Status
Charm-Crypto currently supports Python 3.x but has several compatibility issues that need to be addressed for Python 3.14 support.

## Key Issues Identified

### 1. **C API Changes - `longintrepr.h` Header (CRITICAL)**

**Problem:** The code uses conditional includes for `longintrepr.h` vs `cpython/longintrepr.h` based on `PY_MINOR_VERSION <= 10`, but Python 3.13+ has made significant changes to the C API, and Python 3.14 continues this trend.

**Affected Files:**
- `charm/core/math/integer/integermodule.h` (lines 47-51)
- `charm/core/math/pairing/pairingmodule.h` (lines 45-49)
- `charm/core/math/pairing/relic/pairingmodule3.h` (line 44 - missing conditional!)
- `charm/core/math/pairing/miracl/pairingmodule2.h` (line 49 - missing conditional!)
- `charm/core/math/elliptic_curve/ecmodule.h` (lines 40-44)

**Solution:** 
1. Update the conditional includes to handle Python 3.13+
2. Consider using the new PEP 757 C API for integer import/export (already partially implemented in pairingmodule.c)
3. Fix missing conditionals in relic and miracl modules

### 2. **PyLongObject Internal Structure Changes**

**Problem:** Direct access to `PyLongObject` internals has changed in Python 3.12+ and may be further restricted in 3.14.

**Affected Code:**
- `charm/core/math/integer/integermodule.c` uses `PythonLongVal(l)` macro to access `ob_digit`
- Python 3.12+ changed structure from `ob_digit` to `long_value.ob_digit`
- Python 3.14 may further restrict or remove access to these internals

**Current Workaround:** Macros defined in integermodule.c (lines 32-42) and pairingmodule.c (lines 32-41)

**Recommendation:** Migrate to PEP 757 APIs:
- `PyLong_Export()` / `PyLong_FreeExport()`
- `PyLongWriter_Create()` / `PyLongWriter_Finish()`

### 3. **Deprecated distutils Module**

**Problem:** `setup.py` imports from `distutils.core` and `distutils.sysconfig` (lines 3-4)

**Status:** `distutils` was removed in Python 3.12, but setuptools provides a compatibility shim. This may not work in future versions.

**Solution:** Migrate to modern build system:
- Use `setuptools` exclusively
- Consider migrating to `pyproject.toml` with PEP 517/518
- Replace `distutils.sysconfig.get_python_lib()` with `sysconfig.get_path()`

### 4. **platform.linux_distribution() Removal**

**Problem:** `setup.py` line 40 uses `platform.linux_distribution()` which was removed in Python 3.8

**Solution:** Use alternative methods:
- Check `/etc/os-release` file
- Use `distro` package from PyPI
- Or remove this platform-specific logic

### 5. **Configure Script Python Version Detection**

**Problem:** `configure.sh` (line 505) only checks for Python versions up to 3.8

**Solution:** Update the version list to include newer versions:
```bash
for pyversion in python python3 python3.14 python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3.7
```

### 6. **CI/CD Configuration**

**Problem:** 
- `.travis.yml` only tests Python 3.4, 3.6, 3.7
- `.github/workflows/ci.yml` only tests Python 3.8
- `tox.ini` only tests py32

**Solution:** Update to test modern Python versions (3.10, 3.11, 3.12, 3.13, 3.14)

## Recommended Action Plan

### Phase 1: Critical Fixes (Required for Python 3.13+)
1. ✅ Fix `longintrepr.h` includes in all C extension modules
2. ✅ Fix `pairingmodule3.h` and `pairingmodule2.h` missing conditionals
3. ✅ Update configure script to detect Python 3.13+
4. ✅ Fix `platform.linux_distribution()` usage

### Phase 2: Modernization (Recommended)
1. Migrate to PEP 757 C API for integer operations
2. Replace distutils with setuptools/sysconfig
3. Create `pyproject.toml` for modern build system
4. Update CI/CD to test Python 3.10-3.14

### Phase 3: Future-Proofing
1. Add Python version classifiers in setup.py
2. Document minimum and maximum supported Python versions
3. Set up automated testing for new Python releases
4. Consider using `pythoncapi-compat` for backward compatibility

## Python 3.14 Specific Changes to Watch

Based on the official Python 3.14 release notes:

1. **C API Changes:**
   - `Py_REFCNT()` and `Py_TYPE()` are now opaque function calls in limited API 3.14+
   - Many private C APIs deprecated or removed
   - New `PyConfig_Get()` / `PyConfig_Set()` for runtime configuration

2. **Build Changes:**
   - GNU Autoconf 2.72 required
   - New compiler security options enabled by default

3. **Removed APIs:**
   - Various deprecated functions from 3.13 are now removed
   - `PyDictObject.ma_version_tag` removed

## Testing Strategy

1. Test on Python 3.13 first (currently available)
2. Build and run test suite
3. Fix any deprecation warnings
4. Test on Python 3.14 when available
5. Monitor for any runtime issues with C extensions

## Resources

- [Python 3.14 What's New](https://docs.python.org/3/whatsnew/3.14.html)
- [PEP 757: C API to import-export Python integers](https://peps.python.org/pep-0757/)
- [PEP 741: Python Configuration C API](https://peps.python.org/pep-0741/)
- [Porting Extension Modules to Python 3](https://docs.python.org/3/howto/cporting.html)

