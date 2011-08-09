'''
Base class for public-key encryption
 
Notes: This class implements an interface for a standard public-key encryption scheme.
A public key encryption consists of four algorithms: (paramgen, keygen, encrypt, decrypt).
'''
from toolbox.schemebase import *

class PKEnc(SchemeBase):
    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase.setProperty(self, scheme="PKEnc")
        self.baseSecDefs = Enum('IND_CPA', 'IND_CCA1', 'IND_CCA2')
          
    def paramgen(self, param1=None, param2=None):
        return NotImplemented

    def keygen(self, securityparam):
        return NotImplemented

    def encrypt(self, pk, M):
        if hasattr(self, '_encrypt'):
            # do some arg type checking here?
            targ_pk = self._encrypt.__annotations__['pk']
            targ_m = self._encrypt.__annotations__['M']
            assert SchemeBase.verifyTypeDict(self, pk, targ_pk),  "invalid pk target type."
            if not SchemeBase.verifyType(self, M, targ_m):
                # cast M into target type
                M = Conversion.convert(M, targ_m)
            return self._encrypt(pk, M)
        return NotImplemented

    def decrypt(self, pk, sk, c):
        if hasattr(self, '_decrypt'):
            # do some arg type checking here?   
            #print("annotations:", self._decrypt.__annotations__)
            targ_pk = self._decrypt.__annotations__['pk']
            targ_sk = self._decrypt.__annotations__['sk']
            targ_c = self._decrypt.__annotations__['c']
            assert SchemeBase.verifyTypeDict(self, pk, targ_pk), "invalid pk target type"
            assert SchemeBase.verifyTypeDict(self, sk, targ_sk), "invalid sk target type"
            assert SchemeBase.verifyTypeDict(self, c, targ_c), "invalid cipher target type"
            return self._decrypt(pk, sk, c)
        return NotImplemented
    