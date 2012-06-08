'''
:Date: Jul 1, 2011
:authors: Gary Belvin
'''
from binascii import a2b_hex
from charm.schemes.pkenc.pkenc_rsa import RSA_Enc, RSA_Sig
from charm.toolbox.conversion import Conversion
from charm.toolbox.securerandom import WeakRandom
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
    
        assert m == orig_m, 'o: =>%s\nm: =>%s' % (orig_m, m)
            
    def testRSAVector(self):
        # ==================================
        # Example 1: A 1024-bit RSA Key Pair
        # ==================================
        
        # ------------------------------
        # Components of the RSA Key Pair
        # ------------------------------
        
        # RSA modulus n:
        n = a2b_hex(bytes('\
        bb f8 2f 09 06 82 ce 9c 23 38 ac 2b 9d a8 71 f7 \
        36 8d 07 ee d4 10 43 a4 40 d6 b6 f0 74 54 f5 1f \
        b8 df ba af 03 5c 02 ab 61 ea 48 ce eb 6f cd 48 \
        76 ed 52 0d 60 e1 ec 46 19 71 9d 8a 5b 8b 80 7f \
        af b8 e0 a3 df c7 37 72 3e e6 b4 b7 d9 3a 25 84 \
        ee 6a 64 9d 06 09 53 74 88 34 b2 45 45 98 39 4e \
        e0 aa b1 2d 7b 61 a5 1f 52 7a 9a 41 f6 c1 68 7f \
        e2 53 72 98 ca 2a 8f 59 46 f8 e5 fd 09 1d bd cb '.replace(' ',''),'utf-8'))
        n = Conversion.OS2IP(n, True)
        
        # RSA public exponent e:
        e = a2b_hex(b'11')
        e = Conversion.OS2IP(e, True)
        
        # Prime p: 
        p = a2b_hex(bytes('\
        ee cf ae 81 b1 b9 b3 c9 08 81 0b 10 a1 b5 60 01 \
        99 eb 9f 44 ae f4 fd a4 93 b8 1a 9e 3d 84 f6 32 \
        12 4e f0 23 6e 5d 1e 3b 7e 28 fa e7 aa 04 0a 2d \
        5b 25 21 76 45 9d 1f 39 75 41 ba 2a 58 fb 65 99 '.replace(' ',''),'utf-8'))
        p = Conversion.OS2IP(p, True)
        
        # Prime q: 
        q = a2b_hex(bytes('\
        c9 7f b1 f0 27 f4 53 f6 34 12 33 ea aa d1 d9 35 \
        3f 6c 42 d0 88 66 b1 d0 5a 0f 20 35 02 8b 9d 86 \
        98 40 b4 16 66 b4 2e 92 ea 0d a3 b4 32 04 b5 cf \
        ce 33 52 52 4d 04 16 a5 a4 41 e7 00 af 46 15 03'.replace(' ',''),'utf-8'))
        q = Conversion.OS2IP(q, True)
        
        phi_N = (p - 1) * (q - 1)
        e = e % phi_N

        d = e ** -1
        
        # ----------------------------------
        # Step-by-step RSAES-OAEP Encryption
        # ----------------------------------
        
        # Message to be encrypted:
        M = a2b_hex(bytes('\
        d4 36 e9 95 69 fd 32 a7 c8 a0 5b bc 90 d3 2c 49'.replace(' ',''),'utf-8'))
        
        lhash = a2b_hex(bytes('\
        da 39 a3 ee 5e 6b 4b 0d 32 55 bf ef 95 60 18 90 \
        af d8 07 09'.replace(' ', ''),'utf-8'))
        
        # DB:
        db = a2b_hex(bytes('\
        da 39 a3 ee 5e 6b 4b 0d 32 55 bf ef 95 60 18 90 \
        af d8 07 09 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 01 d4 36 e9 95 69 \
        fd 32 a7 c8 a0 5b bc 90 d3 2c 49'.replace(' ', ''),'utf-8')) 
        
        # Seed:
        seed = a2b_hex(bytes('\
        aa fd 12 f6 59 ca e6 34 89 b4 79 e5 07 6d de c2 \
        f0 6c b5 8f '.replace(' ',''),'utf-8'))
        
        # dbMask:
        dbmask = a2b_hex(bytes('\
        06 e1 de b2 36 9a a5 a5 c7 07 d8 2c 8e 4e 93 24 \
        8a c7 83 de e0 b2 c0 46 26 f5 af f9 3e dc fb 25 \
        c9 c2 b3 ff 8a e1 0e 83 9a 2d db 4c dc fe 4f f4 \
        77 28 b4 a1 b7 c1 36 2b aa d2 9a b4 8d 28 69 d5 \
        02 41 21 43 58 11 59 1b e3 92 f9 82 fb 3e 87 d0 \
        95 ae b4 04 48 db 97 2f 3a c1 4e af f4 9c 8c 3b \
        7c fc 95 1a 51 ec d1 dd e6 12 64'.replace(' ',''),'utf-8')) 
        
        # maskedDB:
        maskeddb = a2b_hex(bytes('\
        dc d8 7d 5c 68 f1 ee a8 f5 52 67 c3 1b 2e 8b b4 \
        25 1f 84 d7 e0 b2 c0 46 26 f5 af f9 3e dc fb 25 \
        c9 c2 b3 ff 8a e1 0e 83 9a 2d db 4c dc fe 4f f4 \
        77 28 b4 a1 b7 c1 36 2b aa d2 9a b4 8d 28 69 d5 \
        02 41 21 43 58 11 59 1b e3 92 f9 82 fb 3e 87 d0 \
        95 ae b4 04 48 db 97 2f 3a c1 4f 7b c2 75 19 52 \
        81 ce 32 d2 f1 b7 6d 4d 35 3e 2d '.replace(' ',''),'utf-8'))
        
        # seedMask:
        seedmask = a2b_hex(bytes('\
        41 87 0b 5a b0 29 e6 57 d9 57 50 b5 4c 28 3c 08 \
        72 5d be a9 '.replace(' ',''),'utf-8'))
        
        # maskedSeed:
        maskedseed = a2b_hex(bytes('\
        eb 7a 19 ac e9 e3 00 63 50 e3 29 50 4b 45 e2 ca \
        82 31 0b 26 '.replace(' ',''),'utf-8'))
        
        # EM = 00 || maskedSeed || maskedDB:
        em = a2b_hex(bytes('\
        00 eb 7a 19 ac e9 e3 00 63 50 e3 29 50 4b 45 e2 \
        ca 82 31 0b 26 dc d8 7d 5c 68 f1 ee a8 f5 52 67 \
        c3 1b 2e 8b b4 25 1f 84 d7 e0 b2 c0 46 26 f5 af \
        f9 3e dc fb 25 c9 c2 b3 ff 8a e1 0e 83 9a 2d db \
        4c dc fe 4f f4 77 28 b4 a1 b7 c1 36 2b aa d2 9a \
        b4 8d 28 69 d5 02 41 21 43 58 11 59 1b e3 92 f9 \
        82 fb 3e 87 d0 95 ae b4 04 48 db 97 2f 3a c1 4f \
        7b c2 75 19 52 81 ce 32 d2 f1 b7 6d 4d 35 3e 2d '.replace(' ',''),'utf-8'))
            
        # Encryption:
        enc = a2b_hex(bytes('\
        12 53 e0 4d c0 a5 39 7b b4 4a 7a b8 7e 9b f2 a0 \
        39 a3 3d 1e 99 6f c8 2a 94 cc d3 00 74 c9 5d f7 \
        63 72 20 17 06 9e 52 68 da 5d 1c 0b 4f 87 2c f6 \
        53 c1 1d f8 23 14 a6 79 68 df ea e2 8d ef 04 bb \
        6d 84 b1 c3 1d 65 4a 19 70 e5 78 3b d6 eb 96 a0 \
        24 c2 ca 2f 4a 90 fe 9f 2e f5 c9 c1 40 e5 bb 48 \
        da 95 36 ad 87 00 c8 4f c9 13 0a de a7 4e 55 8d \
        51 a7 4d df 85 d8 b5 0d e9 68 38 d6 06 3e 09 55 '.replace(' ',''),'utf-8'))
        
        rsa = RSA_Enc()
        pk = { 'N':n, 'e':e }
        sk = { 'phi_N':phi_N, 'd':d , 'N': n}
        
        c = rsa.encrypt(pk, M, seed)
        C = Conversion.IP2OS(c)
        
        if debug: 
            print("RSA OEAP step by step")
            print("Label L  = empty string")
            print("lHash      = ", lhash)
            print("DB         = ", db)
            print("seed       = ", seed)
            print("dbMask     = ", dbmask)
            print("maskedDB   = ", maskeddb)
            print("seedMask   = ", seedmask)
            print("maskedSeed = ", maskedseed)
            print("EM         = ", em)
        
        assert C == enc
      
    
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
        n = a2b_hex(bytes('\
        a2 ba 40 ee 07 e3 b2 bd 2f 02 ce 22 7f 36 a1 95 \
        02 44 86 e4 9c 19 cb 41 bb bd fb ba 98 b2 2b 0e \
        57 7c 2e ea ff a2 0d 88 3a 76 e6 5e 39 4c 69 d4 \
        b3 c0 5a 1e 8f ad da 27 ed b2 a4 2b c0 00 fe 88 \
        8b 9b 32 c2 2d 15 ad d0 cd 76 b3 e7 93 6e 19 95 \
        5b 22 0d d1 7d 4e a9 04 b1 ec 10 2b 2e 4d e7 75 \
        12 22 aa 99 15 10 24 c7 cb 41 cc 5e a2 1d 00 ee \
        b4 1f 7c 80 08 34 d2 c6 e0 6b ce 3b ce 7e a9 a5 '.replace(' ',''),'utf-8'))
        n = Conversion.OS2IP(n, True)
        
        # RSA public exponent e: 
        e = a2b_hex(bytes('01 00 01'.replace(' ',''),'utf-8'))
        e = Conversion.OS2IP(e, True)
        
        
        # Prime p: 
        p = a2b_hex(bytes('\
        d1 7f 65 5b f2 7c 8b 16 d3 54 62 c9 05 cc 04 a2 \
        6f 37 e2 a6 7f a9 c0 ce 0d ce d4 72 39 4a 0d f7 \
        43 fe 7f 92 9e 37 8e fd b3 68 ed df f4 53 cf 00 \
        7a f6 d9 48 e0 ad e7 57 37 1f 8a 71 1e 27 8f 6b '.replace(' ',''),'utf-8'))
        p = Conversion.OS2IP(p, True)
        
        # Prime q: 
        q = a2b_hex(bytes('\
        c6 d9 2b 6f ee 74 14 d1 35 8c e1 54 6f b6 29 87 \
        53 0b 90 bd 15 e0 f1 49 63 a5 e2 63 5a db 69 34 \
        7e c0 c0 1b 2a b1 76 3f d8 ac 1a 59 2f b2 27 57 \
        46 3a 98 24 25 bb 97 a3 a4 37 c5 bf 86 d0 3f 2f'.replace(' ',''),'utf-8'))
        q = Conversion.OS2IP(q, True)
        
        phi_N = (p - 1) * (q - 1)
        e = e % phi_N

        d = e ** -1
        
        # ---------------------------------
        # Step-by-step RSASSA-PSS Signature
        # ---------------------------------
        
        # Message to be signed:
        m = a2b_hex(bytes('\
        85 9e ef 2f d7 8a ca 00 30 8b dc 47 11 93 bf 55 \
        bf 9d 78 db 8f 8a 67 2b 48 46 34 f3 c9 c2 6e 64 \
        78 ae 10 26 0f e0 dd 8c 08 2e 53 a5 29 3a f2 17 \
        3c d5 0c 6d 5d 35 4f eb f7 8b 26 02 1c 25 c0 27 \
        12 e7 8c d4 69 4c 9f 46 97 77 e4 51 e7 f8 e9 e0 \
        4c d3 73 9c 6b bf ed ae 48 7f b5 56 44 e9 ca 74 \
        ff 77 a5 3c b7 29 80 2f 6e d4 a5 ff a8 ba 15 98 \
        90 fc '.replace(' ',''),'utf-8'))        
        
        # mHash:
        mHash = a2b_hex(bytes('\
        37 b6 6a e0 44 58 43 35 3d 47 ec b0 b4 fd 14 c1 \
        10 e6 2d 6a'.replace(' ',''),'utf-8'))
        
        # salt:
        salt = a2b_hex(bytes('\
        e3 b5 d5 d0 02 c1 bc e5 0c 2b 65 ef 88 a1 88 d8 \
        3b ce 7e 61'.replace(' ',''),'utf-8'))
        
        # M':
        mPrime = a2b_hex(bytes('\
        00 00 00 00 00 00 00 00 37 b6 6a e0 44 58 43 35 \
        3d 47 ec b0 b4 fd 14 c1 10 e6 2d 6a e3 b5 d5 d0 \
        02 c1 bc e5 0c 2b 65 ef 88 a1 88 d8 3b ce 7e 61'.replace(' ',''),'utf-8'))
        
        # H:
        H = a2b_hex(bytes('\
        df 1a 89 6f 9d 8b c8 16 d9 7c d7 a2 c4 3b ad 54 \
        6f be 8c fe'.replace(' ',''),'utf-8'))
        
        # DB:
        DB = a2b_hex(bytes('\
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 \
        00 00 00 00 00 00 01 e3 b5 d5 d0 02 c1 bc e5 0c \
        2b 65 ef 88 a1 88 d8 3b ce 7e 61'.replace(' ',''),'utf-8'))
        
        # dbMask:
        dbMask = a2b_hex(bytes('\
        66 e4 67 2e 83 6a d1 21 ba 24 4b ed 65 76 b8 67 \
        d9 a4 47 c2 8a 6e 66 a5 b8 7d ee 7f bc 7e 65 af \
        50 57 f8 6f ae 89 84 d9 ba 7f 96 9a d6 fe 02 a4 \
        d7 5f 74 45 fe fd d8 5b 6d 3a 47 7c 28 d2 4b a1 \
        e3 75 6f 79 2d d1 dc e8 ca 94 44 0e cb 52 79 ec \
        d3 18 3a 31 1f c8 97 39 a9 66 43 13 6e 8b 0f 46 \
        5e 87 a4 53 5c d4 c5 9b 10 02 8d'.replace(' ',''),'utf-8'))
        
        # maskedDB:
        maskedDB = a2b_hex(bytes('\
        66 e4 67 2e 83 6a d1 21 ba 24 4b ed 65 76 b8 67 \
        d9 a4 47 c2 8a 6e 66 a5 b8 7d ee 7f bc 7e 65 af \
        50 57 f8 6f ae 89 84 d9 ba 7f 96 9a d6 fe 02 a4 \
        d7 5f 74 45 fe fd d8 5b 6d 3a 47 7c 28 d2 4b a1 \
        e3 75 6f 79 2d d1 dc e8 ca 94 44 0e cb 52 79 ec \
        d3 18 3a 31 1f c8 96 da 1c b3 93 11 af 37 ea 4a \
        75 e2 4b db fd 5c 1d a0 de 7c ec'.replace(' ',''),'utf-8'))
        
        # Encoded message EM:
        EM = a2b_hex(bytes('\
        66 e4 67 2e 83 6a d1 21 ba 24 4b ed 65 76 b8 67 \
        d9 a4 47 c2 8a 6e 66 a5 b8 7d ee 7f bc 7e 65 af \
        50 57 f8 6f ae 89 84 d9 ba 7f 96 9a d6 fe 02 a4 \
        d7 5f 74 45 fe fd d8 5b 6d 3a 47 7c 28 d2 4b a1 \
        e3 75 6f 79 2d d1 dc e8 ca 94 44 0e cb 52 79 ec \
        d3 18 3a 31 1f c8 96 da 1c b3 93 11 af 37 ea 4a \
        75 e2 4b db fd 5c 1d a0 de 7c ec df 1a 89 6f 9d \
        8b c8 16 d9 7c d7 a2 c4 3b ad 54 6f be 8c fe bc'.replace(' ',''),'utf-8'))
        
        # Signature S, the RSA decryption of EM:
        S = a2b_hex(bytes('\
        8d aa 62 7d 3d e7 59 5d 63 05 6c 7e c6 59 e5 44 \
        06 f1 06 10 12 8b aa e8 21 c8 b2 a0 f3 93 6d 54 \
        dc 3b dc e4 66 89 f6 b7 95 1b b1 8e 84 05 42 76 \
        97 18 d5 71 5d 21 0d 85 ef bb 59 61 92 03 2c 42 \
        be 4c 29 97 2c 85 62 75 eb 6d 5a 45 f0 5f 51 87 \
        6f c6 74 3d ed dd 28 ca ec 9b b3 0e a9 9e 02 c3 \
        48 82 69 60 4f e4 97 f7 4c cd 7c 7f ca 16 71 89 \
        71 23 cb d3 0d ef 5d 54 a2 b5 53 6a d9 0a 74 7e'.replace(' ',''),'utf-8'))
        
        
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
