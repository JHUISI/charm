
from charm.toolbox.pairinggroup import PairingGroup,GT,extract_key
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.toolbox.ABEnc import ABEnc
from charm.schemes.abenc.abenc_lsw08 import KPabe

debug = False
class HybridABEnc(ABEnc):
    """
    >>> from charm.schemes.abenc.abenc_lsw08 import KPabe
    >>> group = PairingGroup('SS512')
    >>> kpabe = KPabe(group)
    >>> hyb_abe = HybridABEnc(kpabe, group)
    >>> access_policy =  ['ONE', 'TWO', 'THREE']
    >>> access_key = '((FOUR or THREE) and (TWO or ONE))'
    >>> msg = b"hello world this is an important message."
    >>> (master_public_key, master_key) = hyb_abe.setup()
    >>> secret_key = hyb_abe.keygen(master_public_key, master_key, access_key)
    >>> cipher_text = hyb_abe.encrypt(master_public_key, msg, access_policy)
    >>> hyb_abe.decrypt(cipher_text, secret_key)
    b'hello world this is an important message.'
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
        cipher = AuthenticatedCryptoAbstraction(extract_key(key))
        c2 = cipher.encrypt(M)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, ct, sk):
        c1, c2 = ct['c1'], ct['c2']
        key = abenc.decrypt(c1, sk)
        cipher = AuthenticatedCryptoAbstraction(extract_key(key))
        return cipher.decrypt(c2)
    
def main():
    groupObj = PairingGroup('SS512')
    kpabe = KPabe(groupObj)
    hyb_abe = HybridABEnc(kpabe, groupObj)
    access_key = '((ONE or TWO) and THREE)'
    access_policy = ['ONE', 'TWO', 'THREE']
    message = b"hello world this is an important message."
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
