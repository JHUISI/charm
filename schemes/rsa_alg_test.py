'''
:Date: Jul 1, 2011
:authors: Gary Belvin
'''
from binascii import a2b_hex
from pkenc_rsa import RSA_Enc, RSA_Sig
from toolbox.conversion import Conversion
from toolbox.securerandom import SecureRandomFactory, WeakRandom
import unittest
from random import Random

debug = False
class Test(unittest.TestCase):

    def testRSAEnc(self):
        rsa = RSA_Enc()
        (pk, sk) = rsa.keygen(1024)
        
        #m = integer(34567890981234556498) % pk['N']
        m = b'This is a test'
        c = rsa.encrypt(pk, m)
        
        orig_m = rsa.decrypt(pk, sk, c)
    
        assert m == orig_m
            
    def testRSAVector(self):
        # ==================================
        # Example 1: A 1024-bit RSA Key Pair
        # ==================================
        
        # ------------------------------
        # Components of the RSA Key Pair
        # ------------------------------
        
        # RSA modulus n:
        n = a2b_hex('\
        a8 b3 b2 84 af 8e b5 0b 38 70 34 a8 60 f1 46 c4\
        91 9f 31 87 63 cd 6c 55 98 c8 ae 48 11 a1 e0 ab\
        c4 c7 e0 b0 82 d6 93 a5 e7 fc ed 67 5c f4 66 85\
        12 77 2c 0c bc 64 a7 42 c6 c6 30 f5 33 c8 cc 72\
        f6 2a e8 33 c4 0b f2 58 42 e9 84 bb 78 bd bf 97\
        c0 10 7d 55 bd b6 62 f5 c4 e0 fa b9 84 5c b5 14\
        8e f7 39 2d d3 aa ff 93 ae 1e 6b 66 7b b3 d4 24\
        76 16 d4 f5 ba 10 d4 cf d2 26 de 88 d3 9f 16 fb'.replace(' ',''))
        
        # RSA public exponent e:
        e = a2b_hex('010001') 
        
        # RSA private exponent d:
        d = a2b_hex('\
        53 33 9c fd b7 9f c8 46 6a 65 5c 73 16 ac a8 5c\
        55 fd 8f 6d d8 98 fd af 11 95 17 ef 4f 52 e8 fd\
        8e 25 8d f9 3f ee 18 0f a0 e4 ab 29 69 3c d8 3b\
        15 2a 55 3d 4a c4 d1 81 2b 8b 9f a5 af 0e 7f 55\
        fe 73 04 df 41 57 09 26 f3 31 1f 15 c4 d6 5a 73\
        2c 48 31 16 ee 3d 3d 2d 0a f3 54 9a d9 bf 7c bf\
        b7 8a d8 84 f8 4d 5b eb 04 72 4d c7 36 9b 31 de\
        f3 7d 0c f5 39 e9 cf cd d3 de 65 37 29 ea d5 d1'.replace(' ',''))
        
        # Prime p: 
        p = a2b_hex('\
        d3 27 37 e7 26 7f fe 13 41 b2 d5 c0 d1 50 a8 1b\
        58 6f b3 13 2b ed 2f 8d 52 62 86 4a 9c b9 f3 0a\
        f3 8b e4 48 59 8d 41 3a 17 2e fb 80 2c 21 ac f1\
        c1 1c 52 0c 2f 26 a4 71 dc ad 21 2e ac 7c a3 9d'.replace(' ',''))
        
        # Prime q: 
        q = a2b_hex('\
        cc 88 53 d1 d5 4d a6 30 fa c0 04 f4 71 f2 81 c7\
        b8 98 2d 82 24 a4 90 ed be b3 3d 3e 3d 5c c9 3c\
        47 65 70 3d 1d d7 91 64 2f 1f 11 6a 0d d8 52 be\
        24 19 b2 af 72 bf e9 a0 30 e8 60 b0 28 8b 5d 77'.replace(' ',''))
        
        # p's CRT exponent dP: 
        dP = a2b_hex('\
        0e 12 bf 17 18 e9 ce f5 59 9b a1 c3 88 2f e8 04\
        6a 90 87 4e ef ce 8f 2c cc 20 e4 f2 74 1f b0 a3\
        3a 38 48 ae c9 c9 30 5f be cb d2 d7 68 19 96 7d\
        46 71 ac c6 43 1e 40 37 96 8d b3 78 78 e6 95 c1'.replace(' ',''))
        
        # q's CRT exponent dQ: 
        dQ = a2b_hex('\
        95 29 7b 0f 95 a2 fa 67 d0 07 07 d6 09 df d4 fc\
        05 c8 9d af c2 ef 6d 6e a5 5b ec 77 1e a3 33 73\
        4d 92 51 e7 90 82 ec da 86 6e fe f1 3c 45 9e 1a\
        63 13 86 b7 e3 54 c8 99 f5 f1 12 ca 85 d7 15 83'.replace(' ',''))
        
        # CRT coefficient qInv: 
        qInv = a2b_hex('\
        4f 45 6c 50 24 93 bd c0 ed 2a b7 56 a3 a6 ed 4d\
        67 35 2a 69 7d 42 16 e9 32 12 b1 27 a6 3d 54 11\
        ce 6f a9 8d 5d be fd 73 26 3e 37 28 14 27 43 81\
        81 66 ed 7d d6 36 87 dd 2a 8c a1 d2 f4 fb d8 e1'.replace(' ',''))
        
        # ---------------------------------
        # RSAES-OAEP Encryption Example 1.1
        # ---------------------------------
        
        # Message to be encrypted:
        M = a2b_hex('\
        66 28 19 4e 12 07 3d b0 3b a9 4c da 9e f9 53 23\
        97 d5 0d ba 79 b9 87 00 4a fe fe 34'.replace(' ',''))
        
        # Seed:
        seed = a2b_hex('\
        18 b7 76 ea 21 06 9d 69 77 6a 33 e9 6b ad 48 e1\
        dd a0 a5 ef'.replace(' ',''))
        
        # Encryption:
        enc = a2b_hex('\
        35 4f e6 7b 4a 12 6d 5d 35 fe 36 c7 77 79 1a 3f\
        7b a1 3d ef 48 4e 2d 39 08 af f7 22 fa d4 68 fb\
        21 69 6d e9 5d 0b e9 11 c2 d3 17 4f 8a fc c2 01\
        03 5f 7b 6d 8e 69 40 2d e5 45 16 18 c2 1a 53 5f\
        a9 d7 bf c5 b8 dd 9f c2 43 f8 cf 92 7d b3 13 22\
        d6 e8 81 ea a9 1a 99 61 70 e6 57 a0 5a 26 64 26\
        d9 8c 88 00 3f 84 77 c1 22 70 94 a0 d9 fa 1e 8c\
        40 24 30 9c e1 ec cc b5 21 00 35 d4 7a c7 2e 8a'.replace(' ',''))
      
    def testRSASig(self):
        length = Random().randrange(1, 1024)
        length = 128
        M = WeakRandom().myrandom(length, True)
        rsa = RSA_Sig()
        (pk, sk) = rsa.keygen(1024)
        S = rsa.sign(sk, M)
        assert rsa.verify(pk, M, S)
    
    def testPSSVector(self):
        # ==================================
        # Example 1: A 1024-bit RSA Key Pair
        # ==================================
        
        # ------------------------------
        # Components of the RSA Key Pair
        # ------------------------------
        
        # RSA modulus n: 
        n = a2b_hex('\
        a2 ba 40 ee 07 e3 b2 bd 2f 02 ce 22 7f 36 a1 95 \
        02 44 86 e4 9c 19 cb 41 bb bd fb ba 98 b2 2b 0e \
        57 7c 2e ea ff a2 0d 88 3a 76 e6 5e 39 4c 69 d4 \
        b3 c0 5a 1e 8f ad da 27 ed b2 a4 2b c0 00 fe 88 \
        8b 9b 32 c2 2d 15 ad d0 cd 76 b3 e7 93 6e 19 95 \
        5b 22 0d d1 7d 4e a9 04 b1 ec 10 2b 2e 4d e7 75 \
        12 22 aa 99 15 10 24 c7 cb 41 cc 5e a2 1d 00 ee \
        b4 1f 7c 80 08 34 d2 c6 e0 6b ce 3b ce 7e a9 a5 '.replace(' ',''))
        n = Conversion.OS2IP(n, True)
        
        # RSA public exponent e: 
        e = a2b_hex('01 00 01'.replace(' ',''))
        e = Conversion.OS2IP(e, True)
        
        
        # Prime p: 
        p = a2b_hex('\
        d1 7f 65 5b f2 7c 8b 16 d3 54 62 c9 05 cc 04 a2 \
        6f 37 e2 a6 7f a9 c0 ce 0d ce d4 72 39 4a 0d f7 \
        43 fe 7f 92 9e 37 8e fd b3 68 ed df f4 53 cf 00 \
        7a f6 d9 48 e0 ad e7 57 37 1f 8a 71 1e 27 8f 6b '.replace(' ',''))
        p = Conversion.OS2IP(p, True)
        
        # Prime q: 
        q = a2b_hex('\
        c6 d9 2b 6f ee 74 14 d1 35 8c e1 54 6f b6 29 87 \
        53 0b 90 bd 15 e0 f1 49 63 a5 e2 63 5a db 69 34 \
        7e c0 c0 1b 2a b1 76 3f d8 ac 1a 59 2f b2 27 57 \
        46 3a 98 24 25 bb 97 a3 a4 37 c5 bf 86 d0 3f 2f'.replace(' ',''))
        q = Conversion.OS2IP(q, True)
        
        phi_N = (p - 1) * (q - 1)
        e = e % phi_N

        d = e ** -1
        
        # ---------------------------------
        # Step-by-step RSASSA-PSS Signature
        # ---------------------------------
        
        # Message to be signed:
        m = a2b_hex('\
        85 9e ef 2f d7 8a ca 00 30 8b dc 47 11 93 bf 55 \
        bf 9d 78 db 8f 8a 67 2b 48 46 34 f3 c9 c2 6e 64 \
        78 ae 10 26 0f e0 dd 8c 08 2e 53 a5 29 3a f2 17 \
        3c d5 0c 6d 5d 35 4f eb f7 8b 26 02 1c 25 c0 27 \
        12 e7 8c d4 69 4c 9f 46 97 77 e4 51 e7 f8 e9 e0 \
        4c d3 73 9c 6b bf ed ae 48 7f b5 56 44 e9 ca 74 \
        ff 77 a5 3c b7 29 80 2f 6e d4 a5 ff a8 ba 15 98 \
        90 fc '.replace(' ',''))        
        
        # mHash:
        mHash = a2b_hex('\
        37 b6 6a e0 44 58 43 35 3d 47 ec b0 b4 fd 14 c1 \
        10 e6 2d 6a'.replace(' ',''))
        
        # salt:
        salt = a2b_hex('\
        e3 b5 d5 d0 02 c1 bc e5 0c 2b 65 ef 88 a1 88 d8 \
        3b ce 7e 61'.replace(' ',''))
        
        # M':
        mPrime = a2b_hex('\
        00 00 00 00 00 00 00 00 37 b6 6a e0 44 58 43 35 \
        3d 47 ec b0 b4 fd 14 c1 10 e6 2d 6a e3 b5 d5 d0 \
        02 c1 bc e5 0c 2b 65 ef 88 a1 88 d8 3b ce 7e 61'.replace(' ',''))
        
        # H:
        H = a2b_hex('\
        df 1a 89 6f 9d 8b c8 16 d9 7c d7 a2 c4 3b ad 54 \
        6f be 8c fe'.replace(' ',''))
        
        # DB:
        DB = a2b_hex('\
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 01 e3 b5 d5 d0 02 c1 bc e5 0c \
        2b 65 ef 88 a1 88 d8 3b ce 7e 61'.replace(' ',''))
        
        # dbMask:
        dbMask = a2b_hex('\
        66 e4 67 2e 83 6a d1 21 ba 24 4b ed 65 76 b8 67 \
        d9 a4 47 c2 8a 6e 66 a5 b8 7d ee 7f bc 7e 65 af \
        50 57 f8 6f ae 89 84 d9 ba 7f 96 9a d6 fe 02 a4 \
        d7 5f 74 45 fe fd d8 5b 6d 3a 47 7c 28 d2 4b a1 \
        e3 75 6f 79 2d d1 dc e8 ca 94 44 0e cb 52 79 ec \
        d3 18 3a 31 1f c8 97 39 a9 66 43 13 6e 8b 0f 46 \
        5e 87 a4 53 5c d4 c5 9b 10 02 8d'.replace(' ',''))
        
        # maskedDB:
        maskedDB = a2b_hex('\
        66 e4 67 2e 83 6a d1 21 ba 24 4b ed 65 76 b8 67 \
        d9 a4 47 c2 8a 6e 66 a5 b8 7d ee 7f bc 7e 65 af \
        50 57 f8 6f ae 89 84 d9 ba 7f 96 9a d6 fe 02 a4 \
        d7 5f 74 45 fe fd d8 5b 6d 3a 47 7c 28 d2 4b a1 \
        e3 75 6f 79 2d d1 dc e8 ca 94 44 0e cb 52 79 ec \
        d3 18 3a 31 1f c8 96 da 1c b3 93 11 af 37 ea 4a \
        75 e2 4b db fd 5c 1d a0 de 7c ec'.replace(' ',''))
        
        # Encoded message EM:
        EM = a2b_hex('\
        66 e4 67 2e 83 6a d1 21 ba 24 4b ed 65 76 b8 67 \
        d9 a4 47 c2 8a 6e 66 a5 b8 7d ee 7f bc 7e 65 af \
        50 57 f8 6f ae 89 84 d9 ba 7f 96 9a d6 fe 02 a4 \
        d7 5f 74 45 fe fd d8 5b 6d 3a 47 7c 28 d2 4b a1 \
        e3 75 6f 79 2d d1 dc e8 ca 94 44 0e cb 52 79 ec \
        d3 18 3a 31 1f c8 96 da 1c b3 93 11 af 37 ea 4a \
        75 e2 4b db fd 5c 1d a0 de 7c ec df 1a 89 6f 9d \
        8b c8 16 d9 7c d7 a2 c4 3b ad 54 6f be 8c fe bc'.replace(' ',''))
        
        # Signature S, the RSA decryption of EM:
        S = a2b_hex('\
        8d aa 62 7d 3d e7 59 5d 63 05 6c 7e c6 59 e5 44 \
        06 f1 06 10 12 8b aa e8 21 c8 b2 a0 f3 93 6d 54 \
        dc 3b dc e4 66 89 f6 b7 95 1b b1 8e 84 05 42 76 \
        97 18 d5 71 5d 21 0d 85 ef bb 59 61 92 03 2c 42 \
        be 4c 29 97 2c 85 62 75 eb 6d 5a 45 f0 5f 51 87 \
        6f c6 74 3d ed dd 28 ca ec 9b b3 0e a9 9e 02 c3 \
        48 82 69 60 4f e4 97 f7 4c cd 7c 7f ca 16 71 89 \
        71 23 cb d3 0d ef 5d 54 a2 b5 53 6a d9 0a 74 7e'.replace(' ',''))
        
        
        if debug: 
            print("PSS Test Step by Step")
            print("mHash    = Hash(M)", mHash)
            print("salt     = random ", salt)
            print("M'       = Padding || mHash || salt", mPrime)
            print("H        = Hash(M')", H)
            print("DB       = Padding || salt", DB) 
            print("dbMask   = MGF(H, length(DB))", dbMask)
            print("maskedDB = DB xor dbMask", maskedDB)
            print("EM       = maskedDB || H || 0xbc", EM)
            print("S        = RSA decryption of EM", S)
        
        rsa = RSA_Sig()
        sk = { 'phi_N':phi_N, 'd':d , 'N': n}
        sig = rsa.sign(sk, m, salt)
        assert S == sig

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()