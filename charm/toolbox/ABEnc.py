''' Base class for attribute-based encryption
 
 Notes: This class implements an interface for a standard attribute-based encryption scheme.
 
 A public key attribute-based encryption scheme consists of four algorithms: 
 (setup, keygen, encrypt, decrypt).
'''
from charm.toolbox.schemebase import *

class ABEnc(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase._setProperty(self, scheme='ABEnc')  
        self.baseSecDefs = Enum('IND_AB_CPA', 'IND_AB_CCA', 'sIND_AB_CPA', 'sIND_AB_CCA') 

    def setup(self):
        raise NotImplementedError

    def keygen(self, pk, mk, object):
        raise NotImplementedError

    def encrypt(self, pk, M, object):
        raise NotImplementedError

    def decrypt(self, pk, sk, ct):
        raise NotImplementedError
