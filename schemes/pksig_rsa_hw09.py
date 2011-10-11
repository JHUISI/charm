"""
Hohenberger-Waters Stateful Signatures (RSA-based)
 
 | From: "S. Hohenberger, B. Waters. Realizing Hash-and-Sign Signatures under Standard Assumptions", Section 3.
 | Published in: Eurocrypt 2009
 | Available from: http://eprint.iacr.org/2009/028.pdf
 | Notes: 

 * type:       signature (public key)
 * setting:      RSA
 * assumption:   RSA

:Author:    J Ayo Akinyele
:Date:      1/2011
:Status:    BROKEN at the moment
"""

from charm.integer import *
from toolbox.PKSig import PKSig
from chamhash_rsa_hw09 import ChamHash_HW09
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
import hmac, hashlib, math

def SHA1(bytes):
  s1 = hashlib.new('sha1')
  s1.update(bytes)
  return s1.digest()


def randomQR(n):
    return random(n) ** 2

class LogFunction:
  def __init__(self, base=10):
    self.base = base
  
  def __getitem__(self, base):
    return LogFunction(base)
  
  def __call__(self, val):
    return math.log(val, self.base)
log = LogFunction()

class Prf:
  def __init__(self):
      pass
  
  @classmethod
  def keygen(self, bits):
    return integer(randomBits(bits))

  @classmethod  
  def eval(self, k, input, outputLen):
    if outputLen%8 != 0:
       return False
    if type(k) == integer:
        h = hmac.new(serialize(k), b'', hashlib.sha1)
    else:
        h = hmac.new(serialize(integer(k)), b'', hashlib.sha1)
    h.update(input)
    seed = Conversion.bytes2integer(h.hexdigest())

    #print("Prf result =>", seed)
    return seed

class BlumIntegerSquareRoot:
  def __init__(self, p, q):
    self.raisedToThePower = 1
    self.p = p
    self.q = q
    
  def pow(self, modularInt):
    # TODO: Verify that this is a blum integer!!!!!!!
    p, q = self.p, self.q
    result = integer(modularInt) % (p * q)
    for repeat in range(self.raisedToThePower):
        result = result ** (((p-1)*(q-1)+4)/8)
    return result

  def __pow__(self, power):
    exp = BlumIntegerSquareRoot(self.p, self.q)
    exp.raisedToThePower = power
    return exp.pow(power)

class Sig_RSA_Stateless_HW09(PKSig):
    def __init__(self, CH = ChamHash_HW09):
#        self.state = 0
        self.Prf = Prf()
        self.ChameleonHash = CH()
        
    def keygen(self, keyLength=1024):
        # Generate a Blum-Williams integer N of 'key_length' bits with factorization p,q
        (p, q) = randomPrime(keyLength), randomPrime(keyLength)
        # Generate random u,h \in QR_N and a random c \in {0,1}^|N|
        N = p * q
        u = randomQR(N)
        h = randomQR(N)
        c = randomBits(keyLength)#PRNG_generate_bits(key_length)

        K = self.Prf.keygen(keyLength)
        self.state = 0
    
        # Generate the Chameleon hash parameters.  We do not need the secret params.
        (L, secret) = self.ChameleonHash.paramgen(keyLength, p, q);
    
        # Assemble the public and secret keys
        pk = { 'length': keyLength, 'N': N, 'u': u, 'h': h, 'c': c, 'K': K, 'L': L }
        sk = { 'p': p, 'q': q }
        return (pk, sk);
    
    def sign(self, pk, sk, message, s=0):
        L, K, c, keyLength, u, h, N = pk['L'], pk['K'], pk['c'], pk['length'], pk['u'], pk['h'], pk['N']
        p, q = sk['p'], sk['q']
        # Use internal state counter if none was provided
        if (s == 0):
          s = self.state
          self.state += 1

        # Hash the message using the chameleon hash under params L to obtain (x, r)
        (x, r) = self.ChameleonHash.hash(L, message);
        print("x =>", x)
        print("r =>", r)
        # Compute e = H_k(s) and check whether it's prime. If not, increment s and repeat.
        e = self.HW_hash(K, c, s, keyLength)
        
        phi_N = (p-1)*(q-1)
        while not (isPrime(e)): # and isPrime(integer(e, (p-1)*(q-1))
            s += 1
            e = self.HW_hash(K, c, s, keyLength)
            e = e % phi_N
#        e = e % phi_N
        print("sign: e =>", e)
    
        # Compute B = SQRT(u^x * h)^ceil(log_2(s)) mod N
        # Note that SQRT requires the factorization p, q
        result = (BlumIntegerSquareRoot(p, q) ** (math.ceil(log[2](s))))
        print("bum-wil result =>", result)
        B = ((u ** x) * h) ** result
        # sigma1 = B^{1/e}
        sigma1 = (B ** (e ** -1))
    
        # Update internal state counter and return sig = (sigma1, r, s)
        self.state = s
        return { 'sigma1': sigma1, 'r': r, 's': s, 'e':e }


    def verify(self, pk, message, sig):
        print("\nVERIFY\n\n")
        sigma1, r, s, e = sig['sigma1'], sig['r'], sig['s'], sig['e']
        K, L, c, keyLength, u, h, N = pk['K'], pk['L'], pk['c'], pk['length'], pk['u'], pk['h'], pk['N']
    
        # Make sure that 0 < s < 2^{keylength/2}, else reject the signature
        if not (0 < s and s < (2 ** (keyLength/2))):
            return False
      
        # Compute Y = sigma1^{2*ceil(log2(s))}
        s1 = integer(2 ** math.ceil(math.log(s,2)))
        print("s1 =>", s1)
        Y = sigma1 ** s1
        print("Y =>", Y)
        # Hash the mesage using the chameleon hash with fixed randomness r
        (x, r) = self.ChameleonHash.hash(L, message, r)
        print("x =>", x)
        print("r =>", r)
        # Compute e = H_k(s) and reject the signature if it's not prime
        #e = self.HW_hash(K, c, s, keyLength)

        print("verify: e =>", e)
        if not isPrime(e):
            return False
    
        print("Final check")
        print()
        lhs = (Y ** e) % N
        print("lhs =>", lhs)
        rhs = ((u ** x) * h) % N
        print("rhs =>", rhs)
        # Verify that Y^e = (u^x h) mod N.  If so, accept the signature
        if lhs == rhs:
            return True
        # Default: reject the signature
        return False
    
    def HW_hash(self, key, c, input, keyLen):
        # Return c XOR PRF(k, input), where the output of PRF is keyLength bits
        if type(input) != str:
            input_temp = input
            input_s = ''
            while input_temp > 0:
                input_s = chr(input_temp & 0xff) + input_s
                input_temp = input_temp >> 8
            input_b = Bytes(input_s, 'utf8')
        else: 
            assert False, "Invalid input: need an integer."
        result = integer(c) ^ self.Prf.eval(key, input_b, keyLen)
        #print("HW_hash =>", result)
        return result

if __name__ == "__main__":
    pksig = Sig_RSA_Stateless_HW09() 

    (pk, sk) = pksig.keygen(1024)
    print("Public parameters...")
    print("pk =>", pk)
    print("sk =>", sk)
    
    m = SHA1(b'this is the message I want to hash.')
    sig = pksig.sign(pk, sk, m)
    print("Signature...")
    print("sig =>", sig)
    
    assert pksig.verify(pk, m, sig), "FAILED VERIFICATION!!!"
    print("Successful Verification!!!")