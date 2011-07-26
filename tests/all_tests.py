'''
Runs all known tests on charm-crypto

:Authors: Gary Belvin
:Date: Jul 26, 2011
'''
import unittest, os, sys
from all_unittests import getAllTestsSuite
from all_schemes import testSchemes, modules

if __name__ == '__main__':
    if os.access("schemes/", os.R_OK):
        os.chdir('schemes/')
    elif os.access("../schemes/", os.R_OK):
        os.chdir('../schemes/')
        
    paths = ['../toolbox/', '.']
    for p in paths:
        if p not in sys.path:
            sys.path.append(os.path.abspath(p))
        
    print (sys.path)
    
    suite = unittest.TestSuite()
    suite.addTests(getAllTestsSuite(paths))
    suite.addTests(testSchemes(modules))
    
    unittest.TextTestRunner(verbosity=12).run(suite)
    