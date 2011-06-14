
from toolbox.pairinggroup import *
from charm.pairing import hash as sha1
from toolbox.ABEncMultiAuth import *
from dabe11 import *
from charm.cryptobase import *
from math import ceil

class HybridABEncMA(ABEncMultiAuth):
    def __init__(self, scheme, groupObj):
        global abencma, group
        # check properties (TODO)
        abencma = scheme
        group = groupObj

    def setup(self):
        return abencma.setup()
    
    def authsetup(self, *args):
        return abencma.authsetup(args)
    
    def encrypt(self, pk, gp, M, policy_str):
        if type(M) != str and type(policy_str) != str: raise "message and policy not right type!"        
        key = group.random(GT)
        c1 = abencma.encrypt(pk, gp, key, policy_str)
        # instantiate a symmetric enc scheme from this key
        cipher = self.instantiateCipher(MODE_CBC, key)        
        c2 = cipher.encrypt(self.pad(M))
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, gp, sk, ct, SK):
        c1, c2 = ct['c1'], ct['c2']
        key = abencma.decrypt(gp, sk, c1, SK)        
        cipher = self.instantiateCipher(MODE_CBC, key)
        msg = cipher.decrypt(c2)
        return msg
        
    def instantiateCipher(self, mode, message):
        self.mode, self.key_len = AES, 16
        # hash GT msg into a hex string
        key = sha1(message)[0:self.key_len]
        iv  = '6543210987654321' # static IV (for testing)    
        PRP_method = selectPRP(AES, (key, mode, iv))        
        return PRP_method
    
    def pad(self, message):
        # calculate the ceiling of
        msg_len = ceil(len(message) / self.key_len) * self.key_len 
        extra = msg_len - len(message)
        # append 'extra' bytes to message
        for i in range(0, extra):
            message += '\x00'
        return message

if __name__ == "__main__":
    groupObj = PairingGroup('a.param')
    dabe = Dabe(groupObj)
        
    hyb_abema = HybridABEncMA(dabe, groupObj)
    
    # add dabe main code as is using below pattern for data encryption
    
#    (pk, mk) = hyb_ibe.setup()
#
#    kID = 'waldoayo@gmail.com'
#    sk = hyb_ibe.extract(mk, kID)
#
#    msg = "Hello World My name is blah blah!!!! Word!"
#    
#    ct = hyb_ibe.encrypt(pk, sk['id'], msg)
#    print("Ciphertext")
#    print("c1 =>", ct['c1'])
#    print("c2 =>", ct['c2'])
#    
#    orig_msg = hyb_ibe.decrypt(pk, sk, ct)
#    print("Result =>", orig_msg)

    
    
