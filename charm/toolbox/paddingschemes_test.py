'''
:Date: Jun 17, 2011
:Authors: Gary Belvin
'''
import unittest
from  charm.toolbox.paddingschemes import OAEPEncryptionPadding, MGF1, hashFunc, PSSPadding, PKCS7Padding
from binascii import a2b_hex

debug = False
class Test(unittest.TestCase):

    def testOEAPVector1(self):
        # OAEP Test vector taken from Appendix C 
        #ftp://ftp.rsa.com/pub/rsalabs/rsa_algorithm/rsa-oaep_spec.pdf
        
        # --------------------------------------------------------------------------------
        # Message:
        m     = a2b_hex(bytes('d4 36 e9 95 69 fd 32 a7 c8 a0 5b bc 90 d3 2c 49'.replace(' ',''),'utf-8'))
        label = ""
        lhash = a2b_hex(bytes("da 39 a3 ee 5e 6b 4b 0d 32 55 bf ef 95 60 18 90 af d8 07 09".replace(' ',""),'utf-8'))
        DB    = a2b_hex(bytes("da 39 a3 ee 5e 6b 4b 0d 32 55 bf ef 95 60 18 90 af d8 07 09 00 00 00 00\
                         00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00\
                         00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00\
                         00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 d4 36 e9 95 69\
                         fd 32 a7 c8 a0 5b bc 90 d3 2c 49".replace(" ", ""),'utf-8'))
 
        seed  = a2b_hex(bytes("aa fd 12 f6 59 ca e6 34 89 b4 79 e5 07 6d de c2 f0 6c b5 8f".replace(' ' ,''),'utf-8'))
        #dbmask = dbMask = MGF (seed , 107):
        dbmask= a2b_hex(bytes("06 e1 de b2 36 9a a5 a5 c7 07 d8 2c 8e 4e 93 24 8a c7 83 de e0 b2 c0 46\
                         26 f5 af f9 3e dc fb 25 c9 c2 b3 ff 8a e1 0e 83 9a 2d db 4c dc fe 4f f4\
                         77 28 b4 a1 b7 c1 36 2b aa d2 9a b4 8d 28 69 d5 02 41 21 43 58 11 59 1b\
                         e3 92 f9 82 fb 3e 87 d0 95 ae b4 04 48 db 97 2f 3a c1 4e af f4 9c 8c 3b\
                         7c fc 95 1a 51 ec d1 dd e6 12 64".replace(" ",""),'utf-8'))
        #maskedDB
        #seedMask = M GF (maskedDB, 20):
        seedMask = a2b_hex(bytes("41 87 0b 5a b0 29 e6 57 d9 57 50 b5 4c 28 3c 08 72 5d be a9".replace(' ',''),'utf-8'))
        maskedSeed= a2b_hex(bytes("eb 7a 19 ac e9 e3 00 63 50 e3 29 50 4b 45 e2 ca 82 31 0b 26".replace(' ',''),'utf-8'))

        #EM = maskedSeed maskedDB
        EM       = a2b_hex(bytes("00 eb 7a 19 ac e9 e3 00 63 50 e3 29 50 4b 45 e2 ca 82 31 0b 26 dc d8 7d 5c\
                            68 f1 ee a8 f5 52 67 c3 1b 2e 8b b4 25 1f 84 d7 e0 b2 c0 46 26 f5 af f9\
                            3e dc fb 25 c9 c2 b3 ff 8a e1 0e 83 9a 2d db 4c dc fe 4f f4 77 28 b4 a1\
                            b7 c1 36 2b aa d2 9a b4 8d 28 69 d5 02 41 21 43 58 11 59 1b e3 92 f9 82\
                            fb 3e 87 d0 95 ae b4 04 48 db 97 2f 3a c1 4f 7b c2 75 19 52 81 ce 32 d2\
                            f1 b7 6d 4d 35 3e 2d".replace(" ",''),'utf-8')) 

        if debug:
            print("Test Vector 1:")
            print("mesg  =>", m)
            print("label =>", label)
            print("lhash =>", lhash)    #Correct
            print("DB    =>", DB)       #Correct
            print("DBMask=>", dbmask)   #Correct
            print("seedMask=>", seedMask)   #Correct
            print("maskedseed=>", maskedSeed)

        c = OAEPEncryptionPadding()
        E = c.encode(m, 128,"",seed)
        self.assertEqual(EM, E)
    
    def testOAEPRoundTripEquiv(self):
        oaep = OAEPEncryptionPadding()
        m = b'This is a test message'
        ct = oaep.encode(m, 64)
        pt = oaep.decode(ct)
        self.assertEqual(m, pt, 'Decoded message is not equal to encoded message\n'\
                         'ct: %s\nm:  %s\npt: %s' % (ct, m, pt))
    
    @unittest.skip("Unnecessary length test")
    def testMFGLength(self):
        seed = ""
        hashFn = OAEPEncryptionPadding().hashFn
        hLen =  OAEPEncryptionPadding().hashFnOutputBytes
        
        for mbytes in range(100):
            a = MGF1(seed, mbytes, hashFn, hLen)
            self.assertEqual(len(a), mbytes, 'MFG output wrong size')

    def testMFGvector(self):
        hashFn = OAEPEncryptionPadding().hashFn
        hLen =  OAEPEncryptionPadding().hashFnOutputBytes
        seed  = a2b_hex(bytes("aa fd 12 f6 59 ca e6 34 89 b4 79 e5 07 6d de c2 f0 6c b5 8f".replace(' ' ,''),'utf-8'))
        #dbmask = dbMask = MGF (seed , 107):
        dbmask= a2b_hex(bytes("06 e1 de b2 36 9a a5 a5 c7 07 d8 2c 8e 4e 93 24 8a c7 83 de e0 b2 c0 46\
                         26 f5 af f9 3e dc fb 25 c9 c2 b3 ff 8a e1 0e 83 9a 2d db 4c dc fe 4f f4\
                         77 28 b4 a1 b7 c1 36 2b aa d2 9a b4 8d 28 69 d5 02 41 21 43 58 11 59 1b\
                         e3 92 f9 82 fb 3e 87 d0 95 ae b4 04 48 db 97 2f 3a c1 4e af f4 9c 8c 3b\
                         7c fc 95 1a 51 ec d1 dd e6 12 64".replace(" ",""),'utf-8'))
        a = MGF1(seed, 107, hashFn, hLen)
        self.assertEqual(dbmask, a)
        
    def testSHA1Vector(self):
        hashFn = hashFunc('sha1')
        V0 = (b"", a2b_hex(bytes("da39a3ee5e6b4b0d3255bfef95601890afd80709",'utf-8')))
        V1 = (bytes("The quick brown fox jumps over the lazy dog", 'utf-8'), a2b_hex(bytes("2fd4e1c67a2d28fced849ee1bb76e7391b93eb12",'utf-8'))) #ASCII encoding
        V2 = (b'The quick brown fox jumps over the lazy dog', a2b_hex(bytes("2fd4e1c67a2d28fced849ee1bb76e7391b93eb12",'utf-8'))) #binary data
        #print("str => ", V2[0])
        #print("H(s)=> ", hashFn(V2[0]))
        #print("stnd=> ", V2[1])
        
        self.assertEqual(hashFn(V0[0]), V0[1], 'empty string')
        self.assertEqual(hashFn(V1[0]), V1[1], 'quick fox')
        self.assertEqual(hashFn(V2[0]), V2[1])
    
    
    def testPSSRountTripEquiv(self):
        pss = PSSPadding()
        m = b'This is a test message'
        em = pss.encode(m)
        self.assertTrue(pss.verify(m, em))
    
    def testPSSTestVector(self):
        # Test vector taken from http://www.rsa.com/rsalabs/node.asp?id=2125
        # ---------------------------------
        # Step-by-step RSASSA-PSS Signature
        # ---------------------------------
        
        # Message M to be signed:
        m = a2b_hex(bytes('85 9e ef 2f d7 8a ca 00 30 8b dc 47 11 93 bf 55\
        bf 9d 78 db 8f 8a 67 2b 48 46 34 f3 c9 c2 6e 64\
        78 ae 10 26 0f e0 dd 8c 08 2e 53 a5 29 3a f2 17\
        3c d5 0c 6d 5d 35 4f eb f7 8b 26 02 1c 25 c0 27\
        12 e7 8c d4 69 4c 9f 46 97 77 e4 51 e7 f8 e9 e0\
        4c d3 73 9c 6b bf ed ae 48 7f b5 56 44 e9 ca 74\
        ff 77 a5 3c b7 29 80 2f 6e d4 a5 ff a8 ba 15 98\
        90 fc'.replace(" ", ""),'utf-8'))

        # mHash    = Hash(M)
        # salt     = random string of octets
        # M'       = Padding || mHash || salt
        # H        = Hash(M')
        # DB       = Padding || salt 
        # dbMask   = MGF(H, length(DB))
        # maskedDB = DB xor dbMask (leftmost bit set to
        #            zero)
        # EM       = maskedDB || H || 0xbc
        
        # mHash:
        mHash = a2b_hex(bytes('37 b6 6a e0 44 58 43 35 3d 47 ec b0 b4 fd 14 c1\
        10 e6 2d 6a'.replace(" ", ""),'utf-8'))
        
        # salt:
        salt = a2b_hex(bytes('e3 b5 d5 d0 02 c1 bc e5 0c 2b 65 ef 88 a1 88 d8\
        3b ce 7e 61'.replace(" ", ""),'utf-8'))
        
        # M':
        mPrime = a2b_hex(bytes('00 00 00 00 00 00 00 00 37 b6 6a e0 44 58 43 35\
        3d 47 ec b0 b4 fd 14 c1 10 e6 2d 6a e3 b5 d5 d0\
        02 c1 bc e5 0c 2b 65 ef 88 a1 88 d8 3b ce 7e 61'.replace(" ", ""),'utf-8'))
        
        # H:
        H = a2b_hex(bytes('df 1a 89 6f 9d 8b c8 16 d9 7c d7 a2 c4 3b ad 54\
        6f be 8c fe'.replace(" ", ""),'utf-8'))
        
        # DB:
        DB = a2b_hex(bytes('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00\
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00\
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00\
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00\
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00\
        00 00 00 00 00 00 01 e3 b5 d5 d0 02 c1 bc e5 0c\
        2b 65 ef 88 a1 88 d8 3b ce 7e 61'.replace(" ", ""),'utf-8'))
        
        # dbMask:
        dbMask = a2b_hex(bytes('66 e4 67 2e 83 6a d1 21 ba 24 4b ed 65 76 b8 67\
        d9 a4 47 c2 8a 6e 66 a5 b8 7d ee 7f bc 7e 65 af\
        50 57 f8 6f ae 89 84 d9 ba 7f 96 9a d6 fe 02 a4\
        d7 5f 74 45 fe fd d8 5b 6d 3a 47 7c 28 d2 4b a1\
        e3 75 6f 79 2d d1 dc e8 ca 94 44 0e cb 52 79 ec\
        d3 18 3a 31 1f c8 97 39 a9 66 43 13 6e 8b 0f 46\
        5e 87 a4 53 5c d4 c5 9b 10 02 8d'.replace(" ", ""),'utf-8'))
        
        # maskedDB:
        maskedDB = a2b_hex(bytes('66 e4 67 2e 83 6a d1 21 ba 24 4b ed 65 76 b8 67\
        d9 a4 47 c2 8a 6e 66 a5 b8 7d ee 7f bc 7e 65 af\
        50 57 f8 6f ae 89 84 d9 ba 7f 96 9a d6 fe 02 a4\
        d7 5f 74 45 fe fd d8 5b 6d 3a 47 7c 28 d2 4b a1\
        e3 75 6f 79 2d d1 dc e8 ca 94 44 0e cb 52 79 ec\
        d3 18 3a 31 1f c8 96 da 1c b3 93 11 af 37 ea 4a\
        75 e2 4b db fd 5c 1d a0 de 7c ec'.replace(" ", ""),'utf-8'))
        
        # Encoded message EM:
        EM = a2b_hex(bytes('66 e4 67 2e 83 6a d1 21 ba 24 4b ed 65 76 b8 67\
        d9 a4 47 c2 8a 6e 66 a5 b8 7d ee 7f bc 7e 65 af\
        50 57 f8 6f ae 89 84 d9 ba 7f 96 9a d6 fe 02 a4\
        d7 5f 74 45 fe fd d8 5b 6d 3a 47 7c 28 d2 4b a1\
        e3 75 6f 79 2d d1 dc e8 ca 94 44 0e cb 52 79 ec\
        d3 18 3a 31 1f c8 96 da 1c b3 93 11 af 37 ea 4a\
        75 e2 4b db fd 5c 1d a0 de 7c ec df 1a 89 6f 9d\
        8b c8 16 d9 7c d7 a2 c4 3b ad 54 6f be 8c fe bc'.replace(" ", ""),'utf-8'))
        
        if debug:
            print("PSS Test Vector:")
            print("M     =>", m)
            print("Mlen  =>", len(m))
            print("mHash =>", mHash)
            print("salt  =>", salt)
            print("M'    =>", mPrime)
            print("H     =>", H)
            print("DB    =>", DB)
            print("dbmask=>", dbMask)
            print("masked=>", maskedDB)
            print("EM    =>", EM)
            print("EMLen =>", len(EM))
        
        pss = PSSPadding()
        realEM = pss.encode(m,len(EM)*8,salt)
        self.assertEqual(EM, realEM)

    
    @classmethod
    def suite(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(Test)
        return suite

class TestPkcs7Padding(unittest.TestCase):
    def setUp(self):
        self.padder = PKCS7Padding()
    def encodecode(self,text):
        _bytes = bytes(text,'utf-8')
        padded = self.padder.encode(_bytes)
        assert _bytes == self.padder.decode(padded), 'o: =>%s\nm: =>%s' % (_bytes,padded)
        assert len(padded) % 16 == 0 , 'invalid padding length: %s' % (len(padded))
        assert len(padded) > 0, 'invalid padding length: %s' % (len(padded))
        assert len(padded) > len(_bytes), 'message must allways have padding'
        
    def testBasic(self):
        self.encodecode("asd")
    def testEmpty(self):
        self.encodecode("")
    def testFull(self):
        self.encodecode("sixteen byte msg")
    def testLarge(self):
        self.encodecode("sixteen byte msg +3")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
