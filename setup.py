from distutils.core import setup, Extension
import os,platform

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

path = 'charm-src/'
_macros = []
_charm_version = opt.get('VERSION')
if opt.get('PAIR_MOD') == 'yes':
   pairing_module = Extension('pairing', include_dirs = [path+'utils/'], 
                           sources = [path+'pairingmath/pairingmodule.c', path+'utils/sha1.c', path+'utils/base64.c'],
                           libraries=['pbc', 'gmp'])
   _ext_modules.append(pairing_module)
   
if opt.get('INT_MOD') == 'yes':
   integer_module = Extension('integer', include_dirs = [path+'utils/'],
                           sources = [path+'integermath/integermodule.c', path+'utils/sha1.c', path+'utils/base64.c'], 
                           libraries=['gmp', 'crypto'])
   _ext_modules.append(integer_module)
   
if opt.get('ECC_MOD') == 'yes':
   ecc_module = Extension('ecc', include_dirs = [path+'utils/'], 
				sources = [path+'ecmath/ecmodule.c', path+'utils/sha1.c', path+'utils/base64.c'], 
				libraries=['gmp', 'crypto'])
   _ext_modules.append(ecc_module)

benchmark_module = Extension('benchmark', sources = [path+'utils/benchmarkmodule.c'])
cryptobase = Extension('cryptobase', sources = [path+'cryptobase/cryptobasemodule.c'])

aes = Extension('AES', sources = [path+'cryptobase/AES.c'])
des  = Extension('DES', include_dirs = [path+'cryptobase/libtom/'], sources = [path+'cryptobase/DES.c'])
des3  = Extension('DES3', include_dirs = [path+'cryptobase/libtom/'], sources = [path+'cryptobase/DES3.c'])
_ext_modules.extend([benchmark_module, cryptobase, aes, des, des3])

if platform.system() in ['Linux', 'Windows']:
   # add benchmark module to pairing, integer and ecc 
   if opt.get('PAIR_MOD') == 'yes': pairing_module.sources.append(path+'utils/benchmarkmodule.c')
   if opt.get('INT_MOD') == 'yes': integer_module.sources.append(path+'utils/benchmarkmodule.c')
   if opt.get('ECC_MOD') == 'yes': ecc_module.sources.append(path+'utils/benchmarkmodule.c')

setup(name = 'Charm-Crypto',
	ext_package = 'charm',
	version =  _charm_version,
	description = 'Charm is a framework for rapid prototyping of cryptosystems',
	ext_modules = _ext_modules,
	author = "J Ayo Akinyele",
	author_email = "waldoayo@gmail.com",
	url = "http://code.google.com/p/charm-crypto/",
	packages = ['charm', 'toolbox', 'compiler', 'schemes'],
	package_dir = {'charm': 'charm-src/charm'},
    package_data = {'charm':['__init__.py', 'engine/*.py'], 'toolbox':['*.py'], 'compiler':['*.py'], 'schemes':['*.py'], 'param':['*.param']},
        license = 'GPL'
     )


