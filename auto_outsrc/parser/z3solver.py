from __future__ import print_function
from z3 import *

"""
format of config file:

variables = [ 'x', 'y', 'z' ]

clauses = [ ('x', 'y'), ('y', 'z'), ('x', 'z') ]
...etc
"""
variableKeyword = "variables"
clauseKeyword = "clauses"
unSat = "unsat"
def read_config(filename):
    print("Importing file: ", filename)
    file = filename.split('.')[0]

    fileVars = __import__(file)
    definitions = dir(fileVars)
    if variableKeyword in definitions and clauseKeyword in definitions:
        return (fileVars.variables, fileVars.clauses)
    else:
        sys.exit("File doesn't contain definitions for '%s' and/or '%s'" % (variableKeyword, clauseKeyword))
        

def solveBooleanCircuit(file, variables, clauses):
    vars = {}
    for v in variables:
        vars[ str(v) ] = Bool(str(v)) # create refs
    
    mySolver = Solver()
    for i in clauses:
        (x, y) = i
        if vars.get(x) and vars.get(y):
            mySolver.add(Xor(vars.get(x), vars.get(y)))
        elif vars.get(x) == None:
            print("Need to add '%s' to variable list." % x)
            return
        elif vars.get(y) == None:
            print("Need to add '%s' to variable list." % y)
            return
    
    isSat = mySolver.check()
    if str(isSat) == unSat: sys.exit("Clauses are not satisfiable. Try again!")
    m = mySolver.model()
    print(m)
    results = {}
    output = "resultDictionary = ["
    for i in range(len(variables)):
        key = m[i]
        #print(key, ':', m[key])
        output += "('" + str(key) + "' , " + str(m[key]) + "), "
        results[ str(key) ] = m[key]
    output += "]"
    f = open(file, 'a')
    f.write(output)
    f.close()
    return results


if __name__ == "__main__":
    print(sys.argv[1:])
    file = sys.argv[1]
#    variables = [ 'x', 'y', 'z' ]
#    clauses = [ ('x', 'y'), ('y', 'x'), ('y', 'z') ]
    variables, clauses = read_config(file)
    solveBooleanCircuit(file, variables, clauses)


 
    