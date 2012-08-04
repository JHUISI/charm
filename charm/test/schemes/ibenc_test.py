from charm.adapters.ibenc_adapt_hybrid import HybridIBEnc
from charm.adapters.ibenc_adapt_identityhash import HashIDAdapter
from charm.schemes.ibenc.ibenc_bb03 import IBE_BB04
from charm.schemes.ibenc.ibenc_bf01 import IBE_BonehFranklin
from charm.schemes.ibenc.ibenc_ckrs09 import IBE_CKRS
from charm.schemes.ibenc.ibenc_lsw08 import IBE_Revoke
from charm.schemes.ibenc.ibenc_sw05 import IBE_SW05_LUC
from charm.schemes.ibenc.ibenc_waters05 import IBE_N04
from charm.schemes.ibenc.ibenc_waters09 import DSE09
from charm.toolbox.pairinggroup import PairingGroup,ZR,GT
from charm.toolbox.hash_module import Waters
import unittest

debug = False

class HybridIBEncTest(unittest.TestCase):
    def testHybridIBEnc(self):
        groupObj = PairingGroup('SS512')
        ibe = IBE_BB04(groupObj)
        
        hashID = HashIDAdapter(ibe, groupObj)
        
        hyb_ibe = HybridIBEnc(hashID, groupObj)
        
        (pk, mk) = hyb_ibe.setup()

        kID = 'waldoayo@gmail.com'
        sk = hyb_ibe.extract(mk, kID)

        msg = b"This is a test message."
        
        ct = hyb_ibe.encrypt(pk, kID, msg)
        if debug:
            print("Ciphertext")
            print("c1 =>", ct['c1'])
            print("c2 =>", ct['c2'])
        
        decrypted_msg = hyb_ibe.decrypt(pk, sk, ct)
        if debug: print("Result =>", decrypted_msg)
        assert decrypted_msg == msg
        del groupObj

class HashIDAdapterTest(unittest.TestCase):
    def testHashIDAdapter(self):
        group = PairingGroup('SS512')
        
        ibe = IBE_BB04(group)
        
        hashID = HashIDAdapter(ibe, group)
        
        (pk, mk) = hashID.setup()
        
        kID = 'waldoayo@email.com'
        sk = hashID.extract(mk, kID)
        if debug: print("Keygen for %s" % kID)
        if debug: print(sk)
        
        m = group.random(GT)
        ct = hashID.encrypt(pk, kID, m)
        
        orig_m = hashID.decrypt(pk, sk, ct)
        
        assert m == orig_m
        if debug: print("Successful Decryption!!!")
        if debug: print("Result =>", orig_m)

class IBE_BB04Test(unittest.TestCase):
    def testIBE_BB04(self):
        # initialize the element object so that object references have global scope
        groupObj = PairingGroup('MNT224')
        ibe = IBE_BB04(groupObj)
        (params, mk) = ibe.setup()

        # represents public identity
        kID = groupObj.random(ZR)
        key = ibe.extract(mk, kID)

        M = groupObj.random(GT)
        cipher = ibe.encrypt(params, kID, M)
        m = ibe.decrypt(params, key, cipher)

        assert m == M, "FAILED Decryption!"
        if debug: print("Successful Decryption!! M => '%s'" % m)

class IBE_BonehFranklinTest(unittest.TestCase):
    def testIBE_BonehFranklin(self):
        groupObj = PairingGroup('MNT224', secparam=1024)    
        ibe = IBE_BonehFranklin(groupObj)
        
        (pk, sk) = ibe.setup()
        
        id = 'user@email.com'
        key = ibe.extract(sk, id)
        
        m = "hello world!!!!!"
        ciphertext = ibe.encrypt(pk, id, m)

        msg = ibe.decrypt(pk, key, ciphertext)
        assert msg == m,  "failed decrypt: \n%s\n%s" % (msg, m)
        if debug: print("Successful Decryption!!!")

class IBE_CKRSTest(unittest.TestCase):
    def testIBE_CKRS(self):
        groupObj = PairingGroup('SS512')
        ibe = IBE_CKRS(groupObj)
        (mpk, msk) = ibe.setup()

        # represents public identity
        ID = "bob@mail.com"
        sk = ibe.extract(mpk, msk, ID)

        M = groupObj.random(GT)
        ct = ibe.encrypt(mpk, ID, M)
        m = ibe.decrypt(mpk, sk, ct)
        if debug: print('m    =>', m)

        assert m == M, "FAILED Decryption!"
        if debug: print("Successful Decryption!!! m => '%s'" % m)

class IBE_RevokeTest(unittest.TestCase):
    def testIBE_Revoke(self):
        # scheme designed for symmetric billinear groups
        grp = PairingGroup('SS512')
        n = 5 # total # of users
        
        ibe = IBE_Revoke(grp)
        
        ID = "user2@email.com"
        S = ["user1@email.com", "user3@email.com", "user4@email.com"]
        (mpk, msk) = ibe.setup(n)
        
        sk = ibe.keygen(mpk, msk, ID)
        if debug: print("Keygen...\nsk :=", sk)
        
        M = grp.random(GT)
        
        ct = ibe.encrypt(mpk, M, S)
        if debug: print("Ciphertext...\nct :=", ct)
        
        m = ibe.decrypt(S, ct, sk)
        assert M == m, "Decryption FAILED!"
        if debug: print("Successful Decryption!!!")

class IBE_SW05_LUCTest(unittest.TestCase):
    def testIBE_SW05_LUC(self):
        # initialize the element object so that object references have global scope
        groupObj = PairingGroup('SS512')
        n = 6; d = 4
        ibe = IBE_SW05_LUC(groupObj)
        (pk, mk) = ibe.setup(n, d)
        if debug:
            print("Parameter Setup...")
            print("pk =>", pk)
            print("mk =>", mk)

        w = ['insurance', 'id=2345', 'oncology', 'doctor', 'nurse', 'JHU'] #private identity
        wPrime = ['insurance', 'id=2345', 'doctor', 'oncology', 'JHU', 'billing', 'misc'] #public identity for encrypt

        (w_hashed, sk) = ibe.extract(mk, w, pk, d, n)

        M = groupObj.random(GT)
        cipher = ibe.encrypt(pk, wPrime, M, n)
        m = ibe.decrypt(pk, sk, cipher, w_hashed, d)

        assert m == M, "FAILED Decryption: \nrecovered m = %s and original m = %s" % (m, M)
        if debug: print("Successful Decryption!! M => '%s'" % m)

class IBE_N04Test(unittest.TestCase):
    def testIBE_N04(self):
        # initialize the element object so that object references have global scope
        groupObj = PairingGroup('SS512')
        waters = Waters(groupObj)
        ibe = IBE_N04(groupObj)
        (pk, mk) = ibe.setup()

        # represents public identity
        ID = "bob@mail.com"
        kID = waters.hash(ID)
        #if debug: print("Bob's key  =>", kID)
        key = ibe.extract(mk, kID)

        M = groupObj.random(GT)
        cipher = ibe.encrypt(pk, kID, M)
        m = ibe.decrypt(pk, key, cipher)
        #print('m    =>', m)

        assert m == M, "FAILED Decryption!"
        if debug: print("Successful Decryption!!! m => '%s'" % m)
        del groupObj

class DSE09Test(unittest.TestCase):
    def testDSE09(self):
        grp = PairingGroup('SS512')
        
        ibe = DSE09(grp)
        
        ID = "user2@email.com"
        (mpk, msk) = ibe.setup()
        
        sk = ibe.keygen(mpk, msk, ID)
        if debug: print("Keygen...\nsk :=", sk)
        
        M = grp.random(GT)    
        ct = ibe.encrypt(mpk, M, ID)
        if debug: print("Ciphertext...\nct :=", ct)
        
        m = ibe.decrypt(ct, sk)
        assert M == m, "Decryption FAILED!"
        if debug: print("Successful Decryption!!!")

if __name__ == "__main__":
    unittest.main()
