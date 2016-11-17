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
        H = hashlib.sha1()

    def setup(self):
        pub = hashlib.sha256()
        return pub

    def S(self, pub):
        x = randomBits(448)
        x = str(x).zfill(135) 

        r = hashlib.sha256(x.encode('utf-8')).digest()

        com = hashlib.sha1(x.encode('utf-8')).digest()[:128]

        dec = x

        return (r, com, dec)

    def R(self, pub, com, dec):
        x = hashlib.sha1(str(dec).encode('utf-8')).digest()[:128]
        
        if(x == com):
            m = hashlib.sha256(str(dec).encode('utf-8')).digest()
            return m
        else:
            return b'FALSE'
