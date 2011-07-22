'''
Base class for cryptographic secure random number generation
:authors: Gary Belvin
'''
import random
from toolbox.bitstring import Bytes

class SecureRandom():
    def __init__(self):
        pass
    
    def getRandomBits(self, length):
        '''Returns a random bit string of length bytes'''
        raise NotImplementedError

    def addSeedMaterial(self, seed):
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
        '''getInstance currently returns a *completely* broken random number generator.
        
        .. todo:: replace with a secure, hash-based PRNG
        '''
        return WeakRandom()
    
    
class WeakRandom(SecureRandom):
    def __init__(self):
        SecureRandom.__init__(self)
        
    def getRandomBits(self, length):
        return self.myrandom(length, False)
    
    def addSeedMaterial(self, seed):
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
    