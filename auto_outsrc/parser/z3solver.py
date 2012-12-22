from __future__ import print_function
from z3 import *
from itertools import combinations

"""
format of config file:

# default input style
variables = [ 'x', 'y', 'z' ]
clauses = [ ('x', 'y'), ('y', 'z'), ('x', 'z') ]
constraints = ['x']
mofn = ['y', 'z']

OR
# alternative input
sk = ['x', 'y']
ct = ['z']
constraints = [sk , ct] # if each index is a list instead of string
search = True # mode that forces the solver to come up w/ a bunch of solutions...

# format of results...
satisfiable = True or False
resultDictionary = [('x', True), ('y', False), ... ]
"""
variableKeyword = "variables"
clauseKeyword = "clauses"
constraintKeyword = "constraints"
mofnKeyword = "mofn"
searchKeyword = "search"
unSat = "unsat"
satisfiableKeyword = "satisfiable"

def read_config(filename):
    print("Importing file: ", filename)
    file = filename.split('.')[0]

    fileVars = __import__(file)
    fileKeys = dir(fileVars)
    return readConfig(fileVars, fileKeys)
#    if variableKeyword in definitions and clauseKeyword in definitions and constraintKeyword in definitions:
#        return (definitions, fileVars.variables, fileVars.clauses, fileVars.constraints)
#    else:
#        sys.exit("File doesn't contain definitions for '%s' and/or '%s'" % (variableKeyword, clauseKeyword))
    

def readConfig(fileVars, fileKeys):
    results = {variableKeyword:[], clauseKeyword:[], constraintKeyword:[], 
               mofnKeyword: [], searchKeyword:None } 
    if variableKeyword in fileKeys:
        results[ variableKeyword ] = getattr(fileVars, variableKeyword)
    if clauseKeyword in fileKeys:
        results[ clauseKeyword ] = getattr(fileVars, clauseKeyword)
    if constraintKeyword in fileKeys:
        results[ constraintKeyword ] = getattr(fileVars, constraintKeyword)
    if mofnKeyword in fileKeys:
        results[ mofnKeyword ] = getattr(fileVars, mofnKeyword) 
    if searchKeyword in fileKeys:
        results[ searchKeyword ] = getattr(fileVars, searchKeyword)
    return results

def getConstraint(vars, mofn, mCount):
    print("mCount :", mCount)
    if mCount == 1:
        return Or([ vars.get(i) for i in mofn ])
    else:
        s = ""
        for i in mofn:
            s += str(i)
        
        cases = list(combinations(s, mCount))
        for c in cases:
            orObjects.append(And([ vars.get(i) for i in mofn ]))
        return Or(orObjects)

def search(vars, solver, mofn, m):
    print("solver before search: ", solver)
    mCount = m
    mofnCon = [ vars.get(i) for i in mofn ]
    while mCount != 0:
        if mCount == len(mofn): # first time call, so no pop
            print(mofn)
            solver.add(And(mofnCon))
        else:
            solver.pop()
            solver.add(getConstraint(vars, mofn, mCount))
            # add (m-1)-of-n to solver and re-check
        #print("solver after update: ", solver)
        #print(solver.check())
        if solver.check() == unsat: mCount -= 1
        else: break # solution was satisfiable, search is complete
    return mCount

def solveBooleanCircuit(filename, optionDict): # variables, clauses, constraints):
    variables   = optionDict.get(variableKeyword)
    clauses     = optionDict.get(clauseKeyword)
    constraints = optionDict.get(constraintKeyword)
    mofn        = optionDict.get(mofnKeyword)
    vars = {}
    for v in variables:
        vars[ str(v) ] = Bool(str(v)) # create Bool refs
    
    mySolver = Solver()
    for i in clauses:
        (x, y) = i
        if vars.get(x) and vars.get(y):
            mySolver.add(Xor(vars.get(x), vars.get(y)))
            mySolver.push()
        elif vars.get(x) == None:
            print("Need to add '%s' to variable list." % x)
            return
        elif vars.get(y) == None:
            print("Need to add '%s' to variable list." % y)
            return
    
    andObjects = []
    for i in constraints:
        if vars.get(i) != None:
            andObjects.append(vars.get(i))
        
    if len(andObjects) > 0:
        mySolver.add(And(andObjects))
        mySolver.push()
    
    # flex constraints: extract the m-of-n variables
    # then perform search to determine largest m out of n that 
    m = len(mofn)
    if m > 0:
        countOutofN = search(vars, mySolver, mofn, m) # returns a number that says how far it got
        print("list: ", mofn)
        print("Result: %d of %d" % (countOutofN, m))
        print("Result constraints: ", mySolver)
    
    f = open(filename, 'a')
    isSat = mySolver.check()
    if str(isSat) == unSat:
        f.write(satisfiableKeyword + " = False\n")
        f.close()
        sys.exit("Clauses are not satisfiable.") 
    else:
        f.write(satisfiableKeyword + " = True\n")
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
    f.write(output)
    f.close()
    return results


if __name__ == "__main__":
    print(sys.argv[1:])
    filename = sys.argv[1]
#    variables = [ 'x', 'y', 'z' ]
#    clauses = [ ('x', 'y'), ('y', 'x'), ('y', 'z') ]
    optionDict = read_config(filename)
    solveBooleanCircuit(filename, optionDict)


 
    