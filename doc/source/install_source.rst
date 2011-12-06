.. _platform-install-manual:

Platform Install Manual 
===========================================

Charm has automated the installation process such that the end-user
does not have to directly handle dependencies, linking, compiler flag setting.
However, there is always the corner case in which an end-user is using a currently
unsupported platform, and thus may need to build and install using a manual process.

We would like to support you in this case, and have written this documentation to get
you started on your path using Charm.  This installation file will contain some
installation blocks highlighting each respective implementation.

Before we begin, please note the current dependencies:

- Python2.7 or Python3

- Pyparsing http://pyparsing.wikispaces.com/

- GMP http://gmplib.org/ 

- PBC http://crypto.stanford.edu/pbc/news.html

- OPENSSL http://www.openssl.org/

- (optional) MIRACL http://www.shamus.ie/. See :ref:`charm-with-miracl` if interested. 

See ``./configure.sh --help`` for other options.

You can obtain a copy of the latest version of Charm from either of the following links:
        http://code.google.com/p/charm-crypto/downloads

	https://github.com/JHUISI/charm/downloads

Please let us know at support@charm-crypto.com if you run into any setup or installation problems. We will be happy to offer our assistance.

Building In Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Note that the entire compilation process is supported by the Charm configure/make scripts.
The steps for building in linux this way are:

- In a terminal, run configure.sh

- The process will fail out at wget, and will ask you to install.

- Using your package manager of choice (e.g., ``sudo apt-get install wget``), install wget.

- With wget installed, run the configure.sh script again, and it should set up your Make dependencies for you.

  - ``make build``

  - ``make install``

.. note::
	Another way to install dependencies is to use your package manager of choice.

Ubuntu 10.04 LTS
------------------------------------------

Before installing Charm, there are a few prerequisites that need to be installed on your system. These are:

        1. Subversion
                ``sudo apt-get install subversion``
        2. Python 3 (By default, Ubuntu 10.04 LTS comes with 2.6 and does not officially support 2.7. Charm requires 2.7 or 3.x) and header files/static library
                ``sudo apt-get install python3 python3-dev``
        3. m4
                ``sudo apt-get install m4``
        4. libssl-dev
                ``sudo apt-get install libssl-dev``

Next, we will install Charm. Navigate to the Charm directory.
        1. We must first run the configuration script:
                ``sudo ./configure.sh –-python=/path/to/python3``
        2. Now we will build and install Charm:
                ``sudo make build``

                ``sudo make install``
        3. And finally we must rebuild the searchpath for libraries
                ``sudo ldconfig``

Ubuntu 11.04
----------------------------------

Before installing Charm, there are a few prerequisites that need to be installed on your system. These are:
        1. Subversion
                ``sudo apt-get install subversion``
        2. m4
                ``sudo apt-get install m4``
        3. Python 3 (this is an optional, though recommended, step)
                ``sudo apt-get install python3``
        4. Header files/static library
                ``sudo apt-get install python-dev`` (if you did not install Python 3)

                ``sudo apt-get install python3-dev`` (if you did install Python 3)
        5. libssl-dev (only necessary if you did not install Python 3)
                ``sudo apt-get install libssl-dev``

Next, we will install Charm. Navigate to the Charm directory.
        1. We must first run the configuration script:
                ``sudo ./configure.sh``

                [If you installed Python 3 and would like to use that, you will need to add ``-–python=/path/to/python3``]

        2. Now we will build and install Charm:
                ``sudo make build``

                ``sudo make install``

        3. And finally we must rebuild the searchpath for libraries
                ``sudo ldconfig``

Fedora
------------------------------------

Before installing Charm, there are a few prerequisites that need to be installed on your system. These are:
        1. m4
                ``su -c "yum install m4"``

        2. Python 3 (this is an optional, though recommended, step)
                ``su -c "yum install python3"``

        3. Header files/static library
                ``su -c "yum install python-devel"`` (if you did not install Python 3)

                ``su -c "yum install python3-devel"`` (if you did install Python 3)

        4. openssl-devel (only necessary if you did not install Python 3)
                ``su -c "yum install openssl-devel"``

Red Hat/Fedora has decided not to support ECC in OpenSSL due to patent concerns, so we now need to remove their restriction and manually import the required files.
        1. Remove the ECC restriction
                1. Navigate to /usr/include/openssl
                        ``cd /usr/include/openssl``
                2. Open the OpenSSL configuration file for editing using your editor of choice
                        ``su -c "vi opensslconf-i386.h"``
                3. Remove the flags that restrict the use of ECC

Delete (at the beginning of file):
::

	#ifndef OPENSSL_NO_EC
 	# define OPENSSL_NO_EC
     	#endif
    	#ifndef OPENSSL_NO_ECDH
      	# define OPENSSL_NO_ECDH
     	#endif
  	#ifndef OPENSSL_NO_ECDSA
  	# define OPENSSL_NO_ECDSA
	# endif

Delete (later on the file):
::

	# if defined(OPENSSL_NO_EC) && !defined(NO_EC)
	#  define NO_EC
	# endif
	# if defined(OPENSSL_NO_ECDH) && !defined(NO_ECDH)
	#  define NO_ECDH
	# endif
	# if defined(OPENSSL_NO_ECDSA) && !defined(NO_ECDSA)
	#  define NO_ECDSA
	# endif

Save the file and close it

        2. Add the ECC files
                1. Navigate to http://www.openssl.org/source/ and download the latest version of openssl source and untar the tar ball.
                2. Navigate to /path/to/openssl-[version]/include/openssl (ie inside the untarred file)
                        ``cd /path/to/openssl-[version]/include/openssl``

                3. Add the new files to the current OpenSSL installation
                        ``su -c "yes n | cp * /usr/include/openssl"``

Next, we will install Charm. Navigate to the Charm directory.
        1. We must first run the configuration script:
                ``su -c "./configure.sh"``

                [If you installed Python 3 and would like to use that, you will need to add ``-–python=/path/to/python3``]

        2. Now we will build and install Charm:
                ``su -c "make build"``

                ``su -c "make install"``

        3. And finally we must rebuild the searchpath for libraries
                ``su -c "ldconfig"``

Mint x86_64
--------------------------------------

Before installing Charm, there are a few prerequisites that need to be installed on your system. These are:
        1. Subversion
                ``sudo apt-get install subversion``
        2. m4
                ``sudo apt-get install m4``
        3. Python 3 (this is an optional, though recommended, step)
                ``sudo apt-get install python3``
        4. Header files/static library
                ``sudo apt-get install python-dev`` (if you did not install Python 3)

                ``sudo apt-get install python3-dev`` (if you did install Python 3)

        5. libssl-dev (only necessary if you did not install Python 3)
                ``sudo apt-get install libssl-dev``

        6. This distro doesn't seem to come with binutils or gcc make sure you install those.

Next, we will install Charm. Navigate to the Charm directory.
        1. We must first run the configuration script:
                ``sudo bash ./configure.sh``                

                [If you installed Python 3 and would like to use that, you will need to add ``-–python=/path/to/python3``]

        2. Now we will build and install Charm:
                ``sudo make build``

                ``sudo make install``
        3. And finally we must rebuild the searchpath for libraries
                ``sudo ldconfig``

.. note::
	Bash to avoid unexpected operator error.

Building in Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Note that the entire compilation process is now supported by the Charm configure/make scripts. The steps for building in mingw32 this way are:
        1. Download the latest source version of openssl.
        2. Run MinGW Shell.
    	3. Extract openssl, configure and install as shown below.
	4. Extract Charm, and navigate to the top directory.
        5. Run configure.sh as shown below.
        6. The process will fail out at wget, and open Internet Explorer to the wget download page.
        7. Install wget, and set it's bin directory on your PATH.  To do this, right-click My Computer, Select Properties, Select Advanced System Settings, Select Advanced, Select Environment Variables, and than PATH.  Scroll to the end, and enter a ; followed by the absolute path to the bin directory (e.g., ``C:\Program Files\etc``).
        8. With wget installed, run the configure.sh script again, and it should set up your make dependencies for you.
    	    ``Make build``

            ``Make install``

.. note::
	Another way to install dependencies is to follow the Windows blocks below.


MinGW32
----------------------------------

Let's first build our dependencies with the following scripts:

To build the GMP library:
::

        ./configure --prefix=/mingw --disable-static --enable-shared
        make
        make install


To build the openssl library:
::

        ./config --openssldir=/mingw --shared # This gets us around installing perl.
        make
        make install

To build the PBC library:
::

        ./configure --prefix=/mingw --disable-static --enable-shared
        make
        make install


To build the Charm library:
::

        ./configure.sh --prefix=/mingw --python=/c/Python32/python.exe
	
Building in Mac OS X
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Leopard v10.6
-------------------------------------
Note that the entire compilation process is supported by the Charm configure/make scripts. The steps for building in os x this way are:
    1. In a terminal, run ``configure.sh``
    2. Make sure you have ``wget`` installed otherwise this process may fail at the ``wget`` check, and will ask you to install.
    3. Using your package manager of choice (e.g., ``sudo port install wget``), install wget.
    4. With wget installed, run the ``configure.sh`` script again, and it should set up your make dependencies for you.
    5. The next steps may require super user privileges so prepend a ``sudo`` to each command:
		``make build`` 

       		``make install``

.. note::
	Another way to install dependencies is to use ``macports`` or ``fink``.


Lion v10.7
------------------------------------

In Lion, Apple has made the decision to deprecate the openssl library in favor of their Common-Crypto library implementation. As a result, you'll have to make some modifications to the library in order to use it with Charm. Please follow the steps below then proceed to install Charm:
    1. Edit the ``crypto.h`` header file at ``/usr/include/openssl/crypto.h``
    2. Add the following before the ``crypto.h`` header definition:

::

#pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#ifndef HEADER_CRYPTO_H
#define HEADER_CRYPTO_H


    3. Next, we can install Charm. Run the configure script as before, but due to some changes in the default compiler installed we have provided a command line option to account for these changes:
		``./configure.sh --enable-darwin``
    
    4. The next steps may require super user privileges so prepend a ``sudo`` to each command:
      		``make build`` 

       		``make install``

