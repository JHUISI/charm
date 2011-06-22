'''
Base class for cryptographic secure random number generation
@author: Gary Belvin
'''

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
    

from weakrandom import WeakRandom
class SecureRandomFactory():
    '''
    This class provides a central place to swap out the randomness engine
    used by the charm framework.
    Classes should call rand = SecureRandomFactory.getInstance() 
    to acquire a randomnesss generator
    '''
    
    @classmethod
    def getInstance(self):
        return WeakRandom()
    