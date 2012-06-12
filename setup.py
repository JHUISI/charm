from distutils.core import setup, Extension, Command
from distutils.sysconfig import get_python_lib
import os, platform, sys, shutil, re

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

core_path = 'native_extensions/core/'
math_path = core_path + 'math/'
crypto_path = core_path + 'crypto/'
utils_path = core_path + 'utils/'

core_prefix = 'charm.core'
math_prefix = core_prefix + '.math'
crypto_prefix = core_prefix + '.crypto'

_macros = []
_charm_version = opt.get('VERSION')

if opt.get('PAIR_MOD') == 'yes':
    if opt.get('USE_PBC') == 'yes':
        pairing_module = Extension(math_prefix+'.pairing', include_dirs = [utils_path], 
                            sources = [math_path+'pairing/pairingmodule.c', 
                                        utils_path+'sha1.c',
                                        utils_path+'base64.c'],
                            libraries=['pbc', 'gmp'])
    else:
        # build MIRACL based pairing module - note that this is for experimental use only
        pairing_module = Extension(math_prefix + '.pairing',
                            include_dirs = [utils_path,
                                            math_path + 'pairing/miracl/'], 
                            sources = [math_path + 'pairing/pairingmodule2.c',
                                        utils_path + 'sha1.c', 
                                        math_path + 'pairing/miracl/miraclwrapper.cc'],
                            libraries=['gmp','stdc++'],
                            extra_objects=[math_path+'pairing/miracl/miracl.a'], extra_compile_args=None)

    _ext_modules.append(pairing_module)
   
if opt.get('INT_MOD') == 'yes':
   integer_module = Extension(math_prefix + '.integer', 
                            include_dirs = [utils_path],
                            sources = [math_path + 'integer/integermodule.c', 
                                        utils_path + 'sha1.c', 
                                        utils_path + 'base64.c'], 
                            libraries=['gmp', 'crypto'])
   _ext_modules.append(integer_module)
   
if opt.get('ECC_MOD') == 'yes':
   ecc_module = Extension(math_prefix + '.elliptic_curve',
                include_dirs = [utils_path], 
				sources = [math_path + 'elliptic_curve/ecmodule.c',
                            utils_path + 'sha1.c',
                            utils_path + 'base64.c'], 
				libraries=['gmp', 'crypto'])
   _ext_modules.append(ecc_module)

benchmark_module = Extension('benchmark', sources = [utils_path + 'benchmarkmodule.c'])

cryptobase = Extension(crypto_prefix+'.cryptobase', sources = [crypto_path + 'cryptobasemodule.c'])

aes = Extension(crypto_prefix + '.AES', sources = [crypto_path + 'AES.c'])

des  = Extension(crypto_prefix + '.DES',
                    include_dirs = [crypto_path + 'libtom/'],
                    sources = [crypto_path + 'DES.c'])

des3  = Extension(crypto_prefix + '.DES3', include_dirs = [crypto_path + 'libtom/'], 
                    sources = [crypto_path + 'DES3.c'])

_ext_modules.extend([benchmark_module, cryptobase, aes, des, des3])

if platform.system() in ['Linux', 'Windows']:
   # add benchmark module to pairing, integer and ecc 
   if opt.get('PAIR_MOD') == 'yes': pairing_module.sources.append(utils_path + 'benchmarkmodule.c')
   if opt.get('INT_MOD') == 'yes': integer_module.sources.append(utils_path + 'benchmarkmodule.c')
   if opt.get('ECC_MOD') == 'yes': ecc_module.sources.append(utils_path + 'benchmarkmodule.c')

setup(name = 'Charm-Crypto',
	version =  _charm_version,
	description = 'Charm is a framework for rapid prototyping of cryptosystems',
	ext_modules = _ext_modules,
	author = "J. Ayo Akinyele",
	author_email = "ayo.akinyele@charm-crypto.com",
	url = "http://charm-crypto.com/",

    # we inentionally store charm in a directory not named charm so that 
    #running the python interpeter from the project directory imports the
    # installed version and not the one in the project with out the binnaries.
    package_dir = {'charm': 'charm-framework'}, 
	packages = ['charm',
                    'charm.core',
                        'charm.core.crypto',    # contains only c modules, but needs __init__.py to load them
                        'charm.core.engine',
                        'charm.core.math',      # same as charm.core.crypto
                    'charm.toolbox',
                    'charm.zkp_compiler',
                ],
    license = 'GPL',
    cmdclass={'uninstall':UninstallCommand}
)
