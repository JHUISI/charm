'''
This script searches for python modules named *_test, and runs all the unit tests it finds
Created on Jun 22, 2011
@author: Gary Belvin
'''
import unittest
import os, imp, re, sys

#A list of all the directories to search
unittestpaths = ['toolbox/', 'schemes/']
for p in unittestpaths:
	sys.path.append(p)

def find_modules(path="."):
    """Return names of modules in a directory.
    http://wiki.python.org/moin/ModulesAsPlugins
    Returns module names in a list. Filenames that end in ".py" or
    ".pyc" are considered to be modules. The extension is not included
    in the returned list.
    """
    modules = set()
    for filename in os.listdir(path):
        module = None
        if filename.endswith(".py"):
            module = filename[:-3]
        elif filename.endswith(".pyc"):
            module = filename[:-4]
        if module is not None:
            modules.add(module)
    return list(modules)


def load_module(name, path=["."]):
    """Return a named module found in a given path."""
    (file, pathname, description) = imp.find_module(name, path)
    return imp.load_module(name, file, pathname, description)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    suite = unittest.TestSuite()
    
    #Collect test cases
    for path in unittestpaths:
        testmodules = [mod for mod in find_modules(path) if re.match(".*_test$", mod)]
        for name in testmodules:
            m = load_module(name, unittestpaths)
            print("Loading .. %s" % m.__file__)
            suite_n = unittest.TestLoader().loadTestsFromModule(m)
            suite.addTests(suite_n)
    
    #Run all tests 
    unittest.TextTestRunner(verbosity=2).run(suite)
