from setuptools import setup
from setuptools.command.test import test as TestCommand
from distutils.core import  Command, Extension
from distutils.sysconfig import get_python_lib
import os, platform, sys, shutil, re, fileinput

def replaceString(file,searchExp,replaceExp):
    if file == None: return # fail silently
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        import sys
        sys.exit(pytest.main(self.test_args))

class UninstallCommand(Command):
    description = "remove old files"
    user_options= []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        install_system=platform.system();
        path_to_charm2 = None;
        if install_system == 'Darwin':
            path_to_charm = get_python_lib();
        elif install_system == 'Windows':
            path_to_charm = get_python_lib();
        elif install_system == 'Linux':
            dist = platform.linux_distribution()[0];
            if dist == 'Ubuntu' or dist == 'debian' or dist == 'LinuxMint':
                path_to_charm = get_python_lib(1, 1, '/usr/local') + '/dist-packages';
                path_to_charm2 = get_python_lib(1, 1, '/usr/local') + '/site-packages';
            elif dist == 'Fedora':
                path_to_charm = get_python_lib(1, 1, '/usr') + '/site-packages';
        #print('python path =>', path_to_charm, _charm_version);
        shutil.rmtree(path_to_charm+'/__pycache__', True)
        shutil.rmtree(path_to_charm+'/compiler', True)
        shutil.rmtree(path_to_charm+'/schemes', True)
        shutil.rmtree(path_to_charm+'/toolbox', True)
        shutil.rmtree(path_to_charm+'/charm/engine', True)

        for files in os.listdir(path_to_charm):
            if not re.match('Charm_Crypto-'+_charm_version+'\.egg-info', files) and re.match('Charm_Crypto-.*\.egg-info', files):
                #print(path_to_charm+'/'+files)
                os.remove(path_to_charm+'/'+files)

        for files in os.listdir(path_to_charm+'/charm'):
            if re.match('.*\.so$', files):
                #print(path_to_charm+'/charm/'+files)
                os.remove(path_to_charm+'/charm/'+files)

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
        print("Warning, using default config vaules.")
        print("You probably want to run ./configure.sh first.")
        opt = {'PAIR_MOD':'yes',
                'USE_PBC':'yes',
                'INT_MOD':'yes',
                'ECC_MOD':'yes'
                }

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

_charm_version = opt.get('VERSION')
lib_config_file = 'charm/config.py'
inc_dirs = [s[2:] for s in opt.get('CHARM_CFLAGS').split() if s.startswith('-I')]
library_dirs = [s[2:] for s in opt.get('LDFLAGS').split() if s.startswith('-L')]
runtime_library_dirs = [s[11:] for s in opt.get('LDFLAGS').split()
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

_ext_modules.extend([benchmark_module, cryptobase, aes, des, des3])
#_ext_modules.extend([cryptobase, aes, des, des3])

if platform.system() in ['Linux', 'Windows']:
   # add benchmark module to pairing, integer and ecc 
   if opt.get('PAIR_MOD') == 'yes': pairing_module.sources.append(benchmark_path + 'benchmarkmodule.c')
   if opt.get('INT_MOD') == 'yes': integer_module.sources.append(benchmark_path  + 'benchmarkmodule.c')
   if opt.get('ECC_MOD') == 'yes': ecc_module.sources.append(benchmark_path  + 'benchmarkmodule.c')

setup(name = 'Charm-Crypto',
	version =  _charm_version,
	description = 'Charm is a framework for rapid prototyping of cryptosystems',
	ext_modules = _ext_modules,
	author = "J. Ayo Akinyele",
	author_email = "ayo.akinyele@charm-crypto.com",
	url = "http://charm-crypto.io/",
        install_requires = ['setuptools',
                            'pyparsing >= 2.1.5,<2.4.1',
                            'hypothesis'],
        tests_require=['pytest', 'hypothesis'],
	packages = ['charm',
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
    license = 'LGPL',
    cmdclass={'uninstall':UninstallCommand,'test':PyTest}
)
