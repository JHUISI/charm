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
searchBoth = True # mode that forces the solver to come up w/ a bunch of solutions...

# format of results...
satisfiable = True or False
resultDictionary = [('x', True), ('y', False), ... ]
"""
verboseKeyword = "verbose"
variableKeyword = "variables"
clauseKeyword = "clauses"
constraintKeyword = "constraints"
mofnKeyword = "mofn"
searchKeyword = "searchBoth"
unSat = "unsat"
satisfiableKeyword = "satisfiable"

def readConfig(filename):
    print("Importing file: ", filename)
    file = filename.split('.')[0]

    fileVars = __import__(file)
    fileKeys = dir(fileVars)
    return _readConfig(fileVars, fileKeys)

def _readConfig(fileVars, fileKeys):
    results = {variableKeyword:[], clauseKeyword:[], constraintKeyword:[], 
               mofnKeyword: [], searchKeyword:False, verboseKeyword:None } 
    if variableKeyword in fileKeys:
        results[ variableKeyword ] = getattr(fileVars, variableKeyword)
    if clauseKeyword in fileKeys:
        results[ clauseKeyword ] = getattr(fileVars, clauseKeyword)
    if constraintKeyword in fileKeys:
        results[ constraintKeyword ] = getattr(fileVars, constraintKeyword)
        for i in results[ constraintKeyword ]:
            if hasattr(fileVars, i):
                results[ i ] = getattr(fileVars, i)
    if mofnKeyword in fileKeys:
        results[ mofnKeyword ] = getattr(fileVars, mofnKeyword) 
    if searchKeyword in fileKeys:
        results[ searchKeyword ] = getattr(fileVars, searchKeyword)
    if verboseKeyword in fileKeys:
        results[ verboseKeyword ] = getattr(fileVars, verboseKeyword)
    return results

def getConstraint(vars, mofn, mCount, verbose=False):
    if verbose: print("mCount :", mCount)
    if mCount == 1:
        return Or([ vars.get(i) for i in mofn ])
    else:
        s = ""
        for i in mofn:
            s += str(i)
        # compute all combination of the variables in s
        # each case ==> AND(case1) OR AND(case2) OR AND(case3) OR ...etc...
        cases = list(combinations(s, mCount))
        orObjects = []
        for c in cases:
            orObjects.append(And([ vars.get(i) for i in c ]))
        return Or(orObjects)

def search(vars, solver, mofn, m, verbose=False):
    if verbose: print("solver before search: ", solver)
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

def searchBoth(vars, solver, key1name, key1, key2name, key2, origConstraints, verbose=False):
    if verbose: print("solver before search: ", solver)
    satisfiable = False

    if len(origConstraints) > 0:    
        solver.add(origConstraints)

    count1 = len(key1)-1
    count2 = len(key2)-1
    solver2 = None
    fixCount1 = False
    fixCount2 = False    
    while not satisfiable:
        solver2 = Solver()
        solver2.add(solver.assertions()) # revert back to solver
        solver2.add(getConstraint(vars, key1, count1), getConstraint(vars, key2, count2))
        #print("solver after update: ", solver2)
        if verbose: print("check: ", solver2.check())
        if solver2.check() == unsat: 
            if not fixCount1: count1 -= 1
            if not fixCount2: count2 -= 1
        else:
            satisfiable = True
            continue
        if count1 == 0 or count2 == 0: 
            # switch strategy... how?
            print("%s: %d of %d" % (key1name, count1, len(key1)))
            print("%s: %d of %d" % (key2name, count2, len(key2)))
            print("Could not find the largest m-of-n for either category.")
            # JAA: this didn't work for this scheme. perhaps, we may need to utilize the option to favor one set over the other?
            return solver

    if verbose:    
        print("final solution: ", solver2)
        print("satisfiable: ", solver2.check())
    print("%s: %d of %d" % (key1name, count1, len(key1)))
    print("%s: %d of %d" % (key2name, count2, len(key2)))
    return solver2

def solveBooleanCircuit(filename, optionDict): # variables, clauses, constraints):
    verbose     = optionDict.get(verboseKeyword)
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
        
    # if searchKeyword disabled
    if not optionDict.get(searchKeyword):
        andObjects = []
        for i in constraints:
            # default case where each i is a string variable
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
    else:
        print("search for both...")
        count = 0
        constraintLists = {}
        _origConstraints = []
        for i in constraints:
            if optionDict.get(i):
                constraintLists[ count ] = (i, optionDict.get(i)); count += 1
                print(i, ":", optionDict.get(i))
            elif vars.get(i) != None: # ground truth that we can't change
                _origConstraints.append(i)
        
        assert len(constraintLists) == 2, "With this option, can only have (keys and (ciphertext or signatures))"
        key1 = list(set(constraintLists[0][1]).difference(_origConstraints))
        key1name = str(constraintLists[0][0])
        key2 = list(set(constraintLists[1][1]).difference(_origConstraints))
        key2name = str(constraintLists[1][0])

        origConstraints = [ vars.get(i) for i in _origConstraints ]
        
        mySolver = searchBoth(vars, mySolver, key1name, key1, key2name, key2, origConstraints, verbose=True)
#        sys.exit(0)
    
    f = open(filename, 'a')
    isSat = mySolver.check()
    if str(isSat) == unSat:
        f.write(satisfiableKeyword + " = False\n")
        f.close()
        sys.exit("Clauses are not satisfiable.") 
    else:
        f.write(satisfiableKeyword + " = True\n")
    model = mySolver.model()
    print(model)
    results = {}
    output = "resultDictionary = ["
    for index in range(len(variables)):
        key = model[index]
        print(key, ':', model[key])
        output += "('" + str(key) + "' , " + str(model[key]) + "), "
        results[ str(key) ] = model[key]
    output += "]"
    f.write(output)
    f.close()
    return results


if __name__ == "__main__":
    print(sys.argv[1:])
    filename = sys.argv[1]
    optionDict = readConfig(filename)
    solveBooleanCircuit(filename, optionDict)


 
    