from distutils.core import setup, Extension

path = 'charm/'
_macros = []
pairing_module = Extension('pairing', include_dirs = [path+'utils/'], sources = [path+'pairingmath/pairingmodule.c', path+'utils/sha1.c', path+'utils/base64.c', path+'utils/benchmarkmodule.c'], libraries=['pbc', 'gmp'])
integer_module = Extension('integer', include_dirs = [path+'utils/'], sources = [path+'integermath/integermodule.c', path+'utils/sha1.c', path+'utils/base64.c', path+'utils/benchmarkmodule.c'], libraries=['gmp', 'crypto'])
ecc_module = Extension('ecc', include_dirs = [path+'utils/'], 
				sources = [path+'ecmath/ecmodule.c', path+'utils/sha1.c', path+'utils/base64.c', path+'utils/benchmarkmodule.c'], 
				libraries=['gmp', 'crypto'])
benchmark_module = Extension('benchmark', sources = [path+'utils/benchmarkmodule.c'])
cryptobase = Extension('cryptobase', sources = [path+'cryptobase/cryptobasemodule.c'])

aes = Extension('AES', sources = [path+'cryptobase/AES.c'])
des  = Extension('DES', include_dirs = [path+'cryptobase/libtom/'], sources = [path+'cryptobase/DES.c'])
des3  = Extension('DES3', include_dirs = [path+'cryptobase/libtom/'], sources = [path+'cryptobase/DES3.c'])

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
	package_data = {'charm':['__init__.py', 'engine/*.py']},
        py_modules = ['toolbox.ecgroup', 'toolbox.integergroup', 'toolbox.pairinggroup', 'toolbox.enum', 'toolbox.schemebase', 'toolbox.IBEnc', 'toolbox.PKEnc', 'toolbox.PKSig', 'toolbox.ABEnc', 'toolbox.secretutil', 
                     'toolbox.node', 'toolbox.zknode', 'toolbox.policytree', 'toolbox.sigmaprotocol', 'toolbox.Commit'],
        license = 'GPL'
     )

