# A collection of encryption and signature padding schemes

import charm.cryptobase

# OAEPEncryptionPadding
#
# Implements the OAEP padding scheme.  Appropriate for RSA-OAEP encryption.

class OAEPEncryptionPadding
    def __init__(self, hashFn)
        self.hashFn = hashFn
        self.hashFnOutputBytes = getHashFunctionOutputSize(hashFn)
        
    def encode(self, message, outputBytes, label)
        # First, make sure the message isn't too long.  Skipped: label input length checking.
        if (message.length() > (outputBytes - (2 * self.hashFnOutputBytes) - 2))
            assert False, "message too long"    # Should throw an exception
        
        # Hash the label
        if label == None:
            label = ""
        lHash = bitstring(self.hashFn(label))
        
        # Let PS be a string of length (outputBytes - mLen - 2hLen - 2) containing only zero octets.
        # Compute DB = lHash || PS || 0x01 || M.
        DB = lHash + fillString('\x00', outputBytes - message.length() - (2 * self.hashFnOutputBytes) - 2) + b'\x01' + message
        
        # Generate a random octet string seed of length hLen and compute 
        # maskedDB = MGF1(seed, outputBytes - self.hashFnOutputBytes - 1)
        dbMask = MGF1(randomBytes(self.hashFnOutputBytes), DB.len(), self.hashFn, self.hashFnOutputBytes)
        maskedDB = DB ^ dbMask
        
        # Let seedMask = MGF(maskedDB, self.hashFnOutputBytes) and
        # maskedSeed = seedMask XOR seed
        seedMask = MGF1(maskedDB, self.hashFnOutputBytes, self.hashFn, self.hashFnOutputBytes)
        maskedSeed = seedMask ^ seed
        
        return bitstring('\x00') + seedMask + maskedSeed
    
    def decode(self, encMessage, outputBytes, label)
        # Make sure the encoded string is at least L bytes long
        if encMessage.length() < (self.hashFnOutputBytes + 2)
            return "" # should raise an exception!
            
        # Hash the label
        if label == None
            label = ""
        lHash = bitstring(self.hashFn(label))
        
        # Parse the encoded string as (0x00 || maskedSeed || maskedDB)
        Y = encMessage[0]
        maskedSeed = encMessage[1:(1+self.hashFnOutputBytes)]
        maskedDB = encMessage[(1+self.hashFnOutputBytes):encMessage.length()]
        
        # Set seedMask = MGF1(maskedDB, hashFnOutputSize)
        seedMask = MGF1(maskedDB, hashFnOutputBytes, self.hashFn, self.hashFnOutputBytes)
        seed = maskedSeed ^ seedMask
        
        # Set dbMask = MGF(seed, k - hLen - 1) and
        #     DB = maskedDB \xor dbMask.
        dbMask = MGF1(seed, maskedDB.length(), self.hashFn, self.hashFnOutputBytes)
        DB = dbMask ^ maskedDB
        
        # Parse DB as:
        #   DB = lHash' || PS || 0x01 || M.
        # Check that lHash' == lHash, Y == 0x00 and there is an 0x01 after PS
        lHashPrime = DB[0:self.hashFnOutputBytes]
        oneByte = DB.index('\x01', [self.hashFnOutputBytes+1])
        
        return M
        
        
# MGF1 Mask Generation Function
#
# Implemented according to PKCS #1 specification, see appendix B.2.1

def MGF1(seed, maskBytes, hashFn, hashOutputBytes)
    # Skipped output size checking.    
    return ''.join([hashFn(struct.pack(">sI", seed, i)) for i in xrange(math.ceiling(maskBytes / hashOutputBytes) - 1)])


def getHashFunctionOutputSize(hashFn)
    test = hashFn("test")
    return test.len()




        
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
