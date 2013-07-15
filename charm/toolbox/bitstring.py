'''
``bistring.Bytes`` is a replacement for Python's ``byte``.
'''

import string
import sys

py3 = False
if float(sys.version[:3]) >= 3.0:
    py3 = True


class Bytes(bytes):
    def __init__(self, value, enc=None):
        if enc != None:
           if py3: bytes.__init__(value, enc)
           else: bytes.__init__(value)
        else:
           bytes.__init__(value)

    def __xor__(self, other):
        '''Overload the ``^`` operator to provide xor '''
        assert len(self) == len(other), "xor: operands differ in length."
        res = bytearray()
        for i in range(0,len(self)):
            if py3: res.append(self[i] ^ other[i])
            else: res.append(chr(ord(self[i]) ^ ord(other[i])))
            #print("res[%s] = %s" % (i, res[i]))
        return Bytes(res)            

    def __add__(self, other):
        return Bytes(bytes.__add__(self, other))
    
    @classmethod
    def fill(self, prefix, length):
        '''Provides an easy way to create a byte array of a specified length and content'''
        bits = b''
        for i in range(0, int(length)):
            bits += prefix
        return Bytes(bits)
        

if py3:
   def getBytes(arg1, arg2='utf-8'):
       return Bytes(arg1, arg2)
else:
   def getBytes(arg1, arg2=None):
       return bytes(arg1)
# TODO: add left and right bit shifting
