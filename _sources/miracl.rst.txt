.. _charm-with-miracl:

Building MIRACL for Charm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first step is to obtain the MIRACL library source from http://www.certivox.com/miracl/. Currently, our pairing base module works with version 5.5.4 (released on 02/08/11). If you're interested in using it for academic purposes, then you are not required to purchase a license. Otherwise, you will have to purchase a MIRACL license since it is not under an open source license. With that said, we provide instructions for how to compile MIRACL and the charm pairing module. 

        1. Unzip the MIRACL-master.zip in the ``charm/charm/core/math/pairing/miracl/``
                ``unzip -j -aa -L MIRACL-master.zip``

        2. Change directories into the ``miracl`` dir and build the library using the provided compile script. Note that this script can build specific curves supported in the MIRACL library. These include ``ss`` for supersingular curves, ``mnt`` for MNT curves and ``bn`` for Barreto-Naehrig curves. This command may require super-user privileges to install on your system. 
                ``sh compile_miracl.sh bn``

        3. If there are no errors during MIRACL compile/install, you may run configure at the top-level source dir and enable use of MIRACL with a specific curve. Unfortunately, we can only support one curve at run-time which is a mild inconvenience and requires re-running configure to switch to another curve. 
                ``./configure.sh --enable-pairing-miracl=bn``

        4. You may build and install Charm as usual. These commands may or may not require super-user privileges depending on your environment.
                ``make``

                ``sudo make install``

