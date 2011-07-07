'''
Created on Jul 1, 2011

@author: urbanus
'''
from schemes.rsa_alg import RSA_Enc, RSA_Sig
import unittest


class Test(unittest.TestCase):


    def testRSAEnc(self):
        rsa = RSA_Enc()
    
        (pk, sk) = rsa.keygen(1024)
        
        #m = integer(34567890981234556498) % pk['N']
        m = b'This is a test'
        c = rsa.encrypt(pk, m)
        
        orig_m = rsa.decrypt(pk, sk, c)
    
        assert m == orig_m
        
    def testRSASig(self):
        rsa = RSA_Sig()
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()