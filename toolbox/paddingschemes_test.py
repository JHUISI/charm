'''
Created on Jun 17, 2011

@author: urbanus
'''
import unittest
import paddingschemes
from binascii import a2b_hex

class Test(unittest.TestCase):

    def testOEAPVector1(self):
        # OAEP Test vector taken from Appendix C 
        #ftp://ftp.rsa.com/pub/rsalabs/rsa_algorithm/rsa-oaep_spec.pdf
        
        # --------------------------------------------------------------------------------
        # Message:
        m     = a2b_hex('d4 36 e9 95 69 fd 32 a7 c8 a0 5b bc 90 d3 2c 49'.replace(' ',''))
        label = ""
        lhash = a2b_hex("da 39 a3 ee 5e 6b 4b 0d 32 55 bf ef 95 60 18 90 af d8 07 09".replace(' ',""))
        DB    = a2b_hex("da 39 a3 ee 5e 6b 4b 0d 32 55 bf ef 95 60 18 90 af d8 07 09 00 00 00 00\
                         00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00\
                         00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00\
                         00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 d4 36 e9 95 69\
                         fd 32 a7 c8 a0 5b bc 90 d3 2c 49".replace(" ", ""))
 
        seed  = a2b_hex("aa fd 12 f6 59 ca e6 34 89 b4 79 e5 07 6d de c2 f0 6c b5 8f".replace(' ' ,''))
        #dbmask = dbMask = MGF (seed , 107):
        dbmask= a2b_hex("06 e1 de b2 36 9a a5 a5 c7 07 d8 2c 8e 4e 93 24 8a c7 83 de e0 b2 c0 46\
                         26 f5 af f9 3e dc fb 25 c9 c2 b3 ff 8a e1 0e 83 9a 2d db 4c dc fe 4f f4\
                         77 28 b4 a1 b7 c1 36 2b aa d2 9a b4 8d 28 69 d5 02 41 21 43 58 11 59 1b\
                         e3 92 f9 82 fb 3e 87 d0 95 ae b4 04 48 db 97 2f 3a c1 4e af f4 9c 8c 3b\
                         7c fc 95 1a 51 ec d1 dd e6 12 64".replace(" ",""))
        #maskedDB
        #seedMask = M GF (maskedDB, 20):
        seedMask = a2b_hex("41 87 0b 5a b0 29 e6 57 d9 57 50 b5 4c 28 3c 08 72 5d be a9".replace(' ',''))
        maskedSeed= a2b_hex("eb 7a 19 ac e9 e3 00 63 50 e3 29 50 4b 45 e2 ca 82 31 0b 26".replace(' ',''))

        #EM = maskedSeed maskedDB
        EM       = a2b_hex("00 eb 7a 19 ac e9 e3 00 63 50 e3 29 50 4b 45 e2 ca 82 31 0b 26 dc d8 7d 5c\
                            68 f1 ee a8 f5 52 67 c3 1b 2e 8b b4 25 1f 84 d7 e0 b2 c0 46 26 f5 af f9\
                            3e dc fb 25 c9 c2 b3 ff 8a e1 0e 83 9a 2d db 4c dc fe 4f f4 77 28 b4 a1\
                            b7 c1 36 2b aa d2 9a b4 8d 28 69 d5 02 41 21 43 58 11 59 1b e3 92 f9 82\
                            fb 3e 87 d0 95 ae b4 04 48 db 97 2f 3a c1 4f 7b c2 75 19 52 81 ce 32 d2\
                            f1 b7 6d 4d 35 3e 2d".replace(" ",'')) 

        if(False):
            print("Test Vector 1:")
            print("mesg  =>", m)
            print("label =>", label)
            print("lhash =>", lhash)    #Correct
            print("DB    =>", DB)       #Correct
            print("DBMask=>", dbmask)   #Correct
            print("seedMask=>", seedMask)   #Correct
            print("maskedseed=>", maskedSeed)

        c = paddingschemes.OAEPEncryptionPadding()
        E = c.encode(m, 128,"",seed)
        self.assertEqual(EM, E)
    
    def testRoundTripEquiv(self):
        oaep = paddingschemes.OAEPEncryptionPadding()
        m = b'This is a test message'
        ct = oaep.encode(m, 64)
        pt = oaep.decode(ct)
        self.assertEqual(m, pt, 'Decoded message is not equal to encoded message\n'\
                         'ct: %s\nm:  %s\npt: %s' % (ct, m, pt))
        
    def testMFG(self):
        seed = ""
        hashFn = paddingschemes.OAEPEncryptionPadding().hashFn
        hLen =  paddingschemes.OAEPEncryptionPadding().hashFnOutputBytes
        
        for mbytes in range(100):
            a = paddingschemes.MGF1(seed, mbytes, hashFn, hLen)
            self.assertEqual(len(a), mbytes, 'MFG output wrong size')

    def testMFGvector(self):
        hashFn = paddingschemes.OAEPEncryptionPadding().hashFn
        hLen =  paddingschemes.OAEPEncryptionPadding().hashFnOutputBytes
        seed  = a2b_hex("aa fd 12 f6 59 ca e6 34 89 b4 79 e5 07 6d de c2 f0 6c b5 8f".replace(' ' ,''))
        #dbmask = dbMask = MGF (seed , 107):
        dbmask= a2b_hex("06 e1 de b2 36 9a a5 a5 c7 07 d8 2c 8e 4e 93 24 8a c7 83 de e0 b2 c0 46\
                         26 f5 af f9 3e dc fb 25 c9 c2 b3 ff 8a e1 0e 83 9a 2d db 4c dc fe 4f f4\
                         77 28 b4 a1 b7 c1 36 2b aa d2 9a b4 8d 28 69 d5 02 41 21 43 58 11 59 1b\
                         e3 92 f9 82 fb 3e 87 d0 95 ae b4 04 48 db 97 2f 3a c1 4e af f4 9c 8c 3b\
                         7c fc 95 1a 51 ec d1 dd e6 12 64".replace(" ",""))
        a = paddingschemes.MGF1(seed, 107, hashFn, hLen)
        self.assertEqual(dbmask, a)
        
    def testSHA1Vector(self):
        hashFn = paddingschemes.hashFunc('sha1')
        V0 = (b"", a2b_hex("da39a3ee5e6b4b0d3255bfef95601890afd80709"))
        V1 = (bytes("The quick brown fox jumps over the lazy dog", 'utf-8'), a2b_hex("2fd4e1c67a2d28fced849ee1bb76e7391b93eb12")) #ASCII encoding
        V2 = (b'The quick brown fox jumps over the lazy dog', a2b_hex("2fd4e1c67a2d28fced849ee1bb76e7391b93eb12")) #binary data
        #print("str => ", V2[0])
        #print("H(s)=> ", hashFn(V2[0]))
        #print("stnd=> ", V2[1])
        
        self.assertEqual(hashFn(V0[0]), V0[1], 'empty string')
        self.assertEqual(hashFn(V1[0]), V1[1], 'quick fox')
        self.assertEqual(hashFn(V2[0]), V2[1])
        
    
    @classmethod
    def suite(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(Test)
        return suite

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()