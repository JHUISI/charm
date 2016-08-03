'''A collection of encryption and signature padding schemes'''
from charm.toolbox.bitstring import Bytes,py3
from charm.toolbox.securerandom import SecureRandomFactory
import charm.core.crypto.cryptobase
import hashlib
import math
import struct
import sys

debug = False


class OAEPEncryptionPadding:
    '''
    :Authors: Gary Belvin
    
    OAEPEncryptionPadding
    
    Implements the OAEP padding scheme.  Appropriate for RSA-OAEP encryption.
    Implemented according to PKCS#1 v2.1 Section 7 ftp://ftp.rsasecurity.com/pub/pkcs/pkcs-1/pkcs-1v2-1.pdf
    '''
    def __init__(self, _hash_type ='sha1'):
        self.name = "OAEPEncryptionPadding"
        self.hashFn = hashFunc(_hash_type)
        self.hashFnOutputBytes = len(hashlib.new(_hash_type).digest())
        
    # outputBytes - the length in octets of the RSA modulus used
    #             - the intended length of the encoded message 
    # emLen = the length of the rsa modulus in bits
    def encode(self, message, emLen, label="", seed=None):
        ''':Return: a Bytes object'''
        # Skipped: label input length checking. (L must be less than 2^61 octets for SHA1)
        # First, make sure the message isn't too long.    emLen
        hLen = self.hashFnOutputBytes
        if (len(message) > (emLen - (2 * hLen) - 2)):
            assert False, "message too long"
        
        if py3: lHash = self.hashFn(Bytes(label, 'utf8'))
        else: lHash = self.hashFn(Bytes(label))  
              
        # Let PS be a string of length (emLen - mLen - 2hLen - 2) containing only zero octets.
        # Compute DB = lHash || PS || 0x01 || M.
        PS = Bytes.fill(b'\x00', emLen - len(message) - (2 * hLen) - 2)
        DB = lHash + PS + b'\x01' + bytes(message)
        
        # Generate a random octet string seed of length hLen and compute 
        # maskedDB = MGF1(seed, emLen - self.hashFnOutputBytes - 1)
        if (seed is None):
            rand = SecureRandomFactory.getInstance()
            seed = rand.getRandomBytes(hLen)
            
        dbMask = MGF1(seed, len(DB), self.hashFn, hLen)

        maskedDB = DB ^ dbMask
        
        # Let seedMask = MGF(maskedDB, self.hashFnOutputBytes) and
        # maskedSeed = seedMask XOR seed
        seedMask = MGF1(maskedDB, len(seed), self.hashFn, hLen)        
        maskedSeed = seedMask ^ seed
        if(debug):
            print("Encoding")
            print("label    =>", label)
            print("lhash    =>", lHash)
            print("seed     =>", seed)
            print("db       =>", DB)
            print("db len   =>", len(DB))
            print("db mask  =>", dbMask)
            print("maskedDB =>", maskedDB)
            print("seedMask =>", seedMask)
            print("maskedSed=>", maskedSeed)
      
        return Bytes(b'\x00') + maskedSeed + maskedDB
    
    def decode(self, encMessage, label=""):
        hLen = self.hashFnOutputBytes
        # Make sure the encoded string is at least L bytes long
        if len(encMessage) < (2 * hLen + 2):
            assert False, "encoded string not long enough."
        if py3: lHash = self.hashFn(Bytes(label, 'utf-8'))
        else: lHash = self.hashFn(Bytes(label))
        # Parse the encoded string as (0x00 || maskedSeed || maskedDB)
        #Y = encMessage[0]
        maskedSeed = Bytes(encMessage[1:(1+hLen)])
        maskedDB = Bytes(encMessage[(1+hLen):])

        # Set seedMask = MGF1(maskedDB, hashFnOutputSize)
        seedMask = MGF1(maskedDB, len(maskedSeed), self.hashFn, hLen)
        seed = maskedSeed ^ seedMask           
        
        # Set dbMask = MGF(seed, k - hLen - 1) and
        #     DB = maskedDB \xor dbMask.
        dbMask = MGF1(seed, len(maskedDB), self.hashFn, hLen)
        DB = dbMask ^ maskedDB
        if(debug):
            print("decoding:")
            print("MaskedSeed => ", maskedSeed)
            print("maskedDB   => ", maskedDB)
            print("r seed =>", seed)
            print("r DB   =>", DB)
                
        # Parse DB as:
        #   DB = lHash' || PS || 0x01 || M.
        # Check that lHash' == lHash, Y == 0x00 and there is an 0x01 after PS
        lHashPrime = DB[0 : hLen]        
        M = DB[DB.find(b'\x01')+1 : ]
        return M

#def MGF1(seed:Bytes, maskBytes:int, hashFn, hLen:int):
def MGF1(seed, maskBytes, hashFn, hLen):
    ''' MGF1 Mask Generation Function
    
    Implemented according to PKCS #1 specification, see appendix B.2.1:
    
    :Parameters:
       - ``hLen``: is the output length of the hash function
       - ``maskBytes``: the number of mask bytes to return
    '''
    debug = False
    # Skipped output size checking.  Must be less than 2^32 * hLen
    ran = range(int(math.ceil(maskBytes / float(hLen))))
    if debug:
        print("calc =>", math.ceil(maskBytes / float(hLen)))
        print("Range =>", ran)
    test = [hashFn(struct.pack(">%dsI" % (len(seed)), seed, i)) for i in ran]
    if debug: 
        print("test =>", test)
    result = b''.join(test)
    return Bytes(result[0:maskBytes])

class hashFunc:
    def __init__(self, _hash_type=None):
        if _hash_type == None:
            self.hashObj = hashlib.new('sha1')
        else:
            self.hashObj = hashlib.new(_hash_type)
        
    #message must be a binary string
    def __call__(self, message):
        h = self.hashObj.copy()
        if type(message) == str:
            h.update(bytes(message))
        elif type(message) in [bytes, Bytes]:
            h.update(bytes(message)) # bytes or custom Bytes
        return Bytes(h.digest())  
    
class PSSPadding:
    '''
    :Authors: Gary Belvin
    
    PSSSignaturePadding
    
    Implements the PSS signature padding scheme.  Appropriate for RSA-PSS signing. 
    Implemented according to section 8 of ftp://ftp.rsasecurity.com/pub/pkcs/pkcs-1/pkcs-1v2-1.pdf.
    '''
    def __init__(self, _hash_type ='sha1'):
        self.hashFn = hashFunc(_hash_type)
        self.hLen = len(hashlib.new(_hash_type).digest())
        self.sLen = self.hLen # The length of the default salt
    
    def encode(self, M, emBits=None, salt=None):
        '''Encodes a message with PSS padding
        emLen will be set to the minimum allowed length if not explicitly set
        '''
        # assert len(M) < (2^61 -1), Message too long
        
        #Let H' = Hash (M'), an octet string of length hLen.
        #Max length of output message
        if emBits is None:
            emBits =  8*self.hLen + 8 * self.sLen + 9
            #Round to the next byte
            emBits = int(math.ceil(emBits / 8.0)) * 8
        assert emBits >= 8*self.hLen + 8 * self.sLen + 9, "Not enough emBits"
        
        #Make sure the the message is long enough to be valid
        emLen = int(math.ceil(emBits / 8.0))        
        assert emLen >= self.hLen + self.sLen + 2, "emLen too small"
        
        if salt is None:
            if self.sLen > 0: 
                salt = SecureRandomFactory.getInstance().getRandomBytes(self.sLen)
            else:
                salt = b''
        assert len(salt) == self.sLen, "Salt wrong size"
        
        #Let M' = (0x)00 00 00 00 00 00 00 00 || mHash || salt;
        eightzerobytes = Bytes.fill(b'\x00', 8)
        mHash = self.hashFn(M)        
        Mprime = eightzerobytes + mHash + salt
        
        #Let H = Hash (M'), an octet string of length hLen.
        H = self.hashFn(Mprime)
        
        #Generate an octet string PS consisting of emLen - sLen - hLen - 2 zero octets.
        #The length of PS may be 0.
        pslen = emLen - self.sLen - self.hLen - 2
        ps = Bytes.fill(b'\x00', pslen)        
        
        #Let DB = PS || 0x01 || salt; DB is an octet string of length emLen - hLen - 1.
        DB = ps + Bytes(b'\x01') + salt

        #Let dbMask = MGF (H, emLen - hLen - 1).
        masklen = emLen - self.hLen - 1
        dbMask = MGF1(H, masklen, self.hashFn, self.hLen)
        #Let maskedDB = DB ^ dbMask.
        maskedDB = DB ^ dbMask
        
        #Set the leftmost 8emLen - emBits bits of the leftmost octet in maskedDB to zero
        numzeros = 8 * emLen - emBits
        bitmask  = int('0'*numzeros + '1'*(8-numzeros), 2)
        ba = bytearray(maskedDB)
        ba[0] &= bitmask
        maskedDB = Bytes(ba)
        
        EM = maskedDB + H + Bytes(b'\xbc')
        
        if debug:
            print("PSS Encoding:")
            print("M     =>", M) 
            print("mHash =>", mHash)
            print("salt  =>", salt)
            print("M'    =>", Mprime)
            print("H     =>", H)
            print("DB    =>", DB)
            print("dbmask=>", dbMask)
            print("masked=>", maskedDB)
            print("EM    =>", EM)
        return EM
    
    def verify(self, M, EM, emBits=None):
        '''
        Verifies that EM is a correct encoding for M
        
        :Parameters:
           - M - the message to verify
           - EM - the encoded message
        :Return: true for 'consistent' or false for 'inconsistent'
        '''
        if debug: print("PSS Decoding:")
        
        #Preconditions
        if emBits == None:
            emBits = 8 * len(EM)
        assert emBits >= 8* self.hLen + 8* self.sLen + 9, "Not enough emBits"
        
        emLen = int(math.ceil(emBits / 8.0))
        assert len(EM) == emLen, "EM length not equivalent to bits provided"
        
        # assert len(M) < (2^61 -1), Message too long
        
        #Let mHash = Hash (M), an octet string of length hLen
        mHash = self.hashFn(M)
        
        #if emLen < hLen + sLen + 2, output 'inconsistent' and stop.
        if emLen < self.hLen + self.sLen + 2:
            if debug: print("emLen too short") 
            return False
        
        #If the rightmost octet of EM does not have hexadecimal value 0xbc, output
        #'inconsistent' and stop.
        if EM[len(EM)-1:] != b'\xbc':
            if debug: print("0xbc not found") 
            return False
        
        #Let maskedDB be the leftmost emLen - hLen - 1 octets of EM, and let H be the
        #next hLen octets.
        maskeDBlen = emLen - self.hLen - 1
        maskedDB = Bytes(EM[:maskeDBlen])
        H = EM[maskeDBlen:maskeDBlen+self.hLen]
        
        #If the leftmost 8emLen - emBits bits of the leftmost octet in maskedDB are not all
        #equal to zero, output 'inconsistent' and stop.
        numzeros = 8 * emLen - emBits
        bitmask  = int('1'*numzeros + '0'*(8-numzeros), 2)
        _mask_check = maskedDB[0]
        if not py3: _mask_check = ord(_mask_check)
        if (_mask_check & bitmask != 0):
            if debug: print("right % bits of masked db not zero, found %" % (numzeros, bin(maskedDB[0])))
            return False 
        
        #Let dbMask = MGF (H, emLen - hLen - 1).
        masklen = emLen - self.hLen - 1
        dbMask = MGF1(H, masklen, self.hashFn, self.hLen)
        #Let DB = maskedDB ^ dbMask.
        DB = maskedDB ^ dbMask
        
        #Set the leftmost 8emLen - emBits bits of the leftmost octet in DB to zero.
        numzeros = 8 * emLen - emBits
        bitmask  = int('0'*numzeros + '1'*(8-numzeros), 2)
        ba = bytearray(DB)
        ba[0] &= bitmask
        DB = Bytes(ba)

        #If the emLen - hLen - sLen - 2 leftmost octets of DB are not zero
        zerolen = emLen - self.hLen - self.sLen - 2
        if DB[:zerolen] != Bytes.fill(b'\x00', zerolen):
            if debug: print("DB did not start with % zero octets" % zerolen) 
            return False
        
        #or if the octet at position emLen - hLen - sLen - 1 (the leftmost position is 'position 1') does not
        #have hexadecimal value 0x01, output 'inconsistent' and stop.
        _db_check = DB[zerolen]
        if not py3: _db_check = ord(_db_check)
        if _db_check != 0x01:
            if debug: print("DB did not have 0x01 at %s, found %s instead" % (zerolen,DB[zerolen])) 
            return False
        
        #Let salt be the last sLen octets of DB.
        salt = DB[len(DB)-self.sLen:]
        #Let M' = (0x)00 00 00 00 00 00 00 00 || mHash || salt ;
        mPrime = Bytes.fill(b'\x00', 8) + mHash + salt
        
        #Let H' = Hash (M'), an octet string of length hLen.
        HPrime = self.hashFn(mPrime)
        
        if debug:
            print("M     =>", M) 
            print("mHash =>", mHash)
            print("salt  =>", salt)
            print("M'    =>", mPrime)
            print("H     =>", H)
            print("DB    =>", DB)
            print("dbmask=>", dbMask)
            print("masked=>", maskedDB)
            print("EM    =>", EM)
        
        #If H = H', output 'consistent'. Otherwise, output 'inconsistent'.
        return H == HPrime

class SAEPEncryptionPadding:
    '''
    :Authors: Christina Garman
    
    SAEPEncryptionPadding
    '''
    def __init__(self, _hash_type ='sha384'):
        self.name = "SAEPEncryptionPadding"
        self.hashFn = hashFunc(_hash_type)
        self.hashFnOutputBytes = len(hashlib.new(_hash_type).digest())
        
    def encode(self, message, n, s0):
        #n = m + s0 + s1
        m = int(n/4) #usually 256 bits

        if(len(message) > (m/8)):
            assert False, "message too long"

        if(len(message) != m):
            message_ext = bytes(message) + Bytes.fill(b'\x80', 1)
            if(len(message_ext) != m):
                message_ext = bytes(message_ext) + Bytes.fill(b'\x00', ((m/8)-2)-len(message))
            message_ext = bytes(message_ext) + Bytes.fill(b'\x80', 1)

        s1 = n - m - s0
        t = Bytes.fill(b'\x00', s0/8)

        rand = SecureRandomFactory.getInstance()
        r = rand.getRandomBytes(int(s1/8))

        v = Bytes(bytes(message_ext) + t)

        x = v ^ self.hashFn(r)

        y = x + r

        if(debug):
            print("Encoding")
            print("m        =>", m)
            print("s0       =>", s0)
            print("s1       =>", s1)
            print("t        =>", t, len(t))
            print("r        =>", r, len(r))
            print("v        =>", v, len(v))
            print("x        =>", x)
            print("y        =>", y, len(y))
      
        return y
    
    def decode(self, encMessage, n, s0):
        m = int(n/4)

        x = encMessage[:int((m+s0)/8)]
        r = encMessage[int((m+s0)/8):int(n-m-s0)]

        v = Bytes(x) ^ self.hashFn(r)

        M = v[:int(m/8)]
        t = v[int(m/8):int(m+s0/8)]

        if(M[-1] == 128 and (M[-2] == 0 or M[-2] == 128)):
            index = M[:(len(M)-1)].rindex(b'\x80')
            M = M[:index]
        else:
            M = M[:len(M)-1]

        if(debug):
            print("decoding:")
            print("x    => ", x)
            print("r    => ", r)
            print("v    => ", v)
            print("M    => ", M)
            print("t    => ", t)
            print("r    =>" , r)

        return (M, t)

class PKCS7Padding(object):
    def __init__(self,block_size = 16):
        self.block_size = block_size
        
    def encode(self,_bytes,block_size = 16):
        pad = self._padlength(_bytes)
        return _bytes.ljust(pad+len(_bytes),bytes([pad]))

    def decode(self,_bytes):
        return _bytes[:-(_bytes[-1])]


    def _padlength(self,_bytes):
        ln=len(_bytes)
        pad_bytes_needed = self.block_size - (ln % self.block_size)
        if pad_bytes_needed == 0:
            pad_bytes_needed = self.block_size
        return pad_bytes_needed
