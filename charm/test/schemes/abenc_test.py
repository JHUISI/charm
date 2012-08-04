from charm.adapters.abenc_adapt_hybrid import HybridABEnc as HybridABEnc
from charm.adapters.kpabenc_adapt_hybrid import HybridABEnc as HybridKPABEnc
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.schemes.abenc.abenc_waters09 import CPabe09
from charm.schemes.abenc.abenc_lsw08 import KPabe
from charm.toolbox.pairinggroup import PairingGroup,GT
import unittest

debug = False

class HybridABEncTest(unittest.TestCase):
    def testHybridABEnc(self):
        groupObj = PairingGroup('SS512')
        cpabe = CPabe_BSW07(groupObj)
        hyb_abe = HybridABEnc(cpabe, groupObj)
        access_policy = '((four or three) and (two or one))'
        message = b"hello world this is an important message."
        (pk, mk) = hyb_abe.setup()
        if debug: print("pk => ", pk)
        if debug: print("mk => ", mk)
        sk = hyb_abe.keygen(pk, mk, ['ONE', 'TWO', 'THREE'])
        if debug: print("sk => ", sk)
        ct = hyb_abe.encrypt(pk, message, access_policy)
        mdec = hyb_abe.decrypt(pk, sk, ct)
        assert mdec == message, "Failed Decryption!!!"
        if debug: print("Successful Decryption!!!")

class CPabe_BSW07Test(unittest.TestCase):
    def testCPabe_BSW07(self):    
        groupObj = PairingGroup('SS512')
        
        cpabe = CPabe_BSW07(groupObj)
        attrs = ['ONE', 'TWO', 'THREE']
        access_policy = '((four or three) and (three or one))'
        if debug: 
            print("Attributes =>", attrs); print("Policy =>", access_policy)
        
        (pk, mk) = cpabe.setup()
        
        sk = cpabe.keygen(pk, mk, attrs)
       
        rand_msg = groupObj.random(GT) 
        if debug: print("msg =>", rand_msg)
        ct = cpabe.encrypt(pk, rand_msg, access_policy)
        if debug: print("\n\nCiphertext...\n")
        groupObj.debug(ct) 
        
        rec_msg = cpabe.decrypt(pk, sk, ct)
        if debug: print("\n\nDecrypt...\n")
        if debug: print("Rec msg =>", rec_msg)

        assert rand_msg == rec_msg, "FAILED Decryption: message is incorrect"
        if debug: print("Successful Decryption!!!")

class KPabeTest(unittest.TestCase):
    def testKPabe(self):    
        groupObj = PairingGroup('MNT224')
        kpabe = KPabe(groupObj)
        
        (pk, mk) = kpabe.setup()
        
        policy = '(ONE or THREE) and (THREE or TWO)'
        attributes = [ 'ONE', 'TWO', 'THREE', 'FOUR' ]
        msg = groupObj.random(GT) 
     
        mykey = kpabe.keygen(pk, mk, policy)
        
        if debug: print("Encrypt under these attributes: ", attributes)
        ciphertext = kpabe.encrypt(pk, msg, attributes)
        if debug: print(ciphertext)
        
        rec_msg = kpabe.decrypt(ciphertext, mykey)
       
        assert msg == rec_msg 
        if debug: print("Successful Decryption!")

class CPabe09Test(unittest.TestCase):
    def testCPabe(self):    
        #Get the eliptic curve with the bilinear mapping feature needed.
        groupObj = PairingGroup('SS512')

        cpabe = CPabe09(groupObj)
        (msk, pk) = cpabe.setup()
        pol = '((ONE or THREE) and (TWO or FOUR))'
        attr_list = ['THREE', 'ONE', 'TWO']

        if debug: print('Acces Policy: %s' % pol)
        if debug: print('User credential list: %s' % attr_list)
        m = groupObj.random(GT)
        
        cpkey = cpabe.keygen(pk, msk, attr_list)
        if debug: print("\nSecret key: %s" % attr_list)
        if debug:groupObj.debug(cpkey)
        cipher = cpabe.encrypt(pk, m, pol)

        if debug: print("\nCiphertext...")
        if debug:groupObj.debug(cipher)    
        orig_m = cpabe.decrypt(pk, cpkey, cipher)
       
        assert m == orig_m, 'FAILED Decryption!!!' 
        if debug: print('Successful Decryption!')    
        del groupObj

class HybridKPABEncTest(unittest.TestCase):
    def testHybridKPABEnc(self):    
        groupObj = PairingGroup('SS512')
        kpabe = KPabe(groupObj)
        hyb_abe = HybridKPABEnc(kpabe, groupObj)
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
    unittest.main()
