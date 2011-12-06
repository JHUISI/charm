.. _charm-with-miracl:

Building MIRACL for Charm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first step is to obtain the MIRACL library source from http://www.shamus.ie/. Currently, our pairing base module works with version 5.5.4 (released on 02/08/11). If you're interested in using it for academic purposes, then you are not required to purchase a license. Otherwise, you will have to purchase a MIRACL license since it is not under an open source license. With that said, we provide instructions for how to compile MIRACL and the charm pairing module. 

        1. Unzip the miracl.zip into ``charm/charm-src/pairingmath/miracl/``
                ``unzip -j -aa -L miracl.zip``

        2. Change directories into the ``miracl`` dir and build the library using the provided compile script. 
                ``sh compile_miracl.sh``

        3. If there are no errors during MIRACL compile, a ``miracl.a`` static library file should appear and you may run configure at the top-level source dir and enable use of MIRACL.
                ``./configure.sh --enable-pairing-miracl``

        4. You may build and install Charm as usual. These commands may or may not require super-user privileges depending on your environment.
                ``make build``

                ``sudo make install``

.. note::
	At the moment, our support for the MIRACL library is rather limited. Primarily, the MIRACL based pairing module only supports the MNT curve parameters shipped with version 5.5.4. We plan to improve the interface significantly in the next few releases and possibly expand to other base modules (standard elliptic curve and integer module). Thank you!
