import charm.cryptobase
from charm.pairing import *
from charm.integer import *
from bitstring import *

import hashlib

class Hash():
    def __init__(self, htype='sha1', pairingElement=None, integerElement=None):        
        if htype == 'sha1':
            self.hash_type = htype 
            self.e = pairingElement
        
    def hashToZn(self, value):
        if type(value) == pairing:
            h = hashlib.new(self.hash_type)
            h.update(value.serialize())
            #print "digest => %s" % h.hexdigest()
            # get raw bytes of digest and hash to Zr
            val = h.digest()
            return int(self.e.H(val, ZR))
            # do something related to that
        if type(value) == long:
            val = BitString(bin(value)).bin
            return int(self.e.H(val, ZR))
        return None
    
    # takes two arbitrary strings and hashes to an element of Zr
    def hashToZr(self, *args):
        if isinstance(args, tuple):
            strs = ""
            for i in args:
                if type(i) == str:
                    strs += BitString(bytes=i).bin
                else:
                    strs += BitString(bin(i)).bin
            if len(strs) > 0:
                return self.e.H(strs, 'Zr')
            return None
