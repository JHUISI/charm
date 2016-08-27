'''
Base class for cryptographic secure random number generation
:authors: Gary Belvin
'''
from charm.toolbox.bitstring import Bytes
from charm.toolbox.conversion import Conversion
from charm.core.math.integer import randomBits
import datetime
import math
import random

class SecureRandom():
    def __init__(self):
        pass
    def getRandomBytes(self, length):
        '''Returns a random bit string of length bytes'''
        raise NotImplementedError
    def addSeed(self, seed):
        '''
        Add randomness to the generator.  
        Always increases entropy
        '''
        raise NotImplementedError

class SecureRandomFactory():
    '''
    This class provides a central place to swap out the randomness engine
    used by the charm framework.
    Classes should call ``rand = SecureRandomFactory.getInstance()`` 
    to acquire a randomnesss generator
    '''
    @classmethod
    def getInstance(self):
        return OpenSSLRand()
    

class OpenSSLRand(SecureRandom):
    '''Uses the OpenSSL PRNG for random bits'''
    def __init__(self):
        SecureRandom.__init__(self)
        #seed with a little bit of random data. This is not the only source
        #of randomness. Internally, OpenSSL samples additional physical randomness.
    
    def getRandomBytes(self, length):
        bits = length * 8;
        val = randomBits(bits)
        return Conversion.IP2OS(val, length)
    
    def getRandomBits(self, length):
        i = randomBits(length)
        len = math.ceil(length / 8)
        return Conversion.IP2OS(i, len)


class WeakRandom(SecureRandom):
    def __init__(self):
        SecureRandom.__init__(self)
    def getRandomBytes(self, length):
        return self.myrandom(length, False)
    def addSeed(self, seed):
        raise NotImplementedError()
    @classmethod
    def myrandom(self, length, printable=False):
        '''
        This method does **NOT** provide cryptographically secure random numbers.
        This should **NOT** be used for production code
        '''
        if(printable):
            #Nice printable characters for testing purposes
            return Bytes(random.randrange(0x20, 0x7E) for i in range(length))
        else:
            return Bytes(random.randrange(0, 256) for i in range(length))
    
