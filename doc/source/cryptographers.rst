For Cryptographers
=======================

Interested in implementing your cryptographic scheme in Charm? Here's a guide to navigate our framework to implement your cryptosystem: 

Group Abstractions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first stage of new scheme development is selecting the appropriate group to instantiate a scheme. Modern cryptographic algorithms are typically implemented on top of mathematical groups based on certain hardness assumptions (e.g., Diffie-Hellman). We provide the same building blocks to facilitate development in this way of thinking: 

At the moment, there are three cryptographic settings covered by Charm (will be expanded in the future): ``integergroups``, ``ecgroups``, and ``pairinggroups``. 
To initialize a group in the elliptic curve (EC) setting, refer to the ``toolbox.eccurve`` for the full set of identifiers and supported NIST approved curves (e.g., ``prime192v1``). For EC with billinear maps (or pairings), we provide a set of identifiers for both symmetric and asymmetric type of curves. For example, the ``'SS512'`` represents a symmetric curve with a 512-bit base field and ``'MNT159'`` represents an asymmetric curve with 159-bit base field. Note that these curves are of prime order.
Finally, for integer groups, typically defining large primes ``p`` and ``q`` is enough to generate an RSA group. For schnorr groups, these group parameters may take some time to generate because they require safe primes (e.g., ``p = 2q + 1``). Here are detailed examples below for integer and pairing groups (see above for EC group initialization):

::

	from charm.toolbox.integergroup import IntegerGroup
	
	group1 = IntegerGroup()	
	group1.paramgen(1024)
	
	g = group1.randomGen()

	from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
	
	group2 = PairingGroup('SS512')
	
	g = group2.random(G1)
	g = group2.random(G2)
	...


Implement a Scheme
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As an example, we show the implementation of a public-key encryption scheme due to Cramer-Shoup 1998 http://knot.kaist.ac.kr/seminar/archive/46/46.pdf, which is provably secure against adaptive chosen ciphertext attacks. 

Typical implementations follow an object-oriented model such that an implementation of a cryptosystem can be easily reused or extended for other purposes. To this end, we provide several base classes with standard interfaces for a variety of cryptographic primitives such as ``PKEnc`` or public-key encryption, ``PKSig`` or public-key signatures, ``ABEnc`` or attribute-based encryption and many more. So, the following describes the python code that implements the Cramer-Shoup PKEnc scheme in Charm:
::

	from charm.toolbox.ecgroup import ECGroup

	class CS98(PKEnc):
	     def __init__(self, curve):
	     	 PKEnc.__init__(self)
	     	 global group
	     	 group = ECGroup(curve)
	        		
Before we get started, it is important to understand that in our toolbox each cryptographic setting has a corresponding group abstraction such as elliptic curve group or ``ECGroup``, pairing group or ``PairingGroup``, and integer groups or ``IntegerGroup``. These abstractions provide a convenient and simple interface for selecting group parameters, performing group operations, and even benchmarking. See the :ref:`toolbox` documentation for more details.

Thus, at the beginning of the scheme, you must import the corresponding group setting in which the cryptographic scheme will be implemented
::
	
	from charm.toolbox.ecgroup import ECGroup

Next, let's explain what goes on during class initialization. During ``__init__``, we define the basic security properties of the ``PKEnc`` scheme and in this case, accept as input a NIST standard elliptic curve identifier. The group object can either be defined globally or defined as a class member. The idea is that any routine within this scheme will have access to the group object to perform any operation. In our example, we define group as a global variable. Alternatively, define group as ``self.group = ECGroup(curve)``.

.. note::
	Also, the ``init`` routine arguments can vary depending on the scheme and group setting. What is shown above is only an example and see other schemes we have implemented for full list of possibilities.

Let's take a look at the first algorithm in the paper, ``keygen``. Keygen only accepts a security parameter, generates the public and private keys and returns them the user. The paper description is as follows:

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

Group elements :eq:`keygen1` and :eq:`keygen2` are selected at random. Next, the group elements :eq:`keygen3` are computed. Then, select a hash function H from the family of universal one-way hash functions. The public key is defined by :eq:`pk` and the private key is defined by :eq:`sk`. Below is the Charm ``keygen`` function defined in the ``CS98`` class:

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

Let's take a look at the encrypt routine as described in the paper. Given a message in G, the encryption algorithm first selects a random integer r :eq:`prelim`, then computes :eq:`encrypt` and returns the ciphertext as :eq:`ciphertext`. The ``encrypt`` algorithm defined in Charm:

::

	def encrypt(self, pk, m):
	    r   = group.random(ZR)
 	    u1  = pk['g1'] ** r
	    u2  = pk['g2'] ** r
	    e   = group.encode(m) * (pk['h'] ** r)
	    alpha = pk['H']((u1, u2, e))
	    v   = (pk['c'] ** r) * (pk['d'] ** (r * alpha)) 

	    return { 'u1' : u1, 'u2' : u2, 'e' : e, 'v' : v } 

.. math:: \alpha = H(u_1, u_2, e)
   :label: decrypt1

.. math:: {u_1}^{x_1 + y_1\alpha} {u_2}^{x_2 + y_2\alpha} = v
   :label: decrypt2

.. math:: m = e / {u_1}^z
   :label: decrypt3

Finally, the decryption routine as described in the paper. Given a ciphertext, the decryption algorithm runs as follows and first computes :eq:`decrypt1`, and tests if :eq:`decrypt2` condition holds, and if so outputs :eq:`decrypt3` otherwise "reject". The ``decrypt`` algorithm defined in Charm:
::

	def decrypt(self, pk, sk, c):
	    alpha = pk['H']((c['u1'], c['u2'], c['e']))

            v_prime = (c['u1'] ** (sk['x1'] + (sk['y1'] * alpha))) * (c['u2'] ** (sk['x2'] + (sk['y2'] * alpha)))
	    if (c['v'] != v_prime):
		return 'reject' 
	    return group.decode(c['e'] / (c['u1'] ** sk['z'])) 

.. note::
   Since the scheme defines messages as a group element, it is important to use the encode/decode methods to convert the message string into a member of the group, ``G``. This encoding function makes cryptographic schemes practical for handling real messages. However, the pairing group does not currently implement such routines for encoding/decoding messages as group elements. This is on purpose given the difficulty and risks associated with implementing such encoding algorithms in pairing groups. Other techniques are used for pairings to provide the ability to convert from/to different message spaces.

For more examples, see the ``schemes`` package that is included in each Charm release.


Reusable Tools 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Perhaps, you are developing a new scheme that relies on existing building blocks such as block ciphers, hash functions, secret sharing and etc -- do not reinvent the wheel! Charm was designed with reusability in mind and to aid cryptographers in easily composing schemes based on existing constructions. Charm has a growing toolbox of reusable components that might simplify your scheme development. If the component you are looking for does not exist in Charm, then once you implement it consider contributing it back to the project for others to leverage. The end goal is to come up with a comprehensive toolbox that all can reuse. See the :ref:`toolbox` section for a detailed list. 

Testing & Benchmarking
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you have implemented your scheme, you might be interested in testing correctness and measuring its efficiency. There are two possible approaches: either define a test routine that executes the algorithms in your scheme via test vectors if they exist and/or embedding the test routine as a docstring in your scheme's class definition. Docstrings are tests that can be executed directly as follows: ``python -m doctest myScheme.py``. See examples in the ``schemes`` package.

There are several benchmark flags you should be aware of such as: ``RealTime``, ``CpuTime``, ``Add``, ``Sub``, ``Mul``, ``Div``, and ``Exp``. Here is an example to demonstrate use of the Charm benchmark interface for the EC setting:

::

	from charm.toolbox.ecgroup import ECGroup,ZR,G
	from charm.toolbox.eccurve import prime192v1

	trials = 10	
	group = ECGroup(prime192v1)
	g = group.random(G)
	h = group.random(G)
	i = group.random(G)

	assert group.InitBenchmark(), "failed to initialize benchmark"
	group.StartBenchmark(["Mul", "Div", "Exp", "Granular"])
	for a in range(trials):
	    j = g * h	
	    k = h ** group.random(ZR)
	    t = (j ** group.random(ZR)) / k
	group.EndBenchmark()

	msmtDict = group.GetGeneralBenchmarks()
	print("<=== General Benchmarks ===>")
	print("Mul := ", msmtDict["Mul"])
	print("Div := ", msmtDict["Div"])
	print("Exp := ", msmtDict["Exp"])
	granDict = group.GetGranularBenchmarks()
	print("<=== Granular Benchmarks ===>")
	print("G mul   := ", granDict["Mul"][G])	
	print("G exp   := ", granDict["Exp"][G])
	

Note that thesame benchmark function calls work for the other group settings as well. In particular, the pairing base module also supports the ability to perform benchmarks at a granular level (operation count per group). For this feature, import ``GetGranularBenchmarks`` in addition to ``GetGeneralBenchmarks`` in the ``pairing`` base module. Also, you are required to supply the ``Granular`` benchmark flag when calling ``StartBenchmark``. Here is an illustrative example:

::

	from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
	
	trials = 10	
	group = PairingGroup("SS1024")
	g = group.random(G1)
	h = group.random(G1)
	i = group.random(G2)

	assert group.InitBenchmark(), "failed to initialize benchmark"
	group.StartBenchmark(["Mul", "Exp", "Pair", "Granular"])
	for a in range(trials):
	    j = g * h	
	    k = i ** group.random(ZR)
	    t = (j ** group.random(ZR)) / h
	    n = pair(h, i)
	group.EndBenchmark()
	
	msmtDict = group.GetGeneralBenchmarks()
	granDict = group.GetGranularBenchmarks()
	print("<=== General Benchmarks ===>")
	print("Results  := ", msmtDict)
	print("<=== Granular Benchmarks ===>")
	print("G1 mul   := ", granDict["Mul"][G1])	
	print("G2 exp   := ", granDict["Exp"][G2])

In the integer module, we provide additional support for benchmarking without a group object:

::
	
	from charm.core.math.integer import *
	trials = 10	
	a = integer(1234)
	
	assert InitBenchmark(), "failed to initialize benchmark"
	StartBenchmark(["RealTime", "Exp", "Mul"])
	for k in range(trials):
	    r = randomPrime(512)
	    s = r * (r ** a)
	    j = r * (r ** a)	    
	EndBenchmark()
	
	msmtDict1 = GetGeneralBenchmarks()
	print("General Benchmarks: ", msmtDict1)



Optimizations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the pairing base module, we now support pre-computation tables for group exponentiation. Note that this speeds up exponentiation signifcantly. To take advantage of this, simply call the ``initPP()`` method on a given pairing object in ``G1``, ``G2``, or ``GT``. ``initPP()`` stores the pre-computed values for the given generator and any use of that variable in an exponentiation operation will automatically utilize the table. See how long it takes to compute 10 exponentiations with & without pre-computation:

::

	from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair

	count = 10	
	group = PairingGroup("MNT224")	
	g = group.random(GT)
	assert g.initPP(), "failed to init pre-computation table"
	h = group.random(GT)
	a, b = group.random(ZR, 2)
	
	assert group.InitBenchmark(), "failed to initialize benchmark"
	group.StartBenchmark(["RealTime"])
	for i in range(count):
	    A = g ** a
	group.EndBenchmark()
	print("With PP: ", group.GetBenchmark("RealTime"))

	assert group.InitBenchmark(), "failed to initialize benchmark"
	group.StartBenchmark(["RealTime"])
	for i in range(count):
	    B = h ** b
	group.EndBenchmark()
	print("Without: ", group.GetBenchmark("RealTime"))
	


Feel free to send us suggestions, bug reports, issues and scheme implementation experiences within Charm at support@charm-crypto.com.

