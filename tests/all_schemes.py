'''
Iterates through all the charm-crypto schemes, and runs them to see if they work

@author: Gary Belvin
'''
import os
import unittest
import all_unittests

#find ./schemes/ -name '*.py' -execdir python3 '{}' \;

def getAllSchemes():
    suite = unittest.TestSuite()
    modules = all_unittests.find_modules()
    testing, skipped = [],[]
    for name in modules:
        mod = all_unittests.load_module(name)
        if hasattr(mod, 'main'):
            testing.append(mod.__name__)
            case = unittest.FunctionTestCase(mod.main, None, None, mod.__name__)
            suite.addTest(case)
        else:
            skipped.append(mod.__name__)
            
    print("Testing  ", testing)
    print("Skipping ", skipped)
    return suite

#Temp method to figure out what's causing the segmentation faults.
#Current theory: any more than one test in a test suite causes the segmentation fault due to calls to PairingGroup()
def testSchemes():
    suite = unittest.TestSuite()
    modules = ['abemultiauth_hybrid', 'ibe_bf03','sig_short_bls04']
    #,'cpabe09','cpabe07','schnorr_sig_08','commit_92','ec_cs98_enc','abemultiauth_hybrid','ecdsa','dsa','elgamal','sig_generic_ibetosig_naor01','hashIDAdapt','hybridenc','paillier','ibe_aw11','cs98_enc','rsa_alg','kpabe','hybridibenc','ibe_bb03','chk04_enc']
    testing, skipped = [],[]
    for name in modules:
        mod = all_unittests.load_module(name)
        if hasattr(mod, 'main'):
            testing.append(mod.__name__)
            case = unittest.FunctionTestCase(mod.main, None, None, mod.__name__)
            suite.addTest(case)
        else:
            skipped.append(mod.__name__)
            
    print("Testing  ", testing)
    print("Skipping ", skipped)
    return suite

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    if os.access("schemes/", os.R_OK):
        os.chdir('schemes/')
    elif os.access("../schemes/", os.R_OK):
        os.chdir('../schemes/')
    #Run all tests 
    unittest.TextTestRunner(verbosity=1).run(getAllSchemes())
    #unittest.TextTestRunner(verbosity=3).run(testSchemes())
