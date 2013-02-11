from __future__ import print_function
from z3 import *
import string

# input for our BF solver
#bfCount = 5
#mskVars = ['alpha', 't1', 't2', 't3', 't4']
#rndVars = ['r1', 'r2']
#
## 4 : alpha * t2 + r1 * t2
##d4 = {'MUL0':['alpha', 't2'], 'MUL1':['r1', 't2'], 'ADD0': ['MUL0', 'MUL1'], 'root':'ADD0' }
## 5 : r1 * t1 * t2 + r2 * t3 * t4 => 
##d5 = {'MUL0': [ 'r1', 't1', 't2' ],  'MUL1': [ 'r2', 't3', 't4' ], 'ADD0': ['MUL0', 'MUL1'], 'root':'ADD0' }
#
##keywords: info, skVars, rndVars, mskVars and bfCount
#info = {'d3': {'root': ['ADD0'], 'ADD0': ['t4', '-r2', 'hID#y']}, 'sk': {}, 'd4': {'root': ['ADD0'], 'ADD0': ['t3', '-r2', 'hID#y']}, 'd2': {'root': ['ADD0'], 'ADD0': ['t1', '-alpha', 't1', '-r1', 'hID#y']}, 'id': {}, 'd0': {'ADD0': ['MUL0', 'MUL2'], 'MUL2': ['r2', 'MUL3'], 'MUL3': ['t3', 't4'], 'MUL0': ['r1', 'MUL1'], 'MUL1': ['t1', 't2'], 'root': ['ADD0']}, 'd1': {'root': ['ADD0'], 'ADD0': ['t2', '-alpha', 't2', '-r1', 'hID#y']}}
#skVars = ['d0', 'd1', 'd2', 'd3', 'd4']

bfCount = 2
mskVars = ['alpha']
rndVars = ['t', 'beta'] # try to capture ordering of instances of random vars.

info = {'sk': ['K', 'L', 'Kl'], 'K': {'root': ['MUL0'], 'ADD0':['alpha', 'beta'], 'MUL0':['ADD0','t']}, 'L': {'root':['LEAF0'], 'LEAF0':['t']}, 'Kl': {'root':['LEAF0'], 'LEAF0':['t']}}

#rndVars = ['t', 'beta', 's'] # try to capture ordering of instances of random vars.
#info = {'sk': ['K', 'L', 'Kl'], 'K': {'root': ['ADD0'], 'ADD0': ['MUL0','MUL1'], 'MUL0':['alpha', 'beta'], 'MUL1':['s', 't']}, 'L': {'root':['LEAF0'], 'LEAF0':['t']}, 'Kl': {'root':['LEAF0'], 'LEAF0':['t']}}

#rndVars = ['t', 'beta']
#info = {'sk': ['K', 'L', 'Kl'], 'K': {'root': ['ADD0'], 'ADD0': ['t','MUL0'], 'MUL0':['alpha', 'beta']}, 'L': {'root':['LEAF0'], 'LEAF0':['t']}, 'Kl': {'root':['LEAF0'], 'LEAF0':['t']}}
#info = {'sk': ['K', 'L', 'Kl'], 'K': {'root': ['ADD0'], 'ADD0': ['alpha','t']}, 'L': {'root':['LEAF0'], 'LEAF0':['t']}, 'Kl': {'root':['LEAF0'], 'LEAF0':['t']}}
skVars = 'sk'

######################################################################################
root = 'root'
ADD,MUL,LEAF='ADD','MUL','LEAF'
nil = None

def clean(v):
    removeSymbols = ['-', '#', '?']
    for i in removeSymbols:
        if v.find(i) != -1:
            v.strip(i)
    return v


class SetupBFSolver:
    def __init__(self):
        self.factorsList = None
        self.theVarMap = None
        self.varList = None
        self.mskList = None
        self.nonNilList = None
        
    def construct(self, mskVars, rndVars):
        # Standard code below
        keygenVars = mskVars + rndVars
        alphabet = string.ascii_lowercase
        factors = []
        
        for i in range(bfCount):
            factors.append(alphabet[i])
        factors.append('nil') # no blinding factor
        print("selected factors :", factors)
        
        # blinding factors
        Factors, self.factorsList = EnumSort('Factors', factors)
        print("factorList :", self.factorsList)
        self.nil = nil = self.factorsList[-1]
        
        # target variables
        self.theVarMap = {}
        self.varList = []
        self.mskList = []
        self.nonNilList = []
        self.rndList = []
        for i in keygenVars:
            i = clean(i)
            j = Const(i, Factors)
            self.varList.append( j )
            self.theVarMap[ i ] = j
            if i in mskVars:
               self.mskList.append( j )
               self.nonNilList.append( j != nil )
            else:
               self.rndList.append( j )
        
        # extract all possible mappings for mskList
        orObjs = []
        for i in self.mskList:
            varMap = []
            for j in self.factorsList:
                if str(j) != str(nil):
                   varMap.append( i == j )
            orObjs.append( Or(varMap) )
    
        andObjVarMap = And(orObjs)
    
        s = Solver()
        s.set(unsat_core=True)
        # add vars for possible blinding factor mappings for msk
        s.add(andObjVarMap)
        # R1. msk must be unique
        s.add( Distinct(self.mskList) )
        # R2. none of the msk variables can be mapped to nil or no blinding factors
        s.add( And(self.nonNilList) )
        
        return s
######################################################################################

class ConstructRule:
    def __init__(self, theVarMap, nil):
        self.varMap = theVarMap
        self.varMapKeys = list(self.varMap.keys())
        self.nil = nil
    
    def baseCase(self, dataList):
        """ returns True iff all elements in the list are in varMap which means they are attributes"""
        for i in dataList:
            if type(i) == list:
                for j in i:
                    if j not in self.varMapKeys:
                        return False
            else:
                if i not in self.varMapKeys:
                    return False
        return True
    
    def getFirstNonAttr(self, data):
        assert type(data) == list, "invalid type to getFirstNonAttr"
        newData = []
        attrList = []
        for i in data:
            if ADD in i or MUL in i:
                newData.append(i)
            elif i in self.varMapKeys:
                attrList.append(i)
        return newData, attrList
    
    def rule(self, ruleType, data, retList=False, excludeList=[]):
        finalConstraints = []
        for i in ruleType:
            if ADD in i:
                if self.baseCase(data[i]):
                    finalConstraints += self.__addRule(data[i], excludeList)
                else:
                    newRuleList, attrList = self.getFirstNonAttr(data[i])
                    print("newDataList=", newRuleList)
                    print("attrList=", attrList)
                    if len(attrList) > 0:
                        res = self.rule(newRuleList, data, True, excludeList)
#                        print("RESULT0: ", res[0])
#                        print("RESULT1: ", res[1] + attrList)
                        data[ i ] = res[1] + attrList # updating current ADD* key/value
                        excludeList += list(res[1])
                        res2 = self.rule([ i ], data, excludeList)
#                        print("RESULT2: ", res[0], res2[0])
                        finalConstraints += res[0] + res2[0]
                    else:
                        finalConstraints += self.rule(newRuleList, data, retList, excludeList)
            elif MUL in i:
                if self.baseCase(data[i]):
                    finalConstraints += self.__mulRule(data[i], excludeList)
                else:
                    print("dealing with mix modes!!!")
                    newRuleList, attrList = self.getFirstNonAttr(data[i])
                    print("newDataList=", newRuleList)
                    print("attrList=", attrList)
                    if len(attrList) > 0:
                        res = self.rule(newRuleList, data, True, excludeList)
                        print("RESULT0: ", res[0])
#                        print("RESULT1: ", res[1] + attrList)
                        bindList = excludeList
                        data[ i ] = [ res[1] ] + attrList # updating current ADD* key/value
                        print("RESULT1: ", data[i])
                        bindList += list(res[1])
                        res2 = self.rule([ i ], data, bindList)
#                        print("RESULT2: ", res2)
                        finalConstraints += res2[0]  + res[0] 
                        print("finalConstraints: ", finalConstraints)
                    else:
                        finalConstraints += self.rule(newRuleList, data, retList, excludeList)                        
            elif LEAF in i:
                finalConstraints += self.__attrRule(data[i]) # base case
        if retList: return finalConstraints, data[i]
        return finalConstraints
    
    def __attrRule(self, data):
        orObjects = []
        print("ATTR Rule: ", data)
        for i in data:
            orObjects.append(self.varMap.get(i) != self.nil)
#            orObjects.append(self.varMap.get(i) == nil)
        print("Result:", Or(orObjects))
        return [ Or(orObjects) ]

    def __handleNotEqualToNil(self, jj):
        if type(jj) == list:
            return And([ self.varMap.get(j) != self.nil for j in jj])
        else:
            return self.varMap.get(jj) != self.nil

    def __handleEqualToNil(self, jj):
        if type(jj) == list:
            return And([ self.varMap.get(j) == self.nil for j in jj])
        else:
            return self.varMap.get(jj) == self.nil

    def __mulRule(self, data, bindList):
        """base rule: a * b ==> Or(And(a != nil, b == nil), And(a == nil, b != nil))"""
        print("MUL Rule: ", data)
        index = 0
        orObjects = []
        for x in range(len(data)):
            objects = []
            for i,j in enumerate(data):
                if index == i:
                    objects.append(self.__handleNotEqualToNil(j))
                else:
                    objects.append(self.__handleEqualToNil(j))
            orObjects.append( And(objects) )
            index += 1
        print("MUL Result: ", Or(orObjects))
        return [ Or(orObjects) ]
    
    def __addRule(self, data, excludeList):
        """base rule: a + b ==> And(a == b), a + b + c ==> And(a == b, a == c, b == c), etc"""        
        print("ADD Rule: ", data)
        varCheck = {}
        objects = []
        for i in data:
            for j in data:
                if i in excludeList and j in excludeList: continue
                ii = self.varMap.get(i)
                jj = self.varMap.get(j)
                if i != j and (j != varCheck.get(i) and i != varCheck.get(j)):
                    varCheck[ i ] = j
                    varCheck[ j ] = i
                    objects.append(ii == jj)
                        
        print("ADD Result: ", Or(objects))
        return [ Or(objects) ]
    

class BFSolver:
    def __init__(self, skList, constraintsDict, unsatIDs):
        self.skList = skList
        self.constraintsDict = constraintsDict
        self.unsatIDs = unsatIDs

    def run(self, theSolver, unsat_id=None):
        self.theSolver = Solver() # theSolver # copy
        self.theSolver.set(unsat_core=True)
        self.theSolver.add( theSolver.assertions() )
        
        for i in self.skList:
            print("BFSolver: key =", i, ", info =", info[i])
            refs = self.unsatIDs[i][0]
            if unsat_id != None and unsat_id == refs: 
                print("BFSolver: skipping :", unsat_id)
                continue
            for j in range(len(self.constraintsDict[ i ])):
                print("BFSolver: ref: ", refs, ", constraint: ", self.constraintsDict[i][j])
                self.theSolver.assert_and_track(self.constraintsDict[i][j], refs)
            print("\n")
        
        print(self.theSolver, "\n")
        print(self.theSolver.check())
        if self.theSolver.check() != unsat:
            print("<=== Traversing Model ===>")
            model = self.theSolver.model()
            print(model)
            for i in model.decls():
                print("%s = %s" % (i.name(), model[i]))
            print("<=== Traversing Model ===>")
            return True, None
        else:
            unsat_list = self.theSolver.unsat_core()

        return False, unsat_list
# 1. construct the SetupBF Solver w/ initial 
setupBF = SetupBFSolver()
theSolver = setupBF.construct(mskVars, rndVars)
theVarMap = setupBF.theVarMap
nil = setupBF.nil

# 2. construct rule and store for each expression
index = 0
construct = ConstructRule(theVarMap, nil)
skList = info.get(skVars)
constraintsDict = {}
unsatIDs = {}
for i in skList:
    constraints = construct.rule(info[i][root], info[i])
    constraintsDict[ i ] = constraints
    ref = 'p' + str(index)
    unsatIDs[ i ] = [ref]
    index += 1
#    unsatIDs[ i ] = []
#    for j in range(len(constraints)):
#        ref = 'p' + str(index)
#        unsatIDs[ i ].append(ref)
#        index += 1


# 3. Run the Solver and deal with unsatisfiable cores.
satisfied = False
unsat_list = []
bf = BFSolver(skList, constraintsDict, unsatIDs)

print("constraintDict=", constraintsDict)
print("unsatIDs=", unsatIDs, "\n")
satisfied, newList = bf.run(theSolver)
print("<=== Summary ===>")
print("RESULTS: satisfied=", satisfied, "unsat_core=", newList)
if satisfied == False:
    for i in newList:
        pID = str(i)
        satisfied, newList = bf.run(theSolver, pID)
        print("NEW RESULTS: satisfied=", satisfied, "unsat_core=", newList)

#    print("Unsat: ", unsat_list)
#    for i in unsat_list:
#        print("Re-run w/o id: ", i)

# TODO: need a strategy to augment solver and keep skList consistent when constraints are unsatisfiable.