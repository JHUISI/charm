# A collection of encryption and signature padding schemes
import charm.cryptobase
import hashlib, random
import string, math, struct
# OAEPEncryptionPadding
#
# Implements the OAEP padding scheme.  Appropriate for RSA-OAEP encryption.

class OAEPEncryptionPadding:
    def __init__(self, _hash_type ='sha1'):
        self.hashFn = hashFunc(_hash_type)
        self.hashFnOutputBytes = len(hashlib.new(_hash_type).digest())
    # outputBytes = 64, label = 'X'    
    def encode(self, message, outputBytes, label=None):
        # First, make sure the message isn't too long.  Skipped: label input length checking.
        if (len(message) > (outputBytes - (2 * self.hashFnOutputBytes) - 2)):
            print("Message Len: ", len(message))
            print("Required Min Len: ", (outputBytes - (2 * self.hashFnOutputBytes) - 2))
            assert False, "message too long"
        
        # Hash the label
        if label == None:
            label = ""

        lHash = self.hashFn(label)        
        # Let PS be a string of length (outputBytes - mLen - 2hLen - 2) containing only zero octets.
        # Compute DB = lHash || PS || 0x01 || M.
        DB = lHash + fillBytes('\x00', outputBytes - len(message) - (2 * self.hashFnOutputBytes) - 2) + b'\x01' + bytes(message, 'utf8')
        
#        print("DB =>", DB)
#        print("DB len =>", len(DB))
        # Generate a random octet string seed of length hLen and compute 
        # maskedDB = MGF1(seed, outputBytes - self.hashFnOutputBytes - 1)
        seed = randomBytes(self.hashFnOutputBytes)
        dbMask = MGF1(seed, len(DB), self.hashFn, self.hashFnOutputBytes)
        maskedDB = DB ^ dbMask
        
        # Let seedMask = MGF(maskedDB, self.hashFnOutputBytes) and
        # maskedSeed = seedMask XOR seed
#        print("maskedDB =>", maskedDB, "\n")
        seedMask = MGF1(maskedDB, self.hashFnOutputBytes, self.hashFn, self.hashFnOutputBytes)        
#        print("seedMask =>", seedMask)
#        print("seedMask len =>", len(seedMask))
        
        maskedSeed = seedMask ^ seed
#        print("maskedSeed =>", maskedSeed)
#        print("maskedSeed len =>", len(maskedSeed))
        return Bytes(b'\x00') + seedMask + maskedSeed
    
    def decode(self, encMessage, outputBytes, label=None):
        # Make sure the encoded string is at least L bytes long
        if len(encMessage) < (self.hashFnOutputBytes + 2):
            assert False, "encoded string not long enough."
            
        # Hash the label
        if label == None:
            label = ""
        lHash = self.hashFn(label)
        
        # Parse the encoded string as (0x00 || maskedSeed || maskedDB)
        Y = encMessage[0]
        maskedSeed = Bytes(encMessage[1:(1+self.hashFnOutputBytes)])
        maskedDB = Bytes(encMessage[(1+self.hashFnOutputBytes):len(encMessage)])
        
        # Set seedMask = MGF1(maskedDB, hashFnOutputSize)
        seedMask = MGF1(maskedDB, self.hashFnOutputBytes, self.hashFn, self.hashFnOutputBytes)
        seed = maskedSeed ^ seedMask
        
        # Set dbMask = MGF(seed, k - hLen - 1) and
        #     DB = maskedDB \xor dbMask.
        dbMask = MGF1(seed, len(maskedDB), self.hashFn, self.hashFnOutputBytes)
        DB = dbMask ^ maskedDB
        
        # print("Result DB =>", DB)        
        # Parse DB as:
        #   DB = lHash' || PS || 0x01 || M.
        # Check that lHash' == lHash, Y == 0x00 and there is an 0x01 after PS
        lHashPrime = DB[0 : self.hashFnOutputBytes]        
        M = DB[DB.find('\x01')+1 : self.hashFnOutputBytes]
        return M

class Bytes(bytes):
    def __init__(self, value, enc=None):
        #print("value =>", value, ", type =>", type(value))
        if enc != None:
           bytes.__init__(value, enc)
        else:
           bytes.__init__(value)

    def __xor__(self, other):
        #print("self =>", self); print("others =>", others)
        if len(self) != len(other):
            assert False, "Xor: operands differ in length."
        res = b''
        for i in range(0,len(self)):
            s,t = self[i], other[i]
            res += Bytes(chr(s ^ t), 'utf8') # should be a string
        # print("res =>", res)
        return Bytes(res)            
        
    def __add__(self, other):
        return Bytes(bytes.__add__(self, other))
# MGF1 Mask Generation Function
#
# Implemented according to PKCS #1 specification, see appendix B.2.1:
def MGF1(seed, maskBytes, hashFn, hashOutputBytes):
    # Skipped output size checking.    
#    result = b''.join([hashFn(struct.pack(">sI", seed, i)) for i in range(math.ceil(maskBytes / hashOutputBytes) - 1)])
    # print("maskBytes =>", maskBytes) # TODO: ERROR HERE!!!
    ran = range(math.ceil(maskBytes / hashOutputBytes) - 1)
    # print("calc =>", math.ceil(maskBytes / hashOutputBytes))
    # print("Range =>", ran)
    test = [hashFn(struct.pack(">sI", seed, i)) for i in ran]
#    print("test =>", test)
    result = b''.join(test)
    diff = maskBytes - len(result)
    result2 = result + fillBytes('\x00', diff)
    return Bytes(result2)

def fillBytes(prefix, length):
    bits = b''
    for i in range(0, length):
        bits += Bytes(prefix, 'utf8')
    return Bytes(bits)

def randomBytes(length):
    bits = random.sample(string.printable, length)
    rand = ""
    for i in bits: rand += i
    return Bytes(rand, 'utf8')


class hashFunc:
    def __init__(self, _hash_type=None):
        if _hash_type == None:
            self.hashObj = hashlib.new('sha1')
        else:
            self.hashObj = hashlib.new(_hash_type)
        
    def __call__(self, message):
        h = self.hashObj.copy()
        h.update(bytes(str(message), 'utf8'))
        return Bytes(h.digest())  
# PSSSignaturePadding
#
# Implements the PSS signature padding scheme.  Appropriate for RSA-PSS signing.

#class PSSPadding
#    def __init__(self, outputBits, randomBits)
#        self.outputBits = outputBits
#        self.randomBits = randomBits
#        
#    def encode(self, N, message)
#        # Pick 'randomBits' random bits
#        return encoded
        
#    def validate(self)
#        # undo the result
#        return decoded
