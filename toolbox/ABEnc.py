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

    def keygen(self, pk, mk, object):
        if hasattr(self, '_keygen'):
            (targ_pk, targ_mk, targ_result) = \
                SchemeBase.getTypes(self._keygen, ['pk', 'mk', 'return'])
            assert SchemeBase.verifyTypeDict(self, pk, targ_pk), "invalid pk type."
            assert SchemeBase.verifyTypeDict(self, mk, targ_mk), "invalid mk type."
            result = self._keygen(pk, mk, object)
            assert SchemeBase.verifyTypeDict(self, result, targ_result), "invalid keygen type."
            return result
        raise NotImplementedError

    def encrypt(self, pk, M, object):
        if hasattr(self, '_encrypt'):
            # do some arg type checking here?
            (targ_pk, targ_m, targ_result) = \
                SchemeBase.getTypes(self._encrypt, ['pk', 'M', 'return'])
            assert SchemeBase.verifyTypeDict(self, pk, targ_pk), "invalid pk type."
            if not SchemeBase.verifyType(self, M, targ_m):
                # cast M into target type
                M = Conversion.convert(self, M, targ_m)
            result = self._encrypt(pk, M, object)        
            assert SchemeBase.verifyTypeDict(self, result, targ_result), "invalid ciphertext type."
            return result
        raise NotImplementedError

    def decrypt(self, pk, sk, ct):
        if hasattr(self, '_decrypt'):
            (targ_pk, targ_sk, targ_ct, targ_result) = \
                SchemeBase.getTypes(self._decrypt, ['pk', 'sk', 'ct', 'return'])
            assert SchemeBase.verifyTypeDict(self, pk, targ_pk), "invalid pk type."
            assert SchemeBase.verifyTypeDict(self, sk, targ_sk), "invalid sk type."
            assert SchemeBase.verifyTypeDict(self, ct, targ_ct), "invalid ciphertext type."

            result = self._decrypt(pk, sk, ct)
            if type(result) == dict:
                assert SchemeBase.verifyTypeDict(self, result, targ_result), "invalid message type."
            else:
                assert SchemeBase.verifyType(self, result, targ_result), "invalid ciphertext type."  
            return result
        raise NotImplementedError
