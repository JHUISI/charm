'''
This script searches for python modules named *_test, and runs all the unit tests it finds
Created on Jun 22, 2011
@author: Gary Belvin
'''
import unittest
import os, imp, re, sys, inspect

#A list of all the directories to search
unittestpaths1 = ['toolbox/', 'schemes/']
unittestpaths2 = ['../toolbox/', '../schemes/']

if os.access("schemes/", os.R_OK):
    unittestpaths = unittestpaths1
elif os.access("../schemes/", os.R_OK):
    unittestpaths = unittestpaths2

def adjustPYPATH(paths):
    for p in paths:
        if p not in sys.path:
            sys.path.append(p)

def find_modules(path="."):
    modules = set()
    for filename in os.listdir(path):
        if re.match(".*py$", filename):
            module = filename[:-3]
            modules.add(module)
    return modules

def load_module(name, path=["."]):
    """Return a named module found in a given path."""
    (file, pathname, description) = imp.find_module(name, path)
    return imp.load_module(name, file, pathname, description)
    
def collectSubClasses(baseclass, mod_list, path=['.']):
    '''Given a set of modules, returns only those classes that inherit from baseclass'''    
    for name in mod_list:
        (file, pathname, description) = imp.find_module(name, path)
        mod = imp.load_module(name, file, pathname, description)
        for name, obj in inspect.getmembers(mod):
            if inspect.isclass(obj) and issubclass(obj, baseclass)\
            and obj != baseclass:
                yield obj

def getAllTestsSuite():
    #Collect test cases
    suite = unittest.TestSuite()
    for path in unittestpaths:
        testmodules = [mod for mod in find_modules(path) if re.match(".*_test$", mod)]
        for name in testmodules:
            m = load_module(name, unittestpaths)
            print("Loading .. %s" % m.__file__)
            suite_n = unittest.TestLoader().loadTestsFromModule(m)
            suite.addTests(suite_n)
    return suite

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    adjustPYPATH(unittestpaths)
    
    #Run all tests 
    unittest.TextTestRunner(verbosity=2).run(getAllTestsSuite())
