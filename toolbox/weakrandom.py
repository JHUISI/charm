'''
Created on Jun 22, 2011

@author: urbanus
'''
import random
from bitstring import *
from SecureRandom import SecureRandom


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
        This method does NOT provide cryptographically secure random numbers
        This should NOT be used for production code
        '''
        
        if(printable):
            #Nice printable characters for testing purposes
            return Bytes(random.randrange(0x20, 0x7E) for i in range(length))
        else:
            return Bytes(random.randrange(0, 256) for i in range(length))