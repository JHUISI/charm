import charm.core.crypto.cryptobase
from charm.core.math.pairing import pairing,pc_element,ZR
from charm.core.math.integer import integer,int2Bytes
from charm.toolbox.conversion import Conversion
from charm.toolbox.bitstring import Bytes
import hashlib, base64

class Hash():
    def __init__(self, pairingElement=None, htype='sha256', integerElement=None):
        self.hash_type = htype
        # instance of PairingGroup
        self.group = pairingElement
        
    def hashToZn(self, value):
        if type(value) == pc_element:
            h = hashlib.new(self.hash_type)
            h.update(self.group.serialize(value))
            #print "digest => %s" % h.hexdigest()
            # get raw bytes of digest and hash to Zr
            val = h.digest()
            return integer(int(self.group.hash(val, ZR)))
            # do something related to that
        if type(value) == integer:
            str_value = int2Bytes(value)
            #print("str_value =>", str_value)
            #val = self.group.hash(str_value, ZR)
            #print("hash =>", val)
            return integer(int(self.group.hash(str_value, ZR)))
        return None
    
    # takes two arbitrary strings and hashes to an element of Zr
    # Uses length-prefixed encoding to prevent input collision attacks
    # (e.g., hash("ab", "c") != hash("a", "bc"))
    def hashToZr(self, *args):
        if isinstance(args, tuple):
            import struct
            parts = []
            for i in args:
                if type(i) == str:
                    encoded = bytes(i, 'utf8')
                elif type(i) == bytes:
                    encoded = i
                elif type(i) == integer:
                    encoded = int2Bytes(i)
                elif type(i) == pc_element:
                    encoded = self.group.serialize(i)
                else:
                    continue
                # Length-prefix each input to prevent collision
                parts.append(struct.pack('>I', len(encoded)) + encoded)

            if len(parts) > 0:
                combined = b''.join(parts)
                strs = str(base64.encodebytes(combined))
                return self.group.hash(strs, ZR)
            return None
        

"""
Waters Hash technique: how to hash in standard model.
Default - len=8, bits=32 ==> 256-bits total (for SHA-256)
For SHA1, len=5 bits=32 ==> 160-bits total
"""
class Waters:
    """
    >>> from charm.toolbox.pairinggroup import *
    >>> from charm.toolbox.hash_module import Waters
    >>> group = PairingGroup("SS512")
    >>> waters = Waters(group, length=8, bits=32)
    >>> a = waters.hash("user@email.com")
    """
    def __init__(self, group, length=8, bits=32, hash_func='sha256'):
        self._group = group
        self._length = length
        self._bitsize = bits
        self.hash_function = hash_func
        self._hashObj = hashlib.new(self.hash_function)
        self.hashLen = len(self._hashObj.digest())

    def sha2(self, message):
        h = self._hashObj.copy()
        h.update(bytes(message, 'utf-8'))
        return Bytes(h.digest())    
    
    def hash(self, strID):
        '''Hash the identity string and break it up in to l bit pieces'''
        assert type(strID) == str, "invalid input type"
        hash = self.sha2(strID)
        
        val = Conversion.OS2IP(hash) #Convert to integer format
        bstr = bin(val)[2:]   #cut out the 0b header

        v=[]
        for i in range(self._length):  #z must be greater than or equal to 1
            binsubstr = bstr[self._bitsize*i : self._bitsize*(i+1)]
            intval = int(binsubstr, 2)
            intelement = self._group.init(ZR, intval)
            v.append(intelement)
        return v
