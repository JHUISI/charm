from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.math.pairing import hashPair as sha2
from charm.adapters.ibenc_adapt_identityhash import HashIDAdapter
from charm.toolbox.IBEnc import IBEnc
from charm.core.crypto.cryptobase import *

debug = False
class HybridIBEnc(IBEnc):
    """
    >>> from charm.schemes.ibenc.ibenc_bb03 import IBE_BB04
    >>> group = PairingGroup('SS512')
    >>> ibe = IBE_BB04(group)
    >>> hashID = HashIDAdapter(ibe, group)
    >>> hyb_ibe = HybridIBEnc(hashID, group)
    >>> (master_public_key, master_key) = hyb_ibe.setup()
    >>> ID = 'john.doe@example.com'
    >>> secret_key = hyb_ibe.extract(master_key, ID)
    >>> msg = b"Hello World!"
    >>> cipher_text = hyb_ibe.encrypt(master_public_key, ID, msg)
    >>> decrypted_msg = hyb_ibe.decrypt(master_public_key, secret_key, cipher_text)
    >>> decrypted_msg == msg
    True

    """
    def __init__(self, scheme, groupObj):
        global ibenc, group
        ibenc = scheme
        group = groupObj

    def setup(self):
        return ibenc.setup()
    
    def extract(self, mk, ID):
        return ibenc.extract(mk, ID)
    
    def encrypt(self, pk, ID, M):
        if type(M) != bytes: raise "message not right type!"        
        key = group.random(GT)
        c1 = ibenc.encrypt(pk, ID, key)
        # instantiate a symmetric enc scheme from this key
        cipher = AuthenticatedCryptoAbstraction(sha2(key))
        c2 = cipher.encrypt(M)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, pk, ID, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = ibenc.decrypt(pk, ID, c1)        
        cipher = AuthenticatedCryptoAbstraction(sha2(key))
        return cipher.decrypt(c2)
    
