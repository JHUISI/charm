
#from charm.core.crypto.cryptobase import MODE_CBC,AES
from charm.toolbox.ABEnc import ABEnc
from charm.toolbox.pairinggroup import GT
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.math.pairing import hash as sha1
from charm.toolbox.conversion import *
#from math import ceil

debug = False
class HybridABEnc(ABEnc):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup
    >>> from schemes.abenc.abenc_lsw08 import KPabe
    >>> group = PairingGroup('SS512')
    >>> kpabe = KPabe(group)
    >>> hyb_abe = HybridABEnc(kpabe, group)
    >>> access_policy =  ['ONE', 'TWO', 'THREE']
    >>> access_key = '((FOUR or THREE) and (TWO or ONE))'
    >>> msg = "hello world this is an important message."
    >>> (master_public_key, master_key) = hyb_abe.setup()
    >>> secret_key = hyb_abe.keygen(master_public_key, master_key, access_key)
    >>> cipher_text = hyb_abe.encrypt(master_public_key, msg, access_policy)
    >>> hyb_abe.decrypt(cipher_text, secret_key)
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
        cipher = AuthenticatedCryptoAbstraction(sha1(key))
        c2 = cipher.encrypt(M)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, ct, sk):
        c1, c2 = ct['c1'], ct['c2']
        key = abenc.decrypt(c1, sk)
        cipher = AuthenticatedCryptoAbstraction(sha1(key))
        return cipher.decrypt(c2)
    
