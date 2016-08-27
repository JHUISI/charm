from charm.adapters.pkenc_adapt_hybrid import HybridEnc
from charm.adapters.pkenc_adapt_chk04 import CHK04
from charm.adapters.pkenc_adapt_bchk05 import BCHKIBEnc
from charm.adapters.ibenc_adapt_identityhash import HashIDAdapter
from charm.schemes.encap_bchk05 import EncapBCHK
from charm.schemes.ibenc.ibenc_bb03 import IBE_BB04
from charm.schemes.pksig.pksig_bls04 import BLS01
from charm.schemes.pkenc.pkenc_cs98 import CS98
from charm.schemes.pkenc.pkenc_elgamal85 import ElGamal
from charm.schemes.pkenc.pkenc_paillier99 import Pai99
from charm.schemes.pkenc.pkenc_rabin import Rabin_Enc, Rabin_Sig
from charm.schemes.pkenc.pkenc_rsa import RSA_Enc, RSA_Sig
from charm.toolbox.pairinggroup import PairingGroup, GT 
from charm.toolbox.ecgroup import elliptic_curve, ECGroup
from charm.toolbox.eccurve import prime192v1, prime192v2
from charm.toolbox.integergroup import RSAGroup, integer, IntegerGroupQ, IntegerGroup

import unittest

debug = False

class BCHKIBEncTest(unittest.TestCase):
    def testBCHKIBEnc(self):
        groupObj = PairingGroup('SS512')
        ibe = IBE_BB04(groupObj)
        encap = EncapBCHK()
        
        hyb_ibe = BCHKIBEnc(ibe, groupObj, encap)
        
        (pk, sk) = hyb_ibe.keygen()
        if debug:
            print("pk => ", pk)
            print("sk => ", sk)

        msg = b"Hello World!"
        
        ct = hyb_ibe.encrypt(pk, msg)
        if debug:
            print("\nCiphertext")
            print("C1 =>", ct['C1'])
            print("C2 =>", ct['C2'])
            print("tag =>", ct['tag'])

        decrypted_msg = hyb_ibe.decrypt(pk, sk, ct)
        assert decrypted_msg == msg
        if debug: print("Successful Decryption!!! =>", decrypted_msg)
        del groupObj

class CHK04Test(unittest.TestCase):
    def testCHK04(self):
        groupObj = PairingGroup('SS512')
        # instantiate an Identity-Based Encryption scheme
        ibe = IBE_BB04(groupObj)
        hash_ibe = HashIDAdapter(ibe, groupObj)
       
        # instantiate an one-time signature scheme such as BLS04
        ots = BLS01(groupObj)
        
        pkenc = CHK04(hash_ibe, ots, groupObj)
        
        # not sure how to enforce secparam yet
        (pk, sk) = pkenc.keygen(0)
        
        msg = groupObj.random(GT)
        ciphertext = pkenc.encrypt(pk, msg)
        
        rec_msg = pkenc.decrypt(pk, sk, ciphertext)
        assert rec_msg == msg, "FAILED Decryption!!!"
        if debug: print("Successful Decryption!")   

class HybridEncTest(unittest.TestCase):
    def testHybridEnc(self):
        groupObj = ECGroup(prime192v1)
        pkenc = ElGamal(groupObj)
        hyenc = HybridEnc(pkenc, msg_len=groupObj.bitsize())
       
        (pk, sk) = hyenc.keygen()

        # message len should be group.bitsize() len for prime192v1 (or 20 bytes)
        m = b'the hello world msg1'
        cipher = hyenc.encrypt(pk, m)
        orig_m = hyenc.decrypt(pk, sk, cipher)
        assert m == orig_m, "Failed Decryption"
        if debug: print("Successful Decryption!!")

class EC_CS98Test(unittest.TestCase):
    def testEC_CS98(self):
        groupObj = ECGroup(prime192v1)
        pkenc = CS98(groupObj)
        
        (pk, sk) = pkenc.keygen()

        # message len should be group.bitsize() len for prime192v1 (or 20 bytes)
        M = b'the hello world msg1'
        ciphertext = pkenc.encrypt(pk, M)
        message = pkenc.decrypt(pk, sk, ciphertext)
        
        assert M == message, "Failed Decryption!!!"
        if debug: print("SUCCESSFUL DECRYPTION!!! => %s" % message)

class CS98Test(unittest.TestCase):
    def testCS98(self):
        p = integer(156053402631691285300957066846581395905893621007563090607988086498527791650834395958624527746916581251903190331297268907675919283232442999706619659475326192111220545726433895802392432934926242553363253333261282122117343404703514696108330984423475697798156574052962658373571332699002716083130212467463571362679)
        q = integer(78026701315845642650478533423290697952946810503781545303994043249263895825417197979312263873458290625951595165648634453837959641616221499853309829737663096055610272863216947901196216467463121276681626666630641061058671702351757348054165492211737848899078287026481329186785666349501358041565106233731785681339)
        groupObj = IntegerGroup()
        pkenc = CS98(groupObj, p, q)
        
        (pk, sk) = pkenc.keygen(1024)
        M = b"hello world. test message"
        ciphertext = pkenc.encrypt(pk, M)
        
        message = pkenc.decrypt(pk, sk, ciphertext)
        
        assert M == message, "UNSUCCESSFUL!!!! :-( why?"
        if debug: print("SUCCESSFULLY RECOVERED => %s" % message)

class ElGamalTest(unittest.TestCase):
    def testElGamal(self):
        groupObj = ECGroup(prime192v2)
        el = ElGamal(groupObj)   
        (pk, sk) = el.keygen()
        # message len should be group.bitsize() len for prime192v1 (or 20 bytes)
        msg = b'the hello world msg1'
        cipher1 = el.encrypt(pk, msg)
        m = el.decrypt(pk, sk, cipher1)    
        assert m == msg, "Failed Decryption!!!"
        if debug: print("SUCCESSFULLY DECRYPTED!!!")

class ElGamalTest(unittest.TestCase):
    def testElGamal(self):
        p = integer(148829018183496626261556856344710600327516732500226144177322012998064772051982752493460332138204351040296264880017943408846937646702376203733370973197019636813306480144595809796154634625021213611577190781215296823124523899584781302512549499802030946698512327294159881907114777803654670044046376468983244647367)
        q = integer(74414509091748313130778428172355300163758366250113072088661006499032386025991376246730166069102175520148132440008971704423468823351188101866685486598509818406653240072297904898077317312510606805788595390607648411562261949792390651256274749901015473349256163647079940953557388901827335022023188234491622323683)
        groupObj = IntegerGroupQ()
        el = ElGamal(groupObj, p, q) 
        (pk, sk) = el.keygen()
        msg = b"hello world!"
        cipher1 = el.encrypt(pk, msg)
        m = el.decrypt(pk, sk, cipher1)
        assert m == msg, "Failed Decryption!!!"
        if debug: print("SUCCESSFULLY DECRYPTED!!!")

class Pai99Test(unittest.TestCase):
    def testPai99(self):
        group = RSAGroup()
        pai = Pai99(group)
            
        (pk, sk) = pai.keygen()
        
        m1 = 12345678987654321
        m2 = 12345761234123409
        m3 = 24691440221777730 # target
        c1 = pai.encrypt(pk, m1)
        c2 = pai.encrypt(pk, m2)
            
        if debug: print("c1 =>", c1, "\n")
        if debug: print("c2 =>", c2, "\n")
        c3 = c1 + c2
        if debug: print("Homomorphic Add Test...\nc1 + c2 =>", c3, "\n")
                
        orig_m = pai.decrypt(pk, sk, c3)
        if debug: print("orig_m =>", orig_m)
        
        # m3 = m1 + m2
        assert m3 == orig_m, "FAILED Decryption!!!" 
        if debug: print("Successful Decryption!")
        
        if debug: print("Homomorphic Mul Test...\n")
        c4 = c1 + 200
        if debug: print("c4 = c1 + 200 =>", c4, "\n")        
        orig_m = pai.decrypt(pk, sk, c4)
        if debug: print("m4 =>", orig_m, "\n")
        
        c5 = c2 * 20201
        if debug: print("c5 = c2 * 2021 =>", c5, "\n")
        orig_m = pai.decrypt(pk, sk, c5)
        if debug: print("m5 =>", orig_m, "\n")

        messages = range(0, 10)
        cts = []

        for m in messages:
            c = pai.encrypt(pk, pai.encode(pk['n'], m))
            cts.append(c)
            enc_m = pai.encode(pk['n'], m)
            rec_m = pai.decrypt(pk, sk, c)
            assert rec_m == m, "Failed to decrypt"

        # test homomorphic properties (addition)
        c0 = cts[0]
        for i in range(1, len(cts)):
            c0 = c0 + cts[i]

        rec_sum = pai.decrypt(pk, sk, c0)
        print("Total Sum: ", rec_sum)
        tot_sum = sum(list(messages))
        assert rec_sum == tot_sum, "Failed to decrypt to correct sum"

class Rabin_EncTest(unittest.TestCase):
    def testRabin_Enc(self):
        rabin = Rabin_Enc()
        
        (pk, sk) = rabin.keygen(128, 1024)
        
        m = b'This is a test'
        #m = 55
        #m = b'A'
        c = rabin.encrypt(pk, m)
        if debug: print("ct =>", c)
        
        orig_m = rabin.decrypt(pk, sk, c)
        if debug: print("recovered m =>", orig_m)

        assert m == orig_m
        if debug: print("Successful Decryption!!!")

class Rabin_SigTest(unittest.TestCase):
    def testRabin_Sig(self):
        M = b'This is a test message.'
        rabin = Rabin_Sig()
        (pk, sk) = rabin.keygen(1024)
        S = rabin.sign(sk, M)
        assert rabin.verify(pk, M, S)
        if debug: print("Successful Signature!")

class RSA_EncTest(unittest.TestCase):
    def testRSA_Enc(self):
        rsa = RSA_Enc()
        
        (pk, sk) = rsa.keygen(1024)
        
        m = b'This is a test'
        c = rsa.encrypt(pk, m)
        if debug: print("ct =>", c)
        
        orig_m = rsa.decrypt(pk, sk, c)
        if debug: print("recovered m =>", orig_m)

        assert m == orig_m
        if debug: print("Successful Decryption!!!")

class RSA_SigTest(unittest.TestCase):
    def testRSA_Sig(self):
        M = b'This is a test message.'
        rsa = RSA_Sig()
        (pk, sk) = rsa.keygen(1024)
        S = rsa.sign(sk, M)
        assert rsa.verify(pk, M, S)
        if debug: print("Successful Signature!")

if __name__ == "__main__":
    unittest.main()
