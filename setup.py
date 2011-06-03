from distutils.core import setup, Extension
import os,platform

print("Platform:", platform.system())

path = 'charm-src/'
_macros = []
pairing_module = Extension('pairing', include_dirs = [path+'utils/'], sources = [path+'pairingmath/pairingmodule.c', path+'utils/sha1.c', path+'utils/base64.c'], libraries=['pbc', 'gmp'])
integer_module = Extension('integer', include_dirs = [path+'utils/'], sources = [path+'integermath/integermodule.c', path+'utils/sha1.c', path+'utils/base64.c'], libraries=['gmp', 'crypto'])
ecc_module = Extension('ecc', include_dirs = [path+'utils/'], 
				sources = [path+'ecmath/ecmodule.c', path+'utils/sha1.c', path+'utils/base64.c'], 
				libraries=['gmp', 'crypto'])
benchmark_module = Extension('benchmark', sources = [path+'utils/benchmarkmodule.c'])
cryptobase = Extension('cryptobase', sources = [path+'cryptobase/cryptobasemodule.c'])

aes = Extension('AES', sources = [path+'cryptobase/AES.c'])
des  = Extension('DES', include_dirs = [path+'cryptobase/libtom/'], sources = [path+'cryptobase/DES.c'])
des3  = Extension('DES3', include_dirs = [path+'cryptobase/libtom/'], sources = [path+'cryptobase/DES3.c'])

if platform.system() == 'Linux':
   # add benchmark module to pairing, integer and ecc 
   pairing_module.sources.append(path+'utils/benchmarkmodule.c')
   integer_module.sources.append(path+'utils/benchmarkmodule.c')
   ecc_module.sources.append(path+'utils/benchmarkmodule.c')

setup(name = 'Charm-Crypto-Module',
	ext_package = 'charm',
	version = '0.1',
	description = 'Charm is a framework for rapid prototyping of cryptosystems',
	ext_modules = [pairing_module, integer_module, ecc_module, benchmark_module, 
                   cryptobase, aes, des, des3],
	author = "J Ayo Akinyele",
	author_email = "waldoayo@gmail.com",
	url = "http://code.google.com/p/charm-crypto/",
	packages = ['charm', 'toolbox', 'compiler', 'schemes'],
	package_dir = {'charm': 'charm-src/charm'},
	package_data = {'charm':['__init__.py', 'engine/*.py'], 'toolbox':['*.py'], 'compiler':['*.py'], 'schemes':['*.py']},
        license = 'GPL'
     )


