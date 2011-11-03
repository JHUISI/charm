import hmac 
from hashlib import sha1 
class MessageAuthenticator(object):
    """ Abstraction for constructing and verifying authenticated messages 
        
    >>> from toolbox.pairinggroup import PairingGroup,GT
    >>> from charm.pairing import hash as extractor
    >>> groupObj = PairingGroup('../param/a.param')
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
            raise ValueError("Currently only HMAC_SHA1 is supportated as an algorithm")
        self._algorithm = alg
        self._key = sha1(b'Poor Mans Key Extractor'+key).digest() # warning only valid in the random oracle
    
    def mac(self,msg):
        """
        authenticates a message 
        """
        return {
                "alg": self._algorithm,
                "msg": msg, 
                "digest": hmac.new(self._key,bytes(msg,'utf-8'),digestmod=sha1).hexdigest()
               }

    def verify(self,msgAndDigest):
        """
        verifies the result returned by mac
        """
        if msgAndDigest['alg'] != self._algorithm:
            raise ValueError()
        expected = bytes(self.mac(msgAndDigest['msg'])['digest'],'utf-8')
        recieved = bytes(msgAndDigest['digest'],'utf-8')
        return sha1(expected).digest() == sha1(recieved).digest() # we compare the hash instead of the direct value to avoid a timing attack
