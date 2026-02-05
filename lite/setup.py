"""
charm-crypto-lite: Lightweight elliptic curve cryptography from the Charm framework.

This package provides ONLY the OpenSSL-based elliptic curve module without
GMP or PBC dependencies. It's ideal for applications that only need:
- Elliptic curve operations (secp256k1, etc.)
- Hash-to-curve functionality
- EC point serialization/deserialization

Build requirements:
- OpenSSL development libraries (libssl-dev on Ubuntu, openssl on macOS via Homebrew)
- Python development headers
- C compiler
"""

from setuptools import setup, Extension
import os
import platform

def get_openssl_paths():
    """Get OpenSSL include and library paths for the current platform."""
    system = platform.system()
    inc_dirs = []
    lib_dirs = []

    if system == 'Darwin':
        # macOS: Check for Homebrew installation (both Apple Silicon and Intel)
        homebrew_prefixes = ['/opt/homebrew', '/usr/local']
        for prefix in homebrew_prefixes:
            openssl_path = os.path.join(prefix, 'opt', 'openssl@3')
            if not os.path.exists(openssl_path):
                openssl_path = os.path.join(prefix, 'opt', 'openssl')
            if os.path.exists(openssl_path):
                inc_dirs.append(os.path.join(openssl_path, 'include'))
                lib_dirs.append(os.path.join(openssl_path, 'lib'))
                break
        # Fallback to general Homebrew paths
        for prefix in homebrew_prefixes:
            if os.path.exists(prefix):
                inc_path = os.path.join(prefix, 'include')
                lib_path = os.path.join(prefix, 'lib')
                if os.path.isdir(inc_path) and inc_path not in inc_dirs:
                    inc_dirs.append(inc_path)
                if os.path.isdir(lib_path) and lib_path not in lib_dirs:
                    lib_dirs.append(lib_path)
                break
    elif system == 'Linux':
        # Linux: Standard system paths
        for inc_path in ['/usr/include', '/usr/local/include']:
            if os.path.isdir(inc_path):
                inc_dirs.append(inc_path)
        for lib_path in ['/usr/lib', '/usr/local/lib', '/usr/lib/x86_64-linux-gnu',
                         '/usr/lib/aarch64-linux-gnu']:
            if os.path.isdir(lib_path):
                lib_dirs.append(lib_path)
    elif system == 'Windows':
        # Windows: Check common OpenSSL installation paths
        openssl_paths = [
            os.environ.get('OPENSSL_ROOT_DIR', ''),
            r'C:\Program Files\OpenSSL-Win64',
            r'C:\Program Files\OpenSSL',
            r'C:\OpenSSL-Win64',
            r'C:\OpenSSL',
        ]
        for openssl_path in openssl_paths:
            if openssl_path and os.path.exists(openssl_path):
                inc_path = os.path.join(openssl_path, 'include')
                lib_path = os.path.join(openssl_path, 'lib')
                if os.path.isdir(inc_path):
                    inc_dirs.append(inc_path)
                if os.path.isdir(lib_path):
                    lib_dirs.append(lib_path)
                    # Also check for VC subdirectory (some installers use this)
                    vc_lib = os.path.join(lib_path, 'VC')
                    if os.path.isdir(vc_lib):
                        lib_dirs.append(vc_lib)
                break
        # Also check environment variables
        if 'INCLUDE' in os.environ:
            for path in os.environ['INCLUDE'].split(';'):
                if path and os.path.isdir(path) and path not in inc_dirs:
                    inc_dirs.append(path)
        if 'LIB' in os.environ:
            for path in os.environ['LIB'].split(';'):
                if path and os.path.isdir(path) and path not in lib_dirs:
                    lib_dirs.append(path)

    return inc_dirs, lib_dirs

# Get platform-specific paths
inc_dirs, lib_dirs = get_openssl_paths()

# Paths relative to this setup.py
core_path = 'charm_lite/core/'
math_path = core_path + 'math/'
ec_path = math_path + 'elliptic_curve/'
utils_path = core_path + 'utilities/'
benchmark_path = core_path + 'benchmark/'

# Add local include paths (including EC module path for ecmodule.h)
inc_dirs = [ec_path, utils_path, benchmark_path] + inc_dirs

# Benchmark enabled by default
_macros = [('BENCHMARK_ENABLED', '1')]

# Platform-specific library names
if platform.system() == 'Windows':
    # Windows uses different library names
    crypto_libs = ['libcrypto', 'libssl']
    # Try alternative names if the above don't work
    # Some OpenSSL builds use: libeay32, ssleay32 (older)
    # Or: libcrypto-3-x64, libssl-3-x64 (OpenSSL 3.x)
else:
    crypto_libs = ['crypto']

# EC module - OpenSSL ONLY, no GMP!
ecc_module = Extension(
    'charm_lite.core.math.elliptic_curve',
    include_dirs=inc_dirs,
    sources=[
        math_path + 'elliptic_curve/ecmodule.c',
        utils_path + 'base64.c'
    ],
    libraries=crypto_libs,  # OpenSSL only - NO GMP!
    library_dirs=lib_dirs,
    define_macros=_macros
)

# Benchmark module - no external dependencies
benchmark_module = Extension(
    'charm_lite.core.benchmark',
    sources=[benchmark_path + 'benchmarkmodule.c']
)

# Add benchmark source to EC module on Linux (symbol loading issue)
if platform.system() in ['Linux', 'Windows']:
    ecc_module.sources.append(benchmark_path + 'benchmarkmodule.c')

setup(
    ext_modules=[ecc_module, benchmark_module],
)

