For App Developers
====================================

.. sectionauthor:: J. Ayo Akinyele

This guide provides application developers with the essential information needed to
integrate Charm cryptographic schemes into their applications.

.. rubric:: Installation and Dependencies

See :ref:`platform-install-manual` for installation instructions.

.. rubric:: Using a Scheme

To use any of our existing schemes in your application, each scheme includes a ``main``
routine that runs through every algorithm (with sample inputs) defined for that scheme.
Thus, the ``main`` function provides a test that the scheme works in addition to
demonstrating how to use it.

**Example:** Instantiating the Cramer-Shoup public-key encryption scheme:

.. code-block:: python

    from charm.schemes.pkenc.pkenc_cs98 import CS98
    from charm.toolbox.eccurve import prime192v1
    from charm.toolbox.ecgroup import ECGroup

    groupObj = ECGroup(prime192v1)
    pkenc = CS98(groupObj)

    (pk, sk) = pkenc.keygen()

    M = b'Hello World!'
    ciphertext = pkenc.encrypt(pk, M)

    message = pkenc.decrypt(pk, sk, ciphertext)

For a full list of schemes available, see the :ref:`schemes` section. For adapters that
extend scheme functionality (such as hybrid encryption), see the :ref:`adapters` section.

.. rubric:: Using the Serialization API

To support serialization of key material and ciphertexts, we provide two high-level
API calls to serialize Charm objects embedded in arbitrary Python structures
(e.g., lists, tuples, or dictionaries):

* ``objectToBytes()`` - Converts Charm objects to base64-encoded byte strings
* ``bytesToObject()`` - Reconstructs Charm objects from serialized byte strings

Both functions are available from the ``charm.core.engine.util`` package and require:

1. The object to be serialized/deserialized
2. A class that defines ``serialize`` and ``deserialize`` methods (such as a group object)

**Basic Usage Example:**

The following example demonstrates serialization with any supported group object
(``IntegerGroup``, ``PairingGroup``, or ``ECGroup``):

.. code-block:: python

    from charm.core.engine.util import objectToBytes, bytesToObject

    # Serialize a public key to bytes
    pk_bytes = objectToBytes(pk, group)

    # Deserialize back to original object
    orig_pk = bytesToObject(pk_bytes, group)

**Custom Serialization Example:**

For schemes based on ``IntegerGroup`` that do not utilize a group object, you can
define a custom serialization class:

.. code-block:: python

    from charm.core.math.integer import integer, serialize, deserialize

    class MySerializeAPI:
        def __init__(self):
            pass

        def serialize(self, charm_object):
            assert type(charm_object) == integer, \
                f"required type is integer, not: {type(charm_object)}"
            return serialize(charm_object)

        def deserialize(self, data):
            assert type(data) == bytes, \
                f"required type is bytes, not: {type(data)}"
            return deserialize(data)

Then use your custom serializer with the standard API:

.. code-block:: python

    from charm.core.engine.util import objectToBytes, bytesToObject

    serObject = MySerializeAPI()

    pk_bytes = objectToBytes(pk, serObject)
    orig_pk = bytesToObject(pk_bytes, serObject)

.. rubric:: Using Charm in C/C++ Applications

Charm provides a C interface to facilitate integration with C/C++ applications. While this
feature is still in development, it enables you to use Charm cryptographic schemes directly
from native code.

The C API provides the following key functions:

* ``InitializeCharm()`` / ``CleanupCharm()`` - Initialize and tear down the Charm environment
* ``InitPairingGroup(curve)`` - Initialize a pairing group with the specified curve
* ``InitClass(module, class, group)`` - Load a Charm scheme class
* ``CallMethod(obj, method, format, ...)`` - Call a method on a Charm object
* ``GetIndex(obj, idx)`` - Extract an element from a tuple or list
* ``Free(obj)`` - Release a Charm object

**Example:** Using the BSW07 CP-ABE scheme from C:

.. code-block:: c

    /* Charm C interface header */
    #include "charm_embed_api.h"

    Charm_t *module, *group, *class;

    /* Initialize Charm environment */
    InitializeCharm();

    /* Initialize a pairing group */
    group = InitPairingGroup("SS1024");

    /* Initialize the CP-ABE scheme */
    class = InitClass("abenc_bsw07", "CPabe_BSW07", group);

    /* Call setup algorithm */
    Charm_t *master_keys = CallMethod(class, "setup", "");

    Charm_t *pkDict = GetIndex(master_keys, 0);
    Charm_t *mskDict = GetIndex(master_keys, 1);

    /* Call keygen algorithm with attributes */
    Charm_t *skDict = CallMethod(class, "keygen", "%O%O%A",
                                  pkDict, mskDict, "[ONE, TWO, THREE]");

    /* Generate a random message in GT */
    Charm_t *msg = CallMethod(group, "random", "%I", GT);

    /* Call encrypt algorithm with access policy */
    Charm_t *ctDict = CallMethod(class, "encrypt", "%O%O%s",
                                  pkDict, msg,
                                  "((THREE or ONE) and (THREE or TWO))");

    /* Call decrypt to recover message */
    Charm_t *msg2 = CallMethod(class, "decrypt", "%O%O%O",
                                pkDict, skDict, ctDict);

    /* Process the Charm objects as needed */
    /* ... see source for details ... */

    /* Free all objects */
    Free(module);
    Free(group);
    Free(class);
    Free(master_keys);
    Free(pkDict);
    Free(mskDict);
    Free(skDict);
    Free(msg);
    Free(msg2);

    /* Tear down the environment */
    CleanupCharm();

The complete example can be found in ``test.c`` in the ``embed`` directory of the Charm source.

.. rubric:: Contact

Feel free to send us suggestions, bug reports, issues, and scheme implementation experiences
at **jakinye3@jhu.edu**.
