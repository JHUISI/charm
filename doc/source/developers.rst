For App Developers
====================================
Installation and dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
See :ref:`platform-install-manual` for installation instructions.

Using a Scheme
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To use any of our existing schemes in your application, each scheme includes a ``main`` routine that runs through every alorithm (with sample inputs) defined for that scheme. Thus, the ``main`` function provides a test that the scheme works in addition to demonstrate how to use it. For example, below is an example of how to instantiate the Cramer-Shoup scheme from above within your application:

::

	from schemes.pkenc.pkenc_cs98.py import CS98
	from charm.toolbox.eccurve import prime192v1
	from charm.toolbox.ecgroup import ECGroup
	
	groupObj = ECGroup(prime192v1)
	pkenc = CS98(groupObj)
	
	(pk, sk) = pkenc.keygen()

	M = b'Hello World!'	
	ciphertext = pkenc.encrypt(pk, M)    

    	message = pkenc.decrypt(pk, sk, ciphertext)

For a full list of schemes that are available to you, see the :ref:`schemes` section.

Using serialization API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To support serialization of key material and ciphertexts, we provide two high-level API calls to serialize charm objects embedded in arbitrary python structures (e.g., lists, tuples, or dictionaries, etc) which are ``objectToBytes()`` and ``bytesToObject()`` from the ``charm.engine.util`` package. These functions provide the necessary functionality for converting keys and ciphertexts to base 64 encoded strings. Both calls require the object to be serialized/deserialized and a class that defines the serialize and deserialize methods such as the group object. 
We also show below how to customize our serialization routines: 

Here is an example of how to use the API with any of the supported group objects (``integergroup``, ``pairinggroup`` or ``ecgroup``):

::

	from charm.engine.util import objectToBytes,bytesToObject
	
	pk_bytes = objectToBytes(pk, group)	

	orig_pk = bytesToObject(pk_bytes, group)

If you would like to define your own custom serialization routine in conjunction with our API, the following example works for schemes based on the ``integergroup`` which in some cases do not utilize a group object:

::

	from charm.core.math.integer import integer,serialize,deserialize
	
	class mySerializeAPI:
		def __init__(self)
			...
		
		def serialize(self, charm_object):
		    assert type(charm_object) == integer, "required type is integer, not: ", type(charm_object)
		    return serialize(charm_object)
		
		def deserialize(self, object):
		    assert type(object) == bytes, "required type is bytes, not: ", type(object)
		    return deserialize(object)


::

	from charm.engine.util import objectToBytes,bytesToObject
	
	serObject = mySerializeAPI()
	
	pk_bytes = objectToBytes(pk, serObject)	

	orig_pk = bytesToObject(pk_bytes, serObject) 

			
Using Charm in C/C++ Apps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO

Feel free to send us suggestions, bug reports, issues and scheme implementation experiences within Charm at support@charm-crypto.com.
