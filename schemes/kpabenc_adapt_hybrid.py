
from charm.cryptobase import MODE_CBC,AES,selectPRP
from toolbox.ABEnc import ABEnc
from schemes.abenc_lsw08 import KPabe
from toolbox.pairinggroup import PairingGroup,GT
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.pairing import hash as sha1
from toolbox.conversion import *
from math import ceil

debug = False
class HybridABEnc(ABEnc):
    """
    >>> groupObj = PairingGroup('../param/a.param')
    >>> kpabe = KPabe(groupObj)
    >>> hyb_abe = HybridABEnc(kpabe, groupObj)
    >>> access_policy =  ['ONE', 'TWO', 'THREE']
    >>> access_key = '((FOUR or THREE) and (TWO or ONE))'
    >>> 
    >>> message = "hello world this is an important message."
    >>> (pk, mk) = hyb_abe.setup()
    >>> sk = hyb_abe.keygen(pk, mk, access_key)
    >>> ct = hyb_abe.encrypt(pk, message, access_policy)
    >>> hyb_abe.decrypt(ct, sk)
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
    
def main():
    groupObj = PairingGroup('../param/a.param')
    kpabe = KPabe(groupObj)
    hyb_abe = HybridABEnc(kpabe, groupObj)
    access_key = '((ONE or TWO) and THREE)'
    access_policy = ['ONE', 'TWO', 'THREE']
    message = "hello world this is an important message."
    (pk, mk) = hyb_abe.setup()
    if debug: print("pk => ", pk)
    if debug: print("mk => ", mk)
    sk = hyb_abe.keygen(pk, mk, access_key)
    if debug: print("sk => ", sk)
    ct = hyb_abe.encrypt(pk, message, access_policy)
    mdec = hyb_abe.decrypt(ct, sk)
    assert mdec == message, "Failed Decryption!!!"
    if debug: print("Successful Decryption!!!")

if __name__ == "__main__":
    debug = True
    main()
