import random, string

class Bytes(bytes):
    def __init__(self, value, enc=None):
        if enc != None:
           bytes.__init__(value, enc)
        else:
           bytes.__init__(value)

    def __xor__(self, other):
        if len(self) != len(other):
            assert False, "Xor: operands differ in length."
        res = bytearray()
        for i in range(0,len(self)):
            res.append(self[i] ^ other[i])
        return Bytes(res)            

    def __add__(self, other):
        return Bytes(bytes.__add__(self, other))

    @classmethod
    def random(self, length, printable=False):
        '''This method does NOT provide cryptographically secure random numbers
        This should NOT be used for production code
        '''
        
        if(printable):
            #Nice printable characters for testing purposes
            return bytes(random.randrange(0x20, 0x7E) for i in range(length))
        else:
            return bytes(random.randrange(0, 256) for i in range(length))
    
    @classmethod
    def fill(self, prefix, length):
        bits = b''
        for i in range(0, length):
            bits += prefix
        return Bytes(bits)

# TODO: add left and right bit shifting
