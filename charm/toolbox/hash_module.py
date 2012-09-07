try:
  import charm.core.crypto.cryptobase
  from charm.core.math.pairing import pairing,ZR
  from charm.core.math.integer import integer,int2Bytes
  from charm.toolbox.conversion import Conversion
  from charm.toolbox.bitstring import Bytes
  import hashlib, base64
except Exception as err:
  print(err)
  exit(-1)

class Hash():
    def __init__(self, htype='sha1', pairingElement=None, integerElement=None):        
        if htype == 'sha1':
            self.hash_type = htype 
            # instance of PairingGroup
            self.group = pairingElement
        
    def hashToZn(self, value):
        if type(value) == pairing:
            h = hashlib.new(self.hash_type)
            h.update(self.group.serialize(value))
            #print "digest => %s" % h.hexdigest()
            # get raw bytes of digest and hash to Zr
            val = h.digest()
            return integer(int(unicode(self.group.hash(val, ZR))))
            # do something related to that
        if type(value) == integer:
            str_value = int2Bytes(value)
            #print("str_value =>", str_value)
            #val = self.group.hash(str_value, ZR)
            #print("hash =>", val)
            return integer(int(unicode(self.group.hash(str_value, ZR))))
        return None
    
    # takes two arbitrary strings and hashes to an element of Zr
    def hashToZr(self, *args):
        if isinstance(args, tuple):
            #print("Hashing =>", args)
            strs = ""
            for i in args:
                if type(i) == unicode:
                    strs += unicode(base64.encodestring(i))
                elif type(i) == bytes:
                    strs += unicode(base64.encodestring(i))
                elif type(i) == integer:
                    strs += unicode(base64.encodestring(int2Bytes(i)))
                elif type(i) == pairing:
                    strs += unicode(base64.encodestring(self.group.serialize(i)))

            if len(strs) > 0:
                return self.group.hash(strs, ZR)
            return None
        

"""
Waters Hash technique: how to hash in standard model.
Default - len=5 bits=32 ==> 160-bits total
"""
class Waters:
    """
    >>> from charm.toolbox.pairinggroup import *
    >>> from charm.toolbox.hash_module import Waters
    >>> group = PairingGroup("SS512")
    >>> waters = Waters(group, length=5, bits=32)
    >>> a = waters.hash("user@email.com")
    """
    def __init__(self, group, length=5, bits=32, hash_func='sha1'):
        self._group = group
        self._length = length
        self._bitsize = bits
        self.hash_function = hash_func
        self._hashObj = hashlib.new(self.hash_function)
        self.hashLen = len(self._hashObj.digest())

    def sha1(self, message):
        h = self._hashObj.copy()
        h.update(message)
        return Bytes(h.digest())    
    
    def hash(self, strID):
        '''Hash the identity string and break it up in to l bit pieces'''
        assert type(strID) == str, "invalid input type"
        hash = self.sha1(strID)
        
        val = Conversion.OS2IP(hash) #Convert to integer format
        bstr = bin(val)[2:]   #cut out the 0b header

        v=[]
        for i in range(self._length):  #z must be greater than or equal to 1
            binsubstr = bstr[self._bitsize*i : self._bitsize*(i+1)]
            intval = int(binsubstr, 2)
            intelement = self._group.init(ZR, intval)
            v.append(intelement)
        return v
