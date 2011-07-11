'''
Iterates through all the charm-crypto schemes, and runs them to see if they work

@author: Gary Belvin
'''
import os, re
import unittest
import all_unittests

def testSchemes(modules=None):
    '''
    Searches the given modules for methods named 'main'
    returns a test suite with one test for each main method
    If modules==None, all modules are searched
    '''
    
    suite = unittest.TestSuite()
    testing, skipped = [],[]
    
    if modules==None:
        #Exclude unit tests
        modules = [mod for mod in all_unittests.find_modules() if not re.match(".*_test$", mod)]
    
    for name in modules:
        mod = all_unittests.load_module(name)
        if hasattr(mod, 'main'):
            testing.append(mod.__name__)
            case = unittest.FunctionTestCase(mod.main, None, None, mod.__name__)
            suite.addTest(case)
        else:
            skipped.append(mod.__name__)
            
    #print("Testing  ", testing)
    print("Skipping ", skipped)
    return suite

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    if os.access("schemes/", os.R_OK):
        os.chdir('schemes/')
    elif os.access("../schemes/", os.R_OK):
        os.chdir('../schemes/')
        
    
    modules = None 
    #Uncomment to restrict the tests to these modules
    # ECC and Pairing 
    #modules = ['ibe_bf03','abemultiauth_hybrid', 'sig_short_bls04', 'kpabe', 'cpabe07', 'cpabe09', 'ecdsa', 'elgamal', 'ibe_bb03', 'hashIDAdapt', 'hybridenc', 'hybridibenc', 'dabe_aw11', 'commit_92', 'chk04_enc', 'sig_generic_ibetosig_naor01', 'ibe_n05']
     
    TesterInstance = unittest.TextTestRunner(verbosity=3)
    TesterInstance.run(testSchemes(modules))#Run tests
