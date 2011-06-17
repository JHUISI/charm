# Base class for public-key signatures
# 
# Notes: This class implements an interface for a standard public-key signature scheme.
#	 A public key signature consists of three algorithms: (keygen, sign, verify).
#
from toolbox.schemebase import *

class Hash(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase.setProperty(self, scheme='Hash')
        self.baseSecDefs = None # Enum('EU_CMA')
        
    def paramgen(self, secparam, p = 0, q = 0):
        raise NotImplementedError		

    def hash(self, message, r):
        raise NotImplementedError