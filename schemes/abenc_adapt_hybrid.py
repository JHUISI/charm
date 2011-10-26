
from charm.cryptobase import MODE_CBC,AES,selectPRP
from toolbox.ABEnc import ABEnc
from schemes.abenc_bsw07 import CPabe_BSW07
from toolbox.pairinggroup import PairingGroup,GT
from charm.pairing import hash as sha1
from toolbox.conversion import *
from math import ceil

debug = False
class HybridABEnc(ABEnc):
    """
    >>> groupObj = PairingGroup('../param/a.param')
    >>> cpabe = CPabe_BSW07(groupObj)
    >>> hyb_abe = HybridABEnc(cpabe, groupObj)
    >>> access_policy = '((four or three) and (two or one))'
    >>> message = "hello world this is an important message."
    >>> (pk, mk) = hyb_abe.setup()
    >>> sk = hyb_abe.keygen(pk, mk, ['ONE', 'TWO', 'THREE'])
    >>> ct = hyb_abe.encrypt(pk, message, access_policy)
    >>> hyb_abe.decrypt(pk, sk, ct)
    'hello world this is an important message.'
    """
    def __init__(self, scheme, groupObj):
        ABEnc.__init__(self)
        global abenc
        # check properties (TODO)
        abenc = scheme
        self.group = groupObj
            
    def setup(self):
        return abenc.setup()
    
    def keygen(self, pk, mk, object):
        return abenc.keygen(pk, mk, object)
    
    def encrypt(self, pk, M, object):
        key = self.group.random(GT)
        c1 = abenc.encrypt(pk, key, object)
        # instantiate a symmetric enc scheme from this key
        cipher = self.instantiateCipher(MODE_CBC, key)        
        c2 = cipher.encrypt(self.__pad(M))
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, pk, sk, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = abenc.decrypt(pk, sk, c1)
        cipher = self.instantiateCipher(MODE_CBC, key)
        msg = cipher.decrypt(c2)
        return Conversion.bytes2str(msg).strip('\x00')
    
    def instantiateCipher(self, mode, message):
        self.alg, self.key_len = AES, 16
        # hash GT msg into a hex string
        key = sha1(message)[0:self.key_len]
        iv  = '6543210987654321' # static IV (for testing)    
        PRP_method = selectPRP(self.alg, (key, mode, iv))        
        return PRP_method
    
    def __pad(self, message):
        # calculate the ceiling of
        msg_len = ceil(len(message) / self.key_len) * self.key_len 
        extra = msg_len - len(message)
        # append 'extra' bytes to message
        for i in range(0, extra):
            message += '\x00'
        return message
