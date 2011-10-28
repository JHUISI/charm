from charm.cryptobase import MODE_CBC,AES,selectPRP
from toolbox.pairinggroup import PairingGroup,GT
from charm.pairing import hash as sha1
from toolbox.conversion import *
from math import ceil
from os import urandom
class SymmetricCryptoAbstracton(object):
    def __init__(self,key, alg = AES, mode = MODE_CBC):
        self._alg = alg
        self.key_len = 16
        self._block_size = 16 
        self._mode = mode
        self._key = sha1(key)[0:self.key_len] 
    def _initCipher(self,IV = None):
        if IV == None :
            IV =  urandom(self._block_size)
        self._IV = IV 
        return selectPRP(self._alg,(self._key,self._mode,IV))

    def encrypt(self,message):
        self._IV = urandom(self._block_size)
        #Because the IV cannot be set after instantiation, decrypt and encrypt 
        # must operate on their own instances of the cipher 
        cipher = self._initCipher() 
        ct= {'ALG':self._alg,
            'MODE':self._mode,
            'IV':self._IV,
            'CipherText':cipher.encrypt(self.__pad(message))
            }
        return ct
    def decrypt(self,cipherText):
        cipher = self._initCipher(cipherText['IV'])
        
        msg = cipher.decrypt(cipherText['CipherText'])
        return self.__unpad(msg)
        
    def __pad(self, message):
        # calculate the ceiling of
        msg_len = ceil(len(message) / self.key_len) * self.key_len
        extra = msg_len - len(message)
        # append 'extra' bytes to message
        for i in range(0, extra):
            message += '\x00'
        return message
    def __unpad(self,message):
        return Conversion.bytes2str(message).strip('\x00')
if __name__ =="__main__":
    groupObj = PairingGroup('../param/a.param')
    a = SymmetricCryptoAbstracton(groupObj.random(GT))
    ct = a.encrypt("as")
    print(ct)    
    m = a.decrypt(ct)
    print(m)
