How To Get Started
==================

Before we begin using Charm, make sure you have the following libraries installed:

- Openssl library [v0.9 or greater]

- Python [v3 or greater]

- 'easy_install' python setup tool

- the pyparsing package

Install Charm
^^^^^^^^^^^^^^^^^^^^^^^^^

Now, to get things going simply execute the configure script packaged with Charm::

   ./configure
   
.. note::
	there are several build options you may set for your environment. For instance, if your python 3 installation is in a non-standard location, then add --python=/path/to/python/3 to configure. 
	
For other build options, execute::

	./configure --help
   
Once configure runs successfully, proceed to build and install Charm. Depending on your environment, these commands may require you have super user privileges. So, prepend the following with 'sudo' or 'su'::

   make build
   make install
   
At this point to verify that Charm has been installed properly, launch your python 3 interpreter::

   >>> from charm.pairing import *
   
If there are no errors or exceptions, Charm has successfully been installed in your environment. Proceed to testing out one of our existing cryptographic scheme implementations in the schemes source directory or learn how to write your own. Refer to the implement a scheme tutorial. 