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
   
At this point to verify that Charm has been installed properly, launch your python 3 interpreter and import the pairing base module::

   >>> from charm.pairing import *
   
If there are no errors or exceptions, Charm has successfully been installed in your environment. Proceed to testing out one of our existing cryptographic scheme implementations in the schemes source directory or learn how to write your own. Refer to the implement a scheme tutorial. 

Implement a Scheme
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interested in implementing your cryptographic scheme in Charm? Here's a guide to navigate our framework to implement your cryptosystem. The following provides an example implementation compared with the algorithm described in the research paper. 

We begin with a public-key encryption scheme due to Cramer-Shoup 1998 http://knot.kaist.ac.kr/seminar/archive/46/46.pdf, which is provably secure against adaptive chosen ciphertext attacks. 

Typical implementations follow an object-oriented model such that an implementation of a cryptosystem can be easily reused or extended for other purposes. To this end, we provide several base classes with standard interfaces for a variety of cryptographic primitives such as ``PKEnc`` or public-key encryption, ``PKSig`` or public-key signatures, ``ABEnc`` or attribute-based encryption and many more. So, the following describes the python code that implements the Cramer-Shoup PKEnc scheme in Charm:
::

	from toolbox.ecgroup import *

	class CS98(PKEnc):
	     def __init__(self, curve):
	     	 PKEnc.__init__(self)
	     	 global group
	     	 group = ECGroup(curve)
	        		
Before we get started, it is important to understand that in our toolbox each cryptographic setting has a corresponding group abstraction such as elliptic curve group or ``ECGroup``, pairing group or ``PairingGroup``, and integer groups or ``IntegerGroup``. This abstraction provides a simple interface for selecting group parameters, performing group operations, and etc. See the ``toolbox`` documentation for more details.

Thus, at the beginning of the scheme, you must import the corresponding group setting in which the cryptographic scheme will be implemented
::
	
	from toolbox.ecgroup import *

Next, let's explain what goes on during class initialization. During ``__init__``, you define the basic security properties of the ``PKEnc`` scheme and in this case accept as input a NIST standard elliptic curve identifier. The group object can either be defined globally or defined as a class member. The idea is that any routine within this scheme will have access to the group object to perform any operation. In our example, we define group as a global variable. Alternatively, you could define group as ``self.group = ECGroup(curve)``.

.. note::
	Also, the ``init`` routine arguments can vary depending on the scheme and group setting. What is shown above is only an example and see other schemes we have implemented for other possibilities.

We describe the first algorithm in the paper, ``keygen``. Keygen only accepts a security parameter and generates the public and private keys and returns to the user. The paper description is as follows:

.. math:: g_1, g_2 \in G
   :label: keygen1

.. math:: x_1, x_2, y_1, y_2, z \in Z_q
   :label: keygen2

.. math:: c = {g_1}^{x_1} \cdot {g_2}^{x_2}, d = {g_1}^{y_1} \cdot {g_2}^{y_2}, h = {g_1}^z
   :label: keygen3

.. math:: pk = (g_1, g_2, c, d, h, H)
   :label: pk

.. math:: sk = (x_1, x_2, y_1, y_2, z)
   :label: sk

Random elements :eq:`keygen1` are chosen and random elements :eq:`keygen2` are also chosen. Next, the group elements :eq:`keygen3` are computed. Select a hash function H from the family of universal one-way hash functions. The public key is defined by :eq:`pk` and the private key is defined by :eq:`sk`. Below is the Charm ``keygen`` function defined in the ``CS98`` class:

::

	def keygen(self, secparam):
	    g1, g2 = group.random(G), group.random(G)
	    x1, x2, y1, y2, z = group.random(ZR), group.random(ZR), group.random(ZR), group.random(ZR), group.random(ZR)
	    c = (g1 ** x1) * (g2 ** x2) 
	    d = (g1 ** y1) * (g2 ** y2)
	    h = (g1 ** z)

	    pk = { 'g1' : g1, 'g2' : g2, 'c' : c, 'd' : d, 'h' : h, 'H' : group.hash }
	    sk = { 'x1' : x1, 'x2' : x2, 'y1' : y1, 'y2' : y2, 'z' : z }
	    return (pk, sk)

.. math:: m \in G, r \in Z_q
   :label: prelim

.. math:: u_1 = {g_1}^r, u_2 = {g_2}^r, e = h^r\cdot m, \alpha = H(u_1, u_2, e), v = c^r\cdot d^{r\alpha}
   :label: encrypt

.. math:: (u_1, u_2, e, v)
   :label: ciphertext

We now describe the encrypt routine as described by the paper. Given a message in G, the encryption algorithm first selects a random integer r :eq:`prelim`, then computes :eq:`encrypt` and returns the ciphertext as :eq:`ciphertext`. The ``encrypt`` algorithm defined in Charm:

::

	def encrypt(self, pk, m):
	    r   = group.random(ZR)
 	    u1  = pk['g1'] ** r
	    u2  = pk['g2'] ** r
	    e   = group.encode(m) * (pk['h'] ** r)
	    alpha = pk['H'](u1, u2, e)
	    v   = (pk['c'] ** r) * (pk['d'] ** (r * alpha)) 

	    return { 'u1' : u1, 'u2' : u2, 'e' : e, 'v' : v } 

.. math:: \alpha = H(u_1, u_2, e)
   :label: decrypt1

.. math:: {u_1}^{x_1 + y_1\alpha} {u_2}^{x_2 + y_2\alpha} = v
   :label: decrypt2

.. math:: m = e / {u_1}^z
   :label: decrypt3

Finally, the decryption routine as described by the paper. Given a ciphertext, the decryption algorithm runs as follows and first computes :eq:`decrypt1`, and tests if :eq:`decrypt2` condition holds, and if so outputs :eq:`decrypt3` otherwise "reject". The ``decrypt`` algorithm defined in Charm:
::

	def decrypt(self, pk, sk, c):
	    alpha = pk['H'](c['u1'], c['u2'], c['e'])

            v_prime = (c['u1'] ** (sk['x1'] + (sk['y1'] * alpha))) * (c['u2'] ** (sk['x2'] + (sk['y2'] * alpha)))
	    if (c['v'] != v_prime):
		return 'reject' 
	    return group.decode(c['e'] / (c['u1'] ** sk['z'])) 

.. note::
   Since the scheme defines messages as a group element, it is important to use the encode/decode methods to convert the message string into a member of the group, G. This helps transform a cryptographic scheme usable for a real application.  However, the pairing group does not currently implement the routines for encoding/decoding messages as group elements. We utilize other techniques for pairings to provide the ability to convert from/to different message spaces.

This concludes the tutorial on a straightforward implementation of the Cramer-Shoup public-key encryption cryptosystem. Feel free to send us suggestions, bug reports, issues and scheme implementation experiences within Charm at support@charm-crypto.com. Thank you!

