from charm.core.math.pairing import hashPair as sha1
from charm.toolbox.paddingschemes import PKCS7Padding
from charm.toolbox.securerandom import OpenSSLRand
from charm.core.crypto.cryptobase import MODE_CBC,AES,selectPRP
from hashlib import sha1 as sha1hashlib
from math import ceil
import json
import hmac
from base64 import b64encode,b64decode

class MessageAuthenticator(object):
    """ Abstraction for constructing and verifying authenticated messages 
       
        A large number of the schemes can only encrypt group elements 
        and do not provide an efficient mechanism for encoding byte in
        those elements. As such we don't pick a symmetric key and encrypt 
        it asymmetrically. Rather, we hash a random group element to get the
        symmetric key.

    >>> from charm.toolbox.pairinggroup import PairingGroup,GT
    >>> from charm.core.math.pairing import hashPair as extractor
    >>> groupObj = PairingGroup('SS512')
    >>> key = groupObj.random(GT)
    >>> m = MessageAuthenticator(extractor(key))
    >>> AuthenticatedMessage = m.mac('Hello World')
    >>> m.verify(AuthenticatedMessage)
    True
    """
    def __init__(self,key, alg = "HMAC_SHA1"):
        """
        Creates a message authenticator and verifier under the specified key
        """
        if alg != "HMAC_SHA1":
            raise ValueError("Currently only HMAC_SHA1 is supported as an algorithm")
        self._algorithm = alg
        self._key = key    
    def mac(self,msg):
        """
        authenticates a message 
        """
        return {
                "alg": self._algorithm,
                "msg": msg, 
                "digest": hmac.new(self._key,(self._algorithm + msg),digestmod=sha1hashlib).hexdigest()
               }

    def verify(self,msgAndDigest):
        """
        verifies the result returned by mac
        """
        if msgAndDigest['alg'] != self._algorithm:
            raise ValueError("Currently only HMAC_SHA1 is supported as an algorithm")
        expected = (self.mac(msgAndDigest['msg'])['digest'])
        recieved = (msgAndDigest['digest'])
        return sha1hashlib(expected).digest() == sha1hashlib(recieved).digest() # we compare the hash instead of the direct value to avoid a timing attack

class SymmetricCryptoAbstraction(object):
    """
    Abstraction for symmetric encryption and decryption of data.
    Ideally provide an INDCCA2 secure symmetric container for arbitrary data.
    Currently only supports primitives that JSON can encode and decode.
  
    A large number of the schemes can only encrypt group elements 
    and do not provide an efficient mechanism for encoding byte in
    those elements. As such we don't pick a symmetric key and encrypt 
    it asymmetrically. Rather, we hash a random group element to get the
    symmetric key.

    >>> from charm.toolbox.pairinggroup import PairingGroup,GT
    >>> groupObj = PairingGroup('SS512')
    >>> from charm.core.math.pairing import hashPair as extractor
    >>> a = SymmetricCryptoAbstraction(extractor(groupObj.random(GT)))
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
        self._padding = PKCS7Padding();
 
    def _initCipher(self,IV = None):
        if IV == None :
            IV =  OpenSSLRand().getRandomBytes(self._block_size)
        self._IV = IV
        return selectPRP(self._alg,(self._key,self._mode,self._IV))

    def __encode_decode(self,data,func):
        data['IV'] = func(data['IV'])
        data['CipherText'] = func(data['CipherText'])
        return data

    #This code should be factored out into  another class
    #Because json is only defined over strings, we need to base64 encode the encrypted data
    # and convert the base 64 byte array into a utf8 string
    def _encode(self,data):
        return self.__encode_decode(data,lambda x:b64encode(x).decode('utf-8'))

    def _decode(self,data):
        return self.__encode_decode(data,lambda x:b64decode((x)))

    def encrypt(self, message):
        #This should be removed when all crypto functions deal with bytes"
        if type(message) != bytes :
            message = (message)
        ct = self._encrypt(message)
        #JSON strings cannot have binary data in them, so we must base64 encode  cipher
        cte = json.dumps(self._encode(ct))
        return cte

    def _encrypt(self,message):
        #Because the IV cannot be set after instantiation, decrypt and encrypt 
        # must operate on their own instances of the cipher 
        cipher = self._initCipher() 
        ct= {'ALG':self._alg,
            'MODE':self._mode,
            'IV':self._IV,
            'CipherText':cipher.encrypt(self._padding.encode(message))
            }
        return ct

    def decrypt(self,cipherText):
        f = json.loads(cipherText)
        return self._decrypt(self._decode(f)) #.decode("utf-8")

    def _decrypt(self,cipherText):
        cipher = self._initCipher(cipherText['IV'])
        msg = cipher.decrypt(cipherText['CipherText'])
        return self._padding.decode(msg)
        
class AuthenticatedCryptoAbstraction(SymmetricCryptoAbstraction): 
    def encrypt(self,msg):
        mac = MessageAuthenticator(sha1hashlib(b'Poor Mans Key Extractor'+self._key).digest()) # warning only valid in the random oracle 
        enc = super(AuthenticatedCryptoAbstraction,self).encrypt(msg)
        return mac.mac(enc)

    def decrypt(self,cipherText): 
        mac = MessageAuthenticator(sha1hashlib(b'Poor Mans Key Extractor'+self._key).digest()) # warning only valid in the random oracle 
        if not  mac.verify(cipherText):
            raise ValueError("Invalid mac. Your data was tampered with or your key is wrong")
        else:
            return super(AuthenticatedCryptoAbstraction,self).decrypt(cipherText['msg'])
