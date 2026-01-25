'''
**Key Encapsulation Mechanism (BCHK05)**

*Authors:* Based on commitment scheme constructions

| **Title:** "Key Encapsulation from Commitment Schemes"
| **Notes:** Simple hash-based encapsulation scheme

.. rubric:: Scheme Properties

* **Type:** key encapsulation mechanism (KEM)
* **Setting:** hash-based
* **Assumption:** random oracle

.. rubric:: Implementation

:Authors: Charm Developers
:Date: Unknown
'''


from charm.core.math.integer import randomBits
import hashlib

debug = False
class EncapBCHK():
    """
    >>> encap = EncapBCHK()
    >>> hout = encap.setup()
    >>> (r, com, dec) = encap.S(hout)
    >>> rout = encap.R(hout, com, dec)
    >>> r == rout
    True
    """
    def __init__(self):
        global H
        H = hashlib.sha1()  # nosec B324 - SHA1 used for historical compatibility

    def setup(self):
        pub = hashlib.sha256()
        return pub

    def S(self, pub):
        x = randomBits(448)
        x = str(x).zfill(135)

        r = hashlib.sha256(x.encode('utf-8')).digest()

        com = hashlib.sha1(x.encode('utf-8')).digest()[:128]  # nosec B324

        dec = x

        return (r, com, dec)

    def R(self, pub, com, dec):
        x = hashlib.sha1(str(dec).encode('utf-8')).digest()[:128]  # nosec B324

        if(x == com):
            m = hashlib.sha256(str(dec).encode('utf-8')).digest()
            return m
        else:
            return b'FALSE'
