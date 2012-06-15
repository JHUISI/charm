''' Base class for attribute-based encryption multi-authority
 
 Notes: This class implements an interface for a standard attribute-based encryption scheme.
 
A public key attribute-based encryption scheme consists of four algorithms: 
(setup, authsetup, keygen, encrypt, decrypt).
'''
from charm.toolbox.schemebase import *

class ABEncMultiAuth(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase.setProperty(self, scheme='ABEncMultiAuth')  
        self.baseSecDefs = None 

    def setup(self):
        raise NotImplementedError

    def authsetup(self, gp, object):
        raise NotImplementedError

    def keygen(self, gp, sk, gid):
        raise NotImplementedError

    def encrypt(self, pk, gp, M, object):
        raise NotImplementedError

    def decrypt(self, gp, sk, ct):
        raise NotImplementedError
