Embedding Charm via Python/C API
================================

We have only tested with Python 2.7 and 3.3, but should work generally with any Python version supported in Charm.

Compiling
============

1. Linux

		./configure.sh 
		cd embed/
		make
		./test

2. Mac OS X: this requires MacPorts and the ``gettext`` package (e.g., sudo port install gettext), then execute the following:

		./configure.sh --enable-darwin	
		cd embed/
		make
		./test
	
3. Windows (have not tested yet)