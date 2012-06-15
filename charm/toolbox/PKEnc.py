'''
Base class for public-key encryption
 
Notes: This class implements an interface for a standard public-key encryption scheme.
A public key encryption consists of four algorithms: (paramgen, keygen, encrypt, decrypt).
'''
from charm.toolbox.schemebase import *

class PKEnc(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase.setProperty(self, scheme="PKEnc")
        self.baseSecDefs = Enum('OW_CPA','OW_CCA1','OW_CCA','IND_CPA','IND_CCA1','IND_CCA',
                                'NM_CPA','NM_CCA1','NM_CCA','KA_CPA','KA_CCA1','KA_CCA')
          
    def paramgen(self, param1=None, param2=None):
        return NotImplemented

    def keygen(self, securityparam):
        return NotImplemented

    def encrypt(self, pk, M):
        return NotImplemented

    def decrypt(self, pk, sk, c):
        return NotImplemented
