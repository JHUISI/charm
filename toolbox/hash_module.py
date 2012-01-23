from __future__ import print_function
import charm.cryptobase
from toolbox.pairinggroup import *
from charm.integer import *
import hashlib, base64

class Hash():
    def __init__(self, htype='sha1', pairingElement=None, integerElement=None):        
        if htype == 'sha1':
            self.hash_type = htype 
            self.e = pairingElement
        
    def hashToZn(self, value):
        if type(value) == pairing:
            h = hashlib.new(self.hash_type)
            h.update(self.e.serialize(value))
            #print "digest => %s" % h.hexdigest()
            # get raw bytes of digest and hash to Zr
            val = h.digest()
            return integer(int(self.e.hash(val, ZR)))
            # do something related to that
        if type(value) == integer:
            str_value = int2Bytes(value)
            return integer(int(self.e.hash(str_value, ZR)))
        return None
    
    # takes two arbitrary strings and hashes to an element of Zr
    def hashToZr(self, *args):
        if isinstance(args, tuple):
            #print("Hashing =>", args)
            strs = unicode("")
            for i in args:
                if type(i) == unicode:
                    strs += unicode(base64.encodestring(i))
                elif type(i) == bytes:
                    strs += unicode(base64.encodestring(i))
                elif type(i) == integer:
                    strs += unicode(base64.encodestring(int2Bytes(i)))
                elif type(i) == pairing:
                    strs += unicode(base64.encodestring(self.e.serialize(i)))

            if len(strs) > 0:
                return self.e.hash(strs, ZR)
            return None
        
