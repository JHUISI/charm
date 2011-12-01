from charm.cryptobase import MODE_CBC,AES,selectPRP
from charm.pairing import hash as sha1
from toolbox.conversion import *
from math import ceil
from os import urandom
import json
from base64 import b64encode,b64decode
class SymmetricCryptoAbstraction(object):
    """
    Abstraction for symmetric encryption and decryption of data.
    Ideally provide an INDCCA2 secure symmetric container for arbitrary data.
    Currently only supports primitives that JSON can encode and decode.

    usage:
    >>> from toolbox.pairinggroup import PairingGroup,GT
    >>> groupObj = PairingGroup('../param/a.param')
    >>> from charm.pairing import hash as sha1
    >>> a = SymmetricCryptoAbstraction(sha1(groupObj.random(GT)))
    >>> ct = a.encrypt("Friendly Fire Isn't")
    >>> a.decrypt(ct)
    "Friendly Fire Isn't"
    """

    def __init__(self,key, alg = AES, mode = MODE_CBC):
        self._alg = alg
        self.key_len = 16
        self._block_size = 16 
        self._mode = mode
        self._key = key[0:self.key_len]
 
    def _initCipher(self,IV = None):
        if IV == None :
            IV =  urandom(self._block_size)
        self._IV = IV
        return selectPRP(self._alg,(self._key,self._mode,self._IV))

    def __encode_decode(self,data,func):
        data['IV'] = func(data['IV'])
        data['CipherText'] = func(data['CipherText'])
        return data

    def _encode(self,data):
        return self.__encode_decode(data,lambda x:b64encode(x).decode('utf-8'))

    def _decode(self,data):
        return self.__encode_decode(data,lambda x:b64decode(bytes(x,'utf-8')))

    def encrypt(self, message):
        ct = self._encrypt(message)
        cte = json.dumps(self._encode(ct))
        return cte

    def _encrypt(self,message):
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
        f = json.loads(cipherText)
        return self._decrypt(self._decode(f))

    def _decrypt(self,cipherText):
        cipher = self._initCipher(cipherText['IV'])
        
        msg = cipher.decrypt(cipherText['CipherText'])
        return self.__unpad(msg)
        
    def __pad(self, message):
        # calculate the ceiling of
        msg_len = ceil(len(message) / float(self.key_len)) * self.key_len
        extra = msg_len - len(message)
        # append 'extra' bytes to message
        for i in range(0, extra):
            message += '\x00'
        return message

    def __unpad(self,message):
        return Conversion.bytes2str(message).strip('\x00') 
