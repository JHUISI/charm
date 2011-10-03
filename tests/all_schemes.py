'''
Iterates through all the charm-crypto schemes, and runs them to see if they work

:authors: Gary Belvin
'''
import os, re
import unittest
import all_unittests

modules = None 
# Uncomment to restrict the tests to these modules
# ECC and Pairing 
# Restrict modules to these schemes (which actually work) until further notice.
#modules = ['ibenc_bf03', 'abemultiauth_hybrid', 'sig_short_bls04', 'kpabe', 'cpabe07', 'cpabe09', 'ecdsa', 'elgamal', 'ibe_bb03',
 #           'hashIDAdapt', 'hybridenc', 'hybridibenc', 'dabe_aw11', 'commit_92', 'chk04_enc', 'sig_generic_ibetosig_naor01', 'ibe_n05']
skip = ['pksig_rsa_hw09', 'pksig_dsa', 'ake_ecmqv']

def testSchemes(modules=None, skip=None):
    '''
    Searches the given modules for methods named 'main'
    returns a test suite with one test for each main method
    If modules==None, all modules are searched
    '''
    
    suite = unittest.TestSuite()
    
    if modules==None:
        #Exclude unit tests
        modules = [mod for mod in all_unittests.find_modules() if not re.match(".*_test$", mod)]
        
    if skip==None:
        skip = []
    else:
        modules = list(set(modules).difference(set(skip)))
        modules.sort() 
    
    for name in modules:
        mod = all_unittests.load_module(name)
        if hasattr(mod, 'main'):
            try:
               case = unittest.FunctionTestCase(mod.main, None, None, mod.__name__)
               suite.addTest(case)
            except Exception as e:
               print("Stack Trace =>", e)
        else:
            skip.append(mod.__name__)
            
    #print("Testing  ", modules)
    #print("Skipping ", skip)
    return suite

if __name__ == "__main__":
    if os.access("schemes/", os.R_OK):
        os.chdir('schemes/')
    elif os.access("../schemes/", os.R_OK):
        os.chdir('../schemes/')

    TesterInstance = unittest.TextTestRunner(verbosity=3)
    TesterInstance.run(testSchemes(modules, skip)) #Run tests
