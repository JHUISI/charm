
from toolbox.pairinggroup import *
from charm.pairing import hash as sha1
from hashIDAdapt import *
from toolbox.IBEnc import *
from charm.cryptobase import *
from math import ceil

debug = False
class HybridIBEnc(IBEnc):
    def __init__(self, scheme, groupObj):
        global ibenc, group
        ibenc = scheme
        group = groupObj

    def setup(self):
        return ibenc.setup()
    
    def extract(self, mk, ID):
        return ibenc.extract(mk, ID)
    
    def encrypt(self, pk, ID, M : str):
        if type(M) != str: raise "message not right type!"        
        key = group.random(GT)
        c1 = ibenc.encrypt(pk, ID, key)
        # instantiate a symmetric enc scheme from this key
        prp = self.getPRP(key)        
        c2 = prp.encrypt(self.pad(M))
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, pk, ID, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = ibenc.decrypt(pk, ID, c1)        
        prp = self.getPRP(key)
        msg = prp.decrypt(c2)
        return bytes.decode(msg, 'utf8').strip('\x00')
        
    def getPRP(self, message):
        self.mode, self.key_len = AES, 16
        # hash GT msg into a hex string
        key = sha1(message)[0:self.key_len]
        iv  = '6543210987654321' # static IV (for testing)    
        PRP_method = selectPRP(AES, (key, MODE_CBC, iv))        
        return PRP_method
    
    def pad(self, message):
        # calculate the ceiling of
        msg_len = ceil(len(message) / self.key_len) * self.key_len 
        extra = msg_len - len(message)
        # append 'extra' bytes to message
        for i in range(0, extra):
            message += '\x00'
        return message

def main():
    groupObj = PairingGroup('../param/a.param')
    ibe = IBE_BB04(groupObj)
    
    hashID = HashIDAdapter(ibe, groupObj)
    
    hyb_ibe = HybridIBEnc(hashID, groupObj)
    
    (pk, mk) = hyb_ibe.setup()

    kID = 'waldoayo@gmail.com'
    sk = hyb_ibe.extract(mk, kID)

    msg = "Hello World My name is blah blah!!!! Word!"
    
    ct = hyb_ibe.encrypt(pk, sk['id'], msg)
    if debug:
        print("Ciphertext")
        print("c1 =>", ct['c1'])
        print("c2 =>", ct['c2'])
    
    orig_msg = hyb_ibe.decrypt(pk, sk, ct)
    if debug: print("Result =>", orig_msg)
    assert orig_msg == msg
    del groupObj

if __name__ == "__main__":
    debug = True
    main()

    
    
