'''
Created on Jun 17, 2011

@author: urbanus
'''
import unittest


class Test(unittest.TestCase):


    def testOEAPVector1(self):
        # RSA-OAEP encryption of 6 random messages with random seeds
        # -----------------------------------------------------------
        
        # OAEP Example 1.1
        # ------------------
        
        # Message:
        m = int('6628194e12073db03ba94cda9ef9532397d50dba79b987004afefe34', 16) 

        # Seed:
        s = int ('18 b7 76 ea 21 06 9d 69 77 6a 33 e9 6b ad 48 e1 dd a0 a5 ef'.replace(' ',''),16) 
        
        # Encryption:
        e = int("35 4f e6 7b 4a 12 6d 5d 35 fe 36 c7 77 79 1a 3f\
        7b a1 3d ef 48 4e 2d 39 08 af f7 22 fa d4 68 fb\
        21 69 6d e9 5d 0b e9 11 c2 d3 17 4f 8a fc c2 01\
        03 5f 7b 6d 8e 69 40 2d e5 45 16 18 c2 1a 53 5f\
        a9 d7 bf c5 b8 dd 9f c2 43 f8 cf 92 7d b3 13 22\
        d6 e8 81 ea a9 1a 99 61 70 e6 57 a0 5a 26 64 26\
        d9 8c 88 00 3f 84 77 c1 22 70 94 a0 d9 fa 1e 8c\
        40 24 30 9c e1 ec cc b5 21 00 35 d4 7a c7 2e 8a".replace(' ', ''),16) 

        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()