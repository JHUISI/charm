'''
``bistring.Bytes`` is a replacement for Python's ``byte``.
'''

import string

class Bytes(bytes):
    def __init__(self, value, enc=None):
        if enc != None:
           bytes.__init__(value, enc)
        else:
           bytes.__init__(value)

    def __xor__(self, other):
        '''Overload the ``^`` operator to provide xor '''
        if len(self) != len(other):
            assert False, "Xor: operands differ in length."
        res = bytearray()
        for i in range(0,len(self)):
            res.append(self[i] ^ other[i])
        return Bytes(res)            

    def __add__(self, other):
        return Bytes(bytes.__add__(self, other))
    
    @classmethod
    def fill(self, prefix, length):
        '''Provides an easy way to create a byte array of a specified length and content'''
        bits = b''
        for i in range(0, length):
            bits += prefix
        return Bytes(bits)

# TODO: add left and right bit shifting
