'''
Base class for public-key signatures
 
Notes: This class implements an interface for a standard public-key signature scheme.
A public key signature consists of three algorithms: (keygen, sign, verify).
'''
from charm.toolbox.schemebase import *

class PKSig(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase.setProperty(self, scheme='PKSig')
        self.baseSecDefs = Enum('EU_CMA', 'wEU_CMA', 'sEU_CMA')
        
    def keygen(self, securityparam):
        raise NotImplementedError		

    def sign(self, pk, sk, message):
        raise NotImplementedError
    
    def verify(self, pk, message, sig):
        raise NotImplementedError
