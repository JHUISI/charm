.. _charm-with-relic:

Building RELIC for Charm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first step is to obtain the RELIC library source from https://code.google.com/p/relic-toolkit/. We provide instructions for how to compile RELIC and the charm pairing module. 

        1. Download the latest version of RELIC and untar in the ``charm/charm/core/math/pairing/relic/``

        2. Change directories into the ``relic`` dir and build the library using the provided compile script. Note that this script only builds Barreto-Naehrig curves supported in the RELIC library. The last command may require super-user privileges to install on your system. 
		``mkdir relic-target``

		``cd relic-target``

                ``sh ../buildRELIC.sh ../relic-<version>/``

        3. If there are no errors during RELIC compile/install, you may run configure at the top-level source dir and enable use of RELIC. 
                ``./configure.sh --enable-pairing-relic``

        4. You may build and install Charm as usual. These commands may or may not require super-user privileges depending on your environment.
                ``make``

                ``sudo make install``

