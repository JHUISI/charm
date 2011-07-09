import charm.cryptobase
from charm.pairing import *
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
            return integer(int(self.e.H(val, ZR)))
            # do something related to that
        if type(value) == integer:
            print("value =>", value)
            str_value = int2Bytes(value)
            return integer(int(self.e.H(str_value, ZR)))
        return None
    
    # takes two arbitrary strings and hashes to an element of Zr
    def hashToZr(self, *args):
        if isinstance(args, tuple):
            #print("Hashing =>", args)
            strs = ""
            for i in args:
                if type(i) == str:
                    strs += str(base64.encodebytes(bytes(i, 'utf8')))
                elif type(i) == bytes:
                    strs += str(base64.encodebytes(i))
                elif type(i) == integer:
                    strs += str(base64.encodebytes(int2Bytes(i)))
                elif type(i) == pairing:
                    strs += str(base64.encodebytes(self.e.serialize(i)))

            if len(strs) > 0:
                return self.e.H(strs, ZR)
            return None
        