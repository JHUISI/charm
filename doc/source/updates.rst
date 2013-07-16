Changes in v0.43
=======================

Integer Module
^^^^^^^^^^^^^^^^^^^^^^^^

- ``reduce()`` method no longer a field of integer object, but rather a class method. 

::

	from charm.core.math.integer import *

	a = integer(7, 5)
	b = reduce(a)
	print("a = ", a)
	print("b = ", b)

- Note that certain mixing of integer objects and Python ``int`` no longer supported. For example, ``integer(10, 17) * -1`` will generate a runtime exception: 


Benchmarking
^^^^^^^^^^^^^^^^^^^^^

- Benchmark API now part of group abstraction class which eliminates need for importing the benchmark methods.
- Removed the ``ID`` handle returned by ``InitBenchmark``.
- No longer necessary to call ``ClearBenchmark()`` to clear benchmarking state.
- Benchmarking options are strings instead of int values. That is, ``"RealTime"``, ``"CpuTime"``, ``"Add"``, ``"Sub"``, ``"Mul"``, ``"Div"``, ``"Exp"``, ``"Pair"``, and ``"Granular"``.
- Both pairing and elliptic curve modules now support collection of granular benchmarks.  


Serialization
^^^^^^^^^^^^^^^^^^^^^
- We have deprecated the use of Pickle as a primary serilization method. Pickle contains a serious vulnerability that could lead to arbitrary code execution. It has been replaced by a safer implementation based on JSON module.
- For backwards compatibility, the Pickle methods are still available, but we output a warning that it is vulnerable. The Pickle methods are now ``objectToBytesWithPickle`` and ``bytesToObjectWithPickle``.
