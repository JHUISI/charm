''' Base class for attribute-based encryption
 
 Notes: This class implements an interface for a standard attribute-based encryption scheme.
 
 A public key attribute-based encryption scheme consists of four algorithms: 
 (setup, keygen, encrypt, decrypt).
'''
from toolbox.schemebase import *

class ABEnc(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase.setProperty(self, scheme='ABEnc')  
        self.baseSecDefs = None 

    def setup(self):
        raise NotImplementedError

    def keygen(self, pk, sk, object):
        raise NotImplementedError

    def encrypt(self, pk, object):
        raise NotImplementedError

    def decrypt(self, pk, sk, ciphertext):
        raise NotImplementedError
