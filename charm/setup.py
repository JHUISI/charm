from distutils.core import setup, Extension

_macros = []
pairing_module = Extension('pairing', include_dirs = ['utils/'], sources = ['pairingmath/pairingmodule.c', 'utils/sha1.c', 'utils/base64.c', 'utils/benchmarkmodule.c'], libraries=['pbc', 'gmp'])
integer_module = Extension('integer', include_dirs = ['utils/'], sources = ['integermath/integermodule.c', 'utils/sha1.c', 'utils/base64.c', 'utils/benchmarkmodule.c'], libraries=['gmp', 'crypto'])
ecc_module = Extension('ecc', include_dirs = ['utils/'], 
				sources = ['ecmath/ecmodule.c', 'utils/sha1.c', 'utils/base64.c', 'utils/benchmarkmodule.c'], 
				libraries=['gmp', 'crypto'])
benchmark_module = Extension('benchmark', sources = ['utils/benchmarkmodule.c'])
cryptobase = Extension('cryptobase', sources = ['cryptobase/cryptobasemodule.c'])

aes = Extension('AES', sources = ['cryptobase/AES.c'])
des  = Extension('DES', include_dirs = ['cryptobase/libtom/'], sources = ['cryptobase/DES.c'])
des3  = Extension('DES3', include_dirs = ['cryptobase/libtom/'], sources = ['cryptobase/DES3.c'])

setup(name = 'Charm-Crypto-Module',
	ext_package = 'charm',
	version = '0.1',
	description = 'Charm is a framework for rapid prototyping of cryptosystems',
	ext_modules = [pairing_module, integer_module, ecc_module, benchmark_module, 
                   cryptobase, aes, des, des3],
	author = "J Ayo Akinyele",
	author_email = "waldoayo@gmail.com",
	url = "http://code.google.com/p/charm-crypto/",
	packages = ['charm'],
	package_data = {'charm':['__init__.py', 'engine/*.py'] }
     )

