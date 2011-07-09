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

def my_tearDown():
    print("clean what...")

#Temp method to figure out what's causing the segmentation faults.
#Current theory: any more than one test in a test suite causes the segmentation fault due to calls to PairingGroup()
def testSchemes():
    suite = unittest.TestSuite()
    # ECC and Pairing 
    modules = ['abemultiauth_hybrid', 'sig_short_bls04', 'kpabe', 'cpabe07', 'cpabe09', 'ecdsa', 'elgamal', 'ibe_bb03', 'hashIDAdapt', 'hybridenc', 'hybridibenc', 'dabe_aw11', 'commit_92', 'chk04_enc', 'sig_generic_ibetosig_naor01', 'ibe_n05']
    #,'cpabe09','cpabe07','schnorr_sig_08','commit_92','ec_cs98_enc','abemultiauth_hybrid','ecdsa','dsa','elgamal','sig_generic_ibetosig_naor01','hashIDAdapt','hybridenc','paillier','ibe_aw11','cs98_enc','rsa_alg','kpabe','hybridibenc','ibe_bb03','chk04_enc']
    testing, skipped = [],['ibe_bf03']
    for name in modules:
        mod = all_unittests.load_module(name)
        if hasattr(mod, 'main'):
            testing.append(mod.__name__)
            case = unittest.FunctionTestCase(mod.main, None, my_tearDown, mod.__name__)
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
    #unittest.TextTestRunner(verbosity=1).run(getAllSchemes())
    TesterInstance = unittest.TextTestRunner(verbosity=3)
    #TesterInstance.run(getAllSchemes())
    TesterInstance.run(testSchemes())
