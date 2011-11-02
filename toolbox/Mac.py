import hmac 
from hashlib import sha1 
from charm.pairing import hash as extractor
class Mac(object):
    """ Abstraction over an authenticated message
    >>> from toolbox.pairinggroup import PairingGroup,GT
    >>> groupObj = PairingGroup('../param/a.param')
    >>> key = groupObj.random(GT)
    >>> m = Mac(key)
    >>> msg = "Hello World"
    >>> foo = m.mac(msg)
    >>> m.verify(foo)
    True
    """
    def __init__(self,key, alg = "HMAC_SHA1"):
        if alg != "HMAC_SHA1":
            raise ValueError("Currently only HMAC_SHA1 is supportated as an algorithm")
        self._algorithm = alg
        self._mac = hmac.new(extractor(key),digestmod=sha1) # warning only valid in the random oracle
    
    def mac(self,msg):
        self._mac.update(msg)
        return {
                "alg": alg,
                "msg": msg, 
                "digest":self._mac.hexdigest()
               }

    def verify(msgAndDigest):
        if msgAndDigest['alg'] != self._algorithm:
            raise ValueError()
        return sha1(mac(msgAndDigest['msg'])) == sha1(msgAndDigest('digest')) #avoids timing attack on comapre. 
