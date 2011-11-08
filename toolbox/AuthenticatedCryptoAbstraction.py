from toolbox.MessageAuthenticator import MessageAuthenticator
from toolbox.SymmetricCryptoAbstraction import SymmetricCryptoAbstraction

class AuthenticatedCryptoAbstraction(SymmetricCryptoAbstraction):
   def encrypt(self,msg):
        mac = MessageAuthenticator(self._key) 
        enc = super(AuthenticatedCryptoAbstraction,self).encrypt(msg)
        return mac.mac(enc);
   def decrypt(self,cipherText): 
        mac = MessageAuthenticator(self._key) 
        if not  mac.verify(cipherText):
            raise ValueError("Invalid mac. Your data was tampered with or your key is wrong")
        else:
            return super(AuthenticatedCryptoAbstraction,self).decrypt(cipherText['msg'])
