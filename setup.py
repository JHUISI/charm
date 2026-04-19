from setuptools import setup
from distutils.core import  Command, Extension
from distutils.sysconfig import get_python_lib
import os, platform, sys, shutil, re, fileinput, subprocess

def replaceString(file,searchExp,replaceExp):
    if file == None: return # fail silently
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)

_ext_modules = []

def read_config(file):
    f = open(file, 'r')
    lines = f.read().split('\n')
    config_key = {}
    for e in lines:
        if e.find('=') != -1:
           param = e.split('=')
           config_key[ param[0] ] = param[1]
    f.close()
    return config_key

def read_version_file():
    """Read version from VERSION file, with fallback."""
    try:
        with open('VERSION', 'r') as f:
            return f.read().strip()
    except IOError:
        return '0.0.0'  # Fallback version

def run_pkg_config(package, flags):
    """
    Run pkg-config to get compiler/linker flags for a package.

    Args:
        package: The package name (e.g., 'gmp', 'pbc', 'openssl')
        flags: The flags to request (e.g., '--cflags', '--libs', '--libs-only-L')

    Returns:
        The output string from pkg-config, or empty string if pkg-config fails.
    """
    import subprocess
    try:
        result = subprocess.run(
            ['pkg-config', flags, package],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        # pkg-config not available or timed out
        pass
    return ''

def get_pkg_config_flags(packages):
    """
    Get combined compiler and linker flags for multiple packages using pkg-config.

    Args:
        packages: List of package names to query (e.g., ['gmp', 'pbc', 'libcrypto'])

    Returns:
        Tuple of (cflags, ldflags) strings with all flags combined.
    """
    cflags_parts = []
    ldflags_parts = []

    for package in packages:
        # Get include paths
        cflags = run_pkg_config(package, '--cflags')
        if cflags:
            cflags_parts.append(cflags)

        # Get library paths (just -L flags, not -l flags)
        # We use --libs-only-L to get library directories
        ldflags = run_pkg_config(package, '--libs-only-L')
        if ldflags:
            ldflags_parts.append(ldflags)

    # Deduplicate flags while preserving order
    def dedupe_flags(flags_str):
        seen = set()
        result = []
        for flag in flags_str.split():
            if flag not in seen:
                seen.add(flag)
                result.append(flag)
        return ' '.join(result)

    combined_cflags = dedupe_flags(' '.join(cflags_parts))
    combined_ldflags = dedupe_flags(' '.join(ldflags_parts))

    return combined_cflags, combined_ldflags

def get_fallback_paths():
    """
    Get fallback library/include paths when pkg-config is not available.

    Returns:
        Tuple of (cflags, ldflags) strings with platform-specific paths.
    """
    system = platform.system()
    ldflags_parts = []
    cflags_parts = []

    if system == 'Darwin':
        # macOS: Check for Homebrew installation (both Apple Silicon and Intel)
        homebrew_prefixes = ['/opt/homebrew', '/usr/local']
        for prefix in homebrew_prefixes:
            if os.path.exists(prefix):
                lib_path = os.path.join(prefix, 'lib')
                inc_path = os.path.join(prefix, 'include')
                # Add paths if the directories exist
                if os.path.isdir(lib_path):
                    ldflags_parts.append(f'-L{lib_path}')
                if os.path.isdir(inc_path):
                    cflags_parts.append(f'-I{inc_path}')
                break
    elif system == 'Linux':
        # Linux: Use standard system paths, plus common additional locations
        # Check common library locations
        for lib_path in ['/usr/local/lib', '/usr/lib', '/usr/lib/x86_64-linux-gnu']:
            if os.path.isdir(lib_path):
                ldflags_parts.append(f'-L{lib_path}')

        # Check common include locations
        for inc_path in ['/usr/local/include', '/usr/include']:
            if os.path.isdir(inc_path):
                cflags_parts.append(f'-I{inc_path}')

    return ' '.join(cflags_parts), ' '.join(ldflags_parts)

def merge_flags(flags1, flags2):
    """
    Merge two flag strings, deduplicating while preserving order.
    """
    seen = set()
    result = []
    for flag in (flags1 + ' ' + flags2).split():
        if flag and flag not in seen:
            seen.add(flag)
            result.append(flag)
    return ' '.join(result)

def get_default_config():
    """
    Generate platform-aware default configuration for PyPI installation.

    This is used when config.mk doesn't exist (e.g., when installing via
    'pip install charm-crypto-framework' from PyPI). The defaults provide
    sensible values for common platforms so the build can proceed.

    The function attempts to use pkg-config to detect library paths for
    gmp, pbc, and openssl. If pkg-config is not available or fails for
    some packages, it merges the results with fallback platform-specific paths.

    For local development, run ./configure.sh first to generate config.mk
    with settings specific to your environment.
    """
    # Base configuration - enables all modules with PBC backend
    config = {
        'PAIR_MOD': 'yes',
        'USE_PBC': 'yes',
        'INT_MOD': 'yes',
        'ECC_MOD': 'yes',
        'LAT_MOD': 'no',
        'DISABLE_BENCHMARK': 'no',
        # These must be strings (even if empty) to avoid AttributeError on .split()
        'LDFLAGS': '',
        'CPPFLAGS': '',
        'CHARM_CFLAGS': '',
        'VERSION': read_version_file(),
    }

    # Required libraries for charm-crypto
    # Note: 'libcrypto' is the pkg-config name for OpenSSL's crypto library
    # Note: 'pbc' often doesn't have a pkg-config file, so we'll use fallback
    required_packages = ['gmp', 'pbc', 'libcrypto']

    # Try pkg-config first (works on Linux and macOS with Homebrew)
    pkg_cflags, pkg_ldflags = get_pkg_config_flags(required_packages)

    # Always get fallback paths - we'll merge them with pkg-config results
    # This handles the case where some packages have pkg-config and some don't
    # (e.g., PBC typically doesn't have a .pc file)
    fallback_cflags, fallback_ldflags = get_fallback_paths()

    if pkg_cflags or pkg_ldflags:
        print("Using pkg-config for library detection (with fallback paths merged)")
        # Merge pkg-config results with fallback paths
        # pkg-config paths come first (more specific), fallback paths added after
        config['CPPFLAGS'] = merge_flags(pkg_cflags, fallback_cflags)
        config['LDFLAGS'] = merge_flags(pkg_ldflags, fallback_ldflags)
    else:
        print("pkg-config not available, using fallback paths")
        config['CPPFLAGS'] = fallback_cflags
        config['LDFLAGS'] = fallback_ldflags

    return config

print("Platform:", platform.system())
config = os.environ.get('CONFIG_FILE')
opt = {}
if config != None:
    print("Config file:", config)
    opt = read_config(config)
else:
    config = "config.mk"
    print("Config file:", config)
    try:
        opt = read_config(config)
    except IOError as e:
        print("Warning, using default config values.")
        print("You probably want to run ./configure.sh first.")
        print("Using platform-aware defaults for PyPI installation...")
        opt = get_default_config()

# Allow enabling lattice module via environment variable
if os.environ.get('LAT_MOD', '').lower() in ('yes', '1', 'true'):
    opt['LAT_MOD'] = 'yes'

core_path = 'charm/core/'
math_path = core_path + 'math/'
crypto_path = core_path + 'crypto/'
utils_path = core_path + 'utilities/'
benchmark_path = core_path + "benchmark/"
cryptobase_path = crypto_path + "cryptobase/"

core_prefix = 'charm.core'
math_prefix = core_prefix + '.math'
crypto_prefix = core_prefix + '.crypto'
#default is no unless benchmark module explicitly disabled
if opt.get('DISABLE_BENCHMARK') == 'yes':
   _macros = None
   _undef_macro = ['BENCHMARK_ENABLED']
else:
   _macros = [('BENCHMARK_ENABLED', '1')]
   _undef_macro = None

# base module config
if opt.get('USE_PBC') == 'yes':
   pass
elif opt.get('USE_RELIC') == 'yes':
   relic_lib = "/usr/local/lib/librelic_s.a"
   relic_inc = "/usr/local/include/relic"
elif opt.get('USE_MIRACL') == 'yes' and opt.get('MIRACL_MNT') == 'yes': 
    mnt_opt = [('BUILD_MNT_CURVE', '1'), ('BUILD_BN_CURVE', '0'), ('BUILD_SS_CURVE', '0')]
    if _macros: 
       _macros.extend( mnt_opt )
    else: 
      _macros = mnt_opt
    miracl_lib = "/usr/local/lib/miracl-mnt.a"
    miracl_inc = "/usr/local/include/miracl"
elif opt.get('USE_MIRACL') == 'yes' and opt.get('MIRACL_BN') == 'yes':
    bn_opt = [('BUILD_MNT_CURVE', '0'), ('BUILD_BN_CURVE', '1'), ('BUILD_SS_CURVE', '0')]
    if _macros: 
       _macros.extend( bn_opt )
    else: 
       _macros = bn_opt 
    miracl_lib = "/usr/local/lib/miracl-bn.a"
    miracl_inc = "/usr/local/include/miracl"
elif opt.get('USE_MIRACL') == 'yes' and opt.get('MIRACL_SS') == 'yes':
    ss_opt = [('BUILD_MNT_CURVE', '0'), ('BUILD_BN_CURVE', '0'), ('BUILD_SS_CURVE', '1')]
    if _macros: 
       _macros.extend( ss_opt )
    else: 
       _macros = ss_opt 
    miracl_lib = "/usr/local/lib/miracl-ss.a"
    miracl_inc = "/usr/local/include/miracl"
else:
    sys.exit("Need to select which module to build for pairing.")

# Get version from config, with fallback to VERSION file
# This ensures version is always available even when config.mk is missing
_charm_version = opt.get('VERSION') or read_version_file()

lib_config_file = 'charm/config.py'

# Extract include directories from compiler flags
# Default to empty string if flags are missing to avoid AttributeError on .split()
inc_dirs = [s[2:] for s in opt.get('CHARM_CFLAGS', '').split() if s.startswith('-I')]
inc_dirs += [s[2:] for s in opt.get('CPPFLAGS', '').split() if s.startswith('-I')]

# Extract library directories from linker flags
# Default to empty string if LDFLAGS is missing (e.g., PyPI installation without config.mk)
library_dirs = [s[2:] for s in opt.get('LDFLAGS', '').split() if s.startswith('-L')]
runtime_library_dirs = [s[11:] for s in opt.get('LDFLAGS', '').split()
                        if s.lower().startswith('-wl,-rpath,')]
if opt.get('PAIR_MOD') == 'yes':
    if opt.get('USE_PBC') == 'yes':
        replaceString(lib_config_file, "pairing_lib=libs ", "pairing_lib=libs.pbc")
        pairing_module = Extension(math_prefix+'.pairing', 
                            include_dirs = [utils_path,
                                            benchmark_path] + inc_dirs,
                            sources = [math_path+'pairing/pairingmodule.c', 
                                        utils_path+'base64.c'],
                            libraries=['pbc', 'gmp', 'crypto'], define_macros=_macros, undef_macros=_undef_macro,
                            library_dirs=library_dirs, runtime_library_dirs=runtime_library_dirs)

    elif opt.get('USE_RELIC') == 'yes':
        # check if RELIC lib has been built. if not, bail
        #if not os.path.exists(relic_lib): 
        #    print("Cannot find RELIC lib. Follow instructions in build script placed in <charm>/core/math/pairing/relic/ dir.")
        #    exit(1)
        replaceString(lib_config_file, "pairing_lib=libs ", "pairing_lib=libs.relic")
        pairing_module = Extension(math_prefix + '.pairing',
                            include_dirs = [utils_path,
                                            benchmark_path, relic_inc],
                            sources = [math_path + 'pairing/relic/pairingmodule3.c',
                                        math_path + 'pairing/relic/relic_interface.c',
                                        utils_path + 'base64.c'],
                            libraries=['relic', 'gmp', 'crypto'], define_macros=_macros, undef_macros=_undef_macro,
                            library_dirs=library_dirs, runtime_library_dirs=runtime_library_dirs)
                            #extra_objects=[relic_lib], extra_compile_args=None)

    elif opt.get('USE_MIRACL') == 'yes':
        # build MIRACL based pairing module - note that this is for experimental use only
        #if not os.path.exists(miracl_lib): 
        #    print("Cannot find MIRACL lib. Follow instructions in build script placed in <charm>/core/math/pairing/miracl/ dir.")
        #    exit(1)
        replaceString(lib_config_file, "pairing_lib=libs ", "pairing_lib=libs.miracl")
        pairing_module = Extension(math_prefix + '.pairing',
                            include_dirs = [utils_path,
                                            benchmark_path, miracl_inc],
                            sources = [math_path + 'pairing/miracl/pairingmodule2.c',
                                        math_path + 'pairing/miracl/miracl_interface2.cc'],
                            libraries=['gmp', 'crypto', 'stdc++'], define_macros=_macros, undef_macros=_undef_macro,
                            extra_objects=[miracl_lib], extra_compile_args=None,
                            library_dirs=library_dirs, runtime_library_dirs=runtime_library_dirs)

    _ext_modules.append(pairing_module)
   
if opt.get('INT_MOD') == 'yes':
   replaceString(lib_config_file, "int_lib=libs ", "int_lib=libs.gmp")
   integer_module = Extension(math_prefix + '.integer', 
                            include_dirs = [utils_path,
                                            benchmark_path] + inc_dirs,
                            sources = [math_path + 'integer/integermodule.c', 
                                        utils_path + 'base64.c'], 
                            libraries=['gmp', 'crypto'], define_macros=_macros, undef_macros=_undef_macro,
                            library_dirs=library_dirs, runtime_library_dirs=runtime_library_dirs)
   _ext_modules.append(integer_module)
   
if opt.get('ECC_MOD') == 'yes':
   replaceString(lib_config_file, "ec_lib=libs ", "ec_lib=libs.openssl")    
   ecc_module = Extension(math_prefix + '.elliptic_curve',
                include_dirs = [utils_path,
                                benchmark_path] + inc_dirs,
				sources = [math_path + 'elliptic_curve/ecmodule.c',
                            utils_path + 'base64.c'], 
				libraries=['gmp', 'crypto'], define_macros=_macros, undef_macros=_undef_macro,
                library_dirs=library_dirs, runtime_library_dirs=runtime_library_dirs)
   _ext_modules.append(ecc_module)

if opt.get('LAT_MOD') == 'yes':
   replaceString(lib_config_file, "lattice_lib=libs ", "lattice_lib=libs.ntl")
   # Detect NTL include/lib paths
   ntl_inc_dirs = list(inc_dirs)
   ntl_lib_dirs = list(library_dirs)
   ntl_rt_dirs = list(runtime_library_dirs)
   try:
       _ntl_cflags = subprocess.check_output(['pkg-config', '--cflags', 'ntl'], stderr=subprocess.DEVNULL).decode().strip()
       _ntl_libs = subprocess.check_output(['pkg-config', '--libs', 'ntl'], stderr=subprocess.DEVNULL).decode().strip()
       ntl_inc_dirs += [s[2:] for s in _ntl_cflags.split() if s.startswith('-I')]
       ntl_lib_dirs += [s[2:] for s in _ntl_libs.split() if s.startswith('-L')]
   except (subprocess.CalledProcessError, FileNotFoundError):
       # Fallback: check common installation paths
       for prefix in ['/opt/homebrew/opt/ntl', '/usr/local', '/usr']:
           if os.path.isfile(os.path.join(prefix, 'include', 'NTL', 'ZZ.h')):
               ntl_inc_dirs.append(os.path.join(prefix, 'include'))
               ntl_lib_dirs.append(os.path.join(prefix, 'lib'))
               break
   lattice_module = Extension(math_prefix + '.lattice',
                include_dirs = [utils_path,
                                benchmark_path,
                                math_path + 'lattice/'] + ntl_inc_dirs,
                sources = [math_path + 'lattice/latticemodule.cpp'],
                libraries=['ntl', 'gmp', 'pthread'], define_macros=_macros, undef_macros=_undef_macro,
                library_dirs=ntl_lib_dirs, runtime_library_dirs=ntl_rt_dirs,
                language='c++',
                extra_compile_args=['-std=c++14'])
   _ext_modules.append(lattice_module)

benchmark_module = Extension(core_prefix + '.benchmark', sources = [benchmark_path + 'benchmarkmodule.c'])

cryptobase = Extension(crypto_prefix+'.cryptobase', sources = [cryptobase_path + 'cryptobasemodule.c'])

aes = Extension(crypto_prefix + '.AES',
                    include_dirs = [cryptobase_path],
                    sources = [crypto_path + 'AES/AES.c'])

des  = Extension(crypto_prefix + '.DES',
                    include_dirs = [cryptobase_path + 'libtom/',
                                    cryptobase_path],
                    sources = [crypto_path + 'DES/DES.c'])

des3  = Extension(crypto_prefix + '.DES3',
                    include_dirs = [cryptobase_path + 'libtom/',
                                    cryptobase_path,
                                    crypto_path + 'DES/'],
                    sources = [crypto_path + 'DES3/DES3.c'])

aesgcm = Extension(crypto_prefix + '.AES_GCM',
                    include_dirs = inc_dirs,
                    sources = [crypto_path + 'AES_GCM/AES_GCM.c'],
                    libraries=['crypto'],
                    library_dirs=library_dirs,
                    runtime_library_dirs=runtime_library_dirs)

_ext_modules.extend([benchmark_module, cryptobase, aes, des, des3, aesgcm])
#_ext_modules.extend([cryptobase, aes, des, des3])

if platform.system() in ['Linux', 'Windows']:
   # add benchmark module to pairing, integer and ecc 
   if opt.get('PAIR_MOD') == 'yes': pairing_module.sources.append(benchmark_path + 'benchmarkmodule.c')
   if opt.get('INT_MOD') == 'yes': integer_module.sources.append(benchmark_path  + 'benchmarkmodule.c')
   if opt.get('ECC_MOD') == 'yes': ecc_module.sources.append(benchmark_path  + 'benchmarkmodule.c')

# Package name follows PyPI conventions (lowercase, hyphenated)
# The import name remains 'charm' for backward compatibility
setup(
    name='charm-crypto-framework',
    version=_charm_version,
    description='Charm is a framework for rapid prototyping of cryptosystems',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    ext_modules=_ext_modules,
    author="J. Ayo Akinyele",
    author_email="jakinye3@jhu.edu",
    url="https://charm-crypto.io/",
    project_urls={
        "Documentation": "https://charm-crypto.io/documentation",
        "Repository": "https://github.com/JHUISI/charm",
        "Issues": "https://github.com/JHUISI/charm/issues",
    },
    python_requires='>=3.8',
    packages=[
        'charm',
        'charm.core',
        'charm.core.crypto',
        'charm.core.engine',
        'charm.core.math',
        'charm.test',
        'charm.test.schemes',
        'charm.test.toolbox',
        'charm.toolbox',
        'charm.zkp_compiler',
        'charm.schemes',
        'charm.schemes.ibenc',
        'charm.schemes.abenc',
        'charm.schemes.pkenc',
        'charm.schemes.hibenc',
        'charm.schemes.pksig',
        'charm.schemes.commit',
        'charm.schemes.grpsig',
        'charm.schemes.prenc',
        'charm.adapters',
    ],
    license='LGPL-3.0-or-later',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: C',
        'Topic :: Security :: Cryptography',
    ]
)
