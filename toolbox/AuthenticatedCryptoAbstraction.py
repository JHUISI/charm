from toolbox.MessageAuthenticator import MessageAuthenticator
from toolbox.SymmetricCryptoAbstraction import SymmetricCryptoAbstraction
from hashlib import sha1
class AuthenticatedCryptoAbstraction(SymmetricCryptoAbstraction): 
   def encrypt(self,msg):
        mac = MessageAuthenticator(sha1(b'Poor Mans Key Extractor'+self._key).digest()) # warning only valid in the random oracle 
        enc = super(AuthenticatedCryptoAbstraction,self).encrypt(msg)
        return mac.mac(enc);
   def decrypt(self,cipherText): 
        mac = MessageAuthenticator(sha1(b'Poor Mans Key Extractor'+self._key).digest()) # warning only valid in the random oracle 
        if not  mac.verify(cipherText):
            raise ValueError("Invalid mac. Your data was tampered with or your key is wrong")
        else:
            return super(AuthenticatedCryptoAbstraction,self).decrypt(cipherText['msg'])
