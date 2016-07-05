''' Base class for Proxy Re-Encryption
 
 Notes: This class implements an interface for a standard proxy re-encryption scheme.
 
 A proxy re-encryption scheme consists of six algorithms: 
 (setup, keygen, encrypt, decrypt, rekeygen, re_encrypt).
'''
from charm.toolbox.schemebase import *

class PREnc(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase._setProperty(self, scheme='PREnc')  
        #self.baseSecDefs = Enum('IND_AB_CPA', 'IND_AB_CCA', 'sIND_AB_CPA', 'sIND_AB_CCA') 

    def setup(self):
        raise NotImplementedError

    def keygen(self, params):
        raise NotImplementedError

    def encrypt(self, params, pk, M):
        raise NotImplementedError

    def decrypt(self, params, sk, ct):
        raise NotImplementedError

    def rekeygen(self, params, pk_a, sk_a, pk_b, sk_b):
        raise NotImplementedError
    
    def re_encrypt(self, params, rk, c_a):
        raise NotImplementedError
