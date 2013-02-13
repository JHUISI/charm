from __future__ import print_function
from z3 import *
import string, sys, importlib

# input for our BF solver
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

#mskVars = ['alpha']
#rndVars = ['t']

#rndVars = ['t', 'beta'] # try to capture ordering of instances of random vars.
#info = {'sk': ['K', 'L', 'Kl'], 'K': {'root': ['MUL0'], 'ADD0':['alpha', 'beta'], 'MUL0':['ADD0','t']}, 'L': {'root':['LEAF0'], 'LEAF0':['t']}, 'Kl': {'root':['LEAF0'], 'LEAF0':['t']}}

#rndVars = ['t', 'beta', 's'] # try to capture ordering of instances of random vars.
#info = {'sk': ['K', 'L', 'Kl'], 'K': {'root': ['ADD0'], 'ADD0': ['MUL0','MUL1'], 'MUL0':['alpha', 'beta'], 'MUL1':['s', 't']}, 'L': {'root':['LEAF0'], 'LEAF0':['t']}, 'Kl': {'root':['LEAF0'], 'LEAF0':['t']}}

#rndVars = ['t', 'beta']
#info = {'sk': ['K', 'L', 'Kl'], 'K': {'root': ['ADD0'], 'ADD0': ['t','MUL0'], 'MUL0':['alpha', 'beta']}, 'L': {'root':['LEAF0'], 'LEAF0':['t']}, 'Kl': {'root':['LEAF0'], 'LEAF0':['t']}}
#info = {'sk': ['K', 'L', 'Kl'], 'K': {'root': ['ADD0'], 'ADD0': ['alpha','t']}, 'L': {'root':['LEAF0'], 'LEAF0':['t']}, 'Kl': {'root':['LEAF0'], 'LEAF0':['t']}}

######################################################################################
bfCount = 0
root = 'root'
ADD,MUL,LEAF='ADD','MUL','LEAF'
nil = None
infoKeyword = 'info'
mskVarsKeyword = 'mskVars'
rndVarsKeyword = 'rndVars'
skVarsKeyword = 'skVar'
bfMapKeyword = 'bfMap'
skBfMapKeyword = 'skBfMap'

class CleanInfo:
    def __init__(self, info, skVars, verbose=False):
        self.info = info
        self.skVars = skVars
        self.verbose = verbose
        
    def __handleOp(self, _list):
        rmVar = None
        for j in _list:
            if j.isdigit(): 
                rmVar = j; break
        if rmVar != None: _list.remove(j)    
        return _list
    
    def __similar(self, i, j):
        m = i[:-1]
        n = j[:-1]
        if m == n: return True
        else: return False
        
    def __inputPreprocessor(self, exprList, exprDict):
        for i in exprList:
            if ADD in i:
                #print("Process ADD:", i, exprDict[i])
                exprDict[i] = self.__handleOp(exprDict[i])            
                self.__inputPreprocessor(exprDict[i], exprDict)
            elif MUL in i:
                #print("Process MUL:", i, exprDict[i])
                exprDict[i] = self.__handleOp(exprDict[i])
                self.__inputPreprocessor(exprDict[i], exprDict)
            elif LEAF in i:
                #print("Process LEAF:", i, exprDict[i])            
                self.__inputPreprocessor(exprDict[i], exprDict)
    
    def __inputCleaner(self, exprList, exprDict):
        for i in exprList:
            if (ADD in i) or (MUL in i):
                if self.verbose: print("Process:", i, exprDict[i])
                self.__inputCleaner(exprDict[i], exprDict)
                replaceWithChild = None
                for j in exprDict[i]:
                    if self.__similar(i, j): replaceWithChild = j; break
                if replaceWithChild != None:
                    exprDict[i].remove(replaceWithChild)
                    exprDict[i].extend(exprDict[replaceWithChild])
    
    def __cleanDict(self, keyList, exprList, exprDict):
        for i in exprList:
            if (ADD in i) or (MUL in i):
                keyList.append(i)
                self.__cleanDict(keyList, exprDict[i], exprDict)
            elif (LEAF in i):
                keyList.append(i)
        return 
    
    def __removeSymbols(self, exprDict):
        symbols = ['-', '?']
        for i in exprDict.keys():
            if type(exprDict[i]) == list:
                for j in range(len(exprDict[i])):
                    tmpList = exprDict[i]
                    if symbols[0] in tmpList[j]:    tmpList[j] = tmpList[j].strip(symbols[0])
                    if symbols[1] in tmpList[j]: tmpList[j] = tmpList[j].strip(symbols[1])                
            if type(exprDict[i]) == dict:
                self.__removeSymbols(exprDict[i])
            
        return
    
    def clean(self):
        for i in self.info[self.skVars]:
            if self.verbose: print("Key:", i)
            self.__inputPreprocessor(self.info[i][root], self.info[i])  
            self.__inputCleaner(self.info[i][root], self.info[i])
            keys = [root]
            self.__cleanDict(keys, self.info[i][root], self.info[i])
            for j in self.info[i].keys():
                if j not in keys:
                    del self.info[i][j]
            self.__removeSymbols(self.info[i])
            if self.verbose: print("RESULT: ", self.info[i])
        
    def getUpdatedInfo(self):
        return self.info
    
def readConfig(filename):
    print("Importing file: ", filename)
    file = filename.split('.')[0]

    fileVars = importlib.import_module(file)
    fileKeys = dir(fileVars)
    return _readConfig(fileVars, fileKeys)

def _readConfig(fileVars, fileKeys):
    info = None
    skVars = None
    mskVars = []
    rndVars = []
    
    if infoKeyword in fileKeys:
        info = getattr(fileVars, infoKeyword)
    if mskVarsKeyword in fileKeys:
        mskVars = getattr(fileVars, mskVarsKeyword)
    if rndVarsKeyword in fileKeys:
        rndVars = getattr(fileVars, rndVarsKeyword)
    if skVarsKeyword in fileKeys:
        skVars = getattr(fileVars, skVarsKeyword)
    
    if len(mskVars) == 0:
        print(mskVarsKeyword, "was not defined in ", filename); sys.exit(-1)
    elif info == None:
        print(infoKeyword, "was not defined in ", filename); sys.exit(-1)
    elif skVars == None:
        print(skVarsKeyword, "was not defined in ", filename); sys.exit(-1)
    
    info[skVars].sort()
    #print("BEFORE: ", info)
    ci = CleanInfo(info, skVars)
    ci.clean()
    info = ci.getUpdatedInfo()
    #print("AFTER:  ", info)
    return (mskVars, rndVars, skVars, info)

def clean(v):
    removeSymbols = ['-', '#', '?']
    for i in removeSymbols:
        if v.find(i) != -1:
            v.strip(i)
    return v

class SetupBFSolver:
    def __init__(self, bfCount):
        self.bfCount = bfCount
        self.factorsList = None
        self.theVarMap = None
        self.varList = None
        self.mskList = None
        self.nonNilList = None
        
    def construct(self, mskVars, rndVars):
        # Standard code below
        keygenVars = mskVars + rndVars
        alphabet = 'bf' #string.ascii_lowercase
        factors = []
        
        for i in range(self.bfCount):
            factors.append(alphabet + str(i))
#            factors.append(alphabet[i])
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
    
    def getUsedVars(self):
        return self.usedVars
    
    def rule(self, ruleType, data, retList=False, excludeList=[]):
        self.usedVars = set()
        finalConstraints = []
        newData = None
        for i in ruleType:
            if ADD in i:
                if self.baseCase(data[i]):
                    if retList: newData = data[i]
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
                    if retList: newData = data[i]
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
        if retList: return finalConstraints, newData
        return finalConstraints
    
    def __attrRule(self, data):
        orObjects = []
        print("ATTR Rule: ", data)
        for i in data:
            self.usedVars = self.usedVars.union([ i ])
            orObjects.append(self.varMap.get(i) != self.nil)
#            orObjects.append(self.varMap.get(i) == nil)
        print("Result:", Or(orObjects))
        return [ Or(orObjects) ]

    def __handleNotEqualToNil(self, jj):
        if type(jj) == list:
            self.usedVars = self.usedVars.union(jj)
            return And([ self.varMap.get(j) != self.nil for j in jj])
        else:
            self.usedVars = self.usedVars.union([jj])
            return self.varMap.get(jj) != self.nil

    def __handleEqualToNil(self, jj):
        if type(jj) == list:
            self.usedVars = self.usedVars.union(jj)
            return And([ self.varMap.get(j) == self.nil for j in jj])
        else:
            self.usedVars = self.usedVars.union([jj])
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
            self.usedVars = self.usedVars.union([i])
            for j in data:
                if i in excludeList and j in excludeList: continue
                ii = self.varMap.get(i)
                jj = self.varMap.get(j)
                if i != j and (j != varCheck.get(i) and i != varCheck.get(j)):
                    varCheck[ i ] = j
                    varCheck[ j ] = i
                    print("DEBUG: ", i, "==", j)
                    objects.append(ii == jj)
        
        print("OBJECTS: ", objects)
#        print("ADD Result: ", Or(objects))
#        return [ Or(objects) ]
        print("ADD Result: ", And(objects))
        return [ And(objects) ]
    


# simultaneous solver over sk element variables.
class SKSolver:
    def __init__(self, skList):
        self.skList = skList
    
    def run(self):
        pass

class BFSolver:
    def __init__(self, skList, constraintsDict, constraintsDictVars, unsatIDs, verbose=False):
        self.skList = skList
        self.constraintsDict = constraintsDict
        self.constraintsDictVars = constraintsDictVars # shows variables that were used
        self.unsatIDs = unsatIDs
        self.usedBFs = None
        self.finalMapOfBFs = {}
        self.solution = {}
        self.verbose = verbose
        
    def __getPlaceholder(self):
        self.index += 1
        return"uf" + str(self.index) 
    
    def run(self, theSolver, unsat_id=None):
        self.index = 0
        self.usedBFs = set()
        self.theSolver = Solver() # theSolver # copy
        self.theSolver.set(unsat_core=True)
        self.theSolver.add( theSolver.assertions() )
        
        for i in self.skList:
            print("BFSolver: key =", i, ", info =", info[i])
            refs = self.unsatIDs[i][0]
            if unsat_id != None and unsat_id == refs: 
                print("BFSolver: skipping :", unsat_id,"\n")
                continue
            for j in range(len(self.constraintsDict[ i ])):
                print("BFSolver: ref: ", refs, ", constraint: ", self.constraintsDict[i][j])
                self.theSolver.assert_and_track(self.constraintsDict[i][j], refs)
            print("\n")
        
        print(self.theSolver, "\n")
        print(self.theSolver.check(), "\n")
        if self.theSolver.check() != unsat:
            print("<=== Interpret Results ===>")
            model = self.theSolver.model()
            print(model)
            for i in self.skList:
                print("SK: ", i, self.unsatIDs[i], )
                refs = self.unsatIDs[i][0]
                self.solution[ i ] = {}
                self.finalMapOfBFs[ i ] = set()
                if unsat_id != None and unsat_id == refs: 
                    print("unique blinding factor for: ", i, "\n")
                    bfNew = self.__getPlaceholder()
                    self.usedBFs = self.usedBFs.union([ bfNew ])
                    self.solution[ i ] = bfNew
                    self.finalMapOfBFs[ i ] = self.finalMapOfBFs[ i ].union([ bfNew ])
                    continue
                for k in self.constraintsDictVars[i]:
                    for l in model.decls():
                        lKey = str(l.name())
                        if lKey in k:
                            print("%s = %s" % (l.name(), model[l]))
                            lVal = str(model[l])
                            if lVal != 'nil':
                                self.usedBFs = self.usedBFs.union([ lVal ])
                                self.solution[ i ][ lKey ] = lVal
                                self.finalMapOfBFs[ i ] = self.finalMapOfBFs[ i ].union([ lVal ])
#                self.solution[ i ] = skSolution
                print("")
            print("<=== Interpret Results ===>")
            print("Unique blinding factors: ", self.usedBFs)
            return True, None
        else:
            unsat_list = self.theSolver.unsat_core()

        return False, unsat_list
    
    def getBFSolution(self):
        return self.solution
    
    def getSKSolution(self):
        return self.finalMapOfBFs
    
    def writeToFile(self, filename):
        assert len(self.solution) > 0, "BF solution is empty!"
        assert len(self.finalMapOfBFs) > 0, "sk BF solution is empty!"
        BFMapForProof = bfMapKeyword + " = " + str(self.solution) + "\n"
        newDict = {}
        for i,j in self.finalMapOfBFs.items():
            newDict[i] = list(j)[0] # assume just one element in list
        SKMapForKeygen = skBfMapKeyword + " = " + str(newDict) + "\n"
        f = open(filename, 'a')
        if self.verbose: print("BFSolver.writeToFile: ", BFMapForProof, end="")
        f.write( BFMapForProof )
        if self.verbose: print("BFSolver.writeToFile: ", SKMapForKeygen)
        f.write( SKMapForKeygen )
        f.close()
        return
    
def isSubset(hashList, hashDict, unsatIDs):
    for i in hashDict.keys():
        if set(hashList).issubset( hashDict[i] ):
            print("Found a subset. Existing reference = ", unsatIDs[i])
            return unsatIDs[i]
    return 


if __name__ == "__main__":
    filename = sys.argv[1]
    (mskVars, rndVars, skVars, info) = readConfig(filename)
    # 1. construct the SetupBF Solver w/ initial 
    bfCount = len(info.get(skVars))
    setupBF = SetupBFSolver(bfCount)
    theSolver = setupBF.construct(mskVars, rndVars)
    theVarMap = setupBF.theVarMap
    nil = setupBF.nil
    
    # 2. construct rule and store for each expression
    index = 0
    construct = ConstructRule(theVarMap, nil)
    skList = info.get(skVars)
    constraintsDict = {}
    constraintsDictVars = {}
    unsatIDs = {}
    hashID = {}
    for i in skList:
        print("key: ", i)
        constraints = construct.rule(info[i][root], info[i])
        constraintsDictVars[ i ] = construct.getUsedVars()
        constraintsDict[ i ] = constraints
        _hashID = []
        unsatIDs[ i ] = []
        for j in range(len(constraints)):
            _hashID.append(constraints[j].hash())
        
        # determine if hashID list is a subset of another variable. 
        # Replace the refID to minimize assert tracking issues associated with group element expressions
        refVal = isSubset(_hashID, hashID, unsatIDs)
        if refVal == None:
            ref = 'p' + str(index)
            unsatIDs[ i ].append(ref)
            index += 1
        else:
            unsatIDs[ i ] = refVal
        hashID[i] = _hashID
                
    # 3. Run the Solver and deal with unsatisfiable cores.
    satisfied = False
    unsat_list = []
    bf = BFSolver(skList, constraintsDict, constraintsDictVars, unsatIDs)
    
    print("constraintsDictVars=", constraintsDictVars)
    print("constraintDict=", constraintsDict)
    print("unsatIDs=", unsatIDs, "\n")

    satisfied, newList = bf.run(theSolver)
    print("\n<=== Summary ===>")
    print("RESULTS: satisfied=", satisfied, "unsat_core=", newList)
    if satisfied: # iff satsified on the first go around.
        print("bfVarsMap = ", bf.getBFSolution())
        print("skVarsMap = ", bf.getSKSolution())
        bf.writeToFile(filename)
        exit(0)
        # append results to the input filename
    elif len(newList) == 1: # satisfied == False
        pID = str(newList[0])
        satisfied, newList = bf.run(theSolver, pID)
        print("NEW RESULTS: satisfied=", satisfied, "unsat_core=", newList)
        if satisfied:
            print("<=== END ===>")
            print("bfVarsMap = ", bf.getBFSolution())
            print("skVarsMap = ", bf.getSKSolution())
            print("\n")
            bf.writeToFile(filename)
    else:
        for i in newList:
            pID = str(i)
            satisfied, newList2 = bf.run(theSolver, pID)
            print("NEW RESULTS: satisfied=", satisfied, "unsat_core=", newList)
            print("<=== END ===>")
            print("\n")
    
    # TODO: need a strategy to augment solver and keep skList consistent when constraints are unsatisfiable.