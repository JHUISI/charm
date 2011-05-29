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
        res = b''
        for i in range(0,len(self)):
            s,t = self[i], other[i]
            res += Bytes(chr(s ^ t), 'utf8')
        return Bytes(res)            

    def __add__(self, other):
        return Bytes(bytes.__add__(self, other))

    @classmethod
    def random(self, length):
        bits = random.sample(string.printable, length)
        rand = ""
        for i in bits: rand += i
        return Bytes(rand, 'utf8')
    
    @classmethod
    def fill(self, prefix, length):
        bits = b''
        for i in range(0, length):
            bits += Bytes(prefix, 'utf8')
        return Bytes(bits)

# TODO: add left and right bit shifting
