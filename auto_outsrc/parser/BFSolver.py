from __future__ import print_function
from z3 import *
import string, sys, importlib
import myLog

#input to BFSolver
######################################################################################
#skVar = 'sk'
#mskVars = ['alpha', 't1', 't2', 't3', 't4']
#rndVars = ['r1', 'r2']
##keywords: info, skVars, rndVars, mskVars and bfCount
#info = {'d3': {'root': ['ADD0'], 'ADD0': ['t4', '-r2', 'hID#y']}, 'sk': ['d0', 'd1', 'd2', 'd3', 'd4'], 
#'d4': {'root': ['ADD0'], 'ADD0': ['t3', '-r2', 'hID#y']}, 'd2': {'root': ['ADD0'], 'ADD0': ['t1', '-alpha', 't1', '-r1', 'hID#y']}, 
#'id': {}, 'd0': {'ADD0': ['MUL0', 'MUL2'], 'MUL2': ['r2', 'MUL3'], 'MUL3': ['t3', 't4'], 'MUL0': ['r1', 'MUL1'], 'MUL1': ['t1', 't2'], 'root': ['ADD0']}, 
#'d1': {'root': ['ADD0'], 'ADD0': ['t2', '-alpha', 't2', '-r1', 'hID#y']}}
######################################################################################
bfCount = 0
root = 'root'
ADD,MUL,LEAF,LIST='ADD','MUL','LEAF','LIST'
nil = None
infoKeyword = 'info'
mskVarsKeyword = 'mskVars'
rndVarsKeyword = 'rndVars'
skVarsKeyword = 'skVar'
bfMapKeyword = 'bfMap'
skBfMapKeyword = 'skBfMap'
hashtag = '#'
includeMskVarsInDict = False
includeDict = {}

class CleanVarRefs:
    def __init__(self, info, skVars, refVars, verbose=False):
        self.info = info
        self.skVars = skVars
        self.refVars = list(refVars)
        self.isMsk = False
        self.verbose = verbose
    
    def setIsMsk(self):
        self.isMsk = True
    
    def __getVars(self, key, srcDict):
        keyList = set()
        for i,j in srcDict.items():
            if type(j) == dict:
                return self.__getVars(key, j)
            if type(j) == list:
                for k in j:
                    if k.find(hashtag) == -1:
                        if key == k:
                            keyList = keyList.union( [ k ] )
                    else:
                        if key == k.split(hashtag)[0]:
                            keyList = keyList.union( [ k ] )                        
        return keyList
    
    def clean(self):
        global includeMskVarsInDict
        newList = set()
        for j in self.refVars:
            #if self.verbose: 
            #myLog.info("Key:", j)
            for i in self.info[self.skVars]:
                matchKeyList = self.__getVars(j, self.info[i])
                #myLog.info(i, ":", self.info[i], matchKeyList)
                newList = newList.union( matchKeyList )
        
        if set(self.refVars) == set(newList):
            return self.refVars
        elif len(newList) == 0:
            if self.isMsk: includeMskVarsInDict = True # meaning there were no references to mk variables in
            return self.refVars
        else:
            return list(newList)

        
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
                #myLog.info("Process ADD:", i, exprDict[i])
                exprDict[i] = self.__handleOp(exprDict[i])            
                self.__inputPreprocessor(exprDict[i], exprDict)
            elif MUL in i:
                #myLog.info("Process MUL:", i, exprDict[i])
                exprDict[i] = self.__handleOp(exprDict[i])
                self.__inputPreprocessor(exprDict[i], exprDict)
            elif LEAF in i:
                #myLog.info("Process LEAF:", i, exprDict[i])            
                self.__inputPreprocessor(exprDict[i], exprDict)
    
    def __inputCleaner(self, exprList, exprDict):
        for i in exprList:
            if (ADD in i) or (MUL in i):
                if self.verbose: myLog.info("Process:", i, exprDict[i])
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
            elif (LIST in i):
                keyList.append(i)
                self.__cleanDict(keyList, exprDict[i], exprDict)
            elif exprDict.get(i).get(root) != None:
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
            if self.verbose: myLog.info("Key:", i)
            if self.info[i].get(root) != None:
                self.__inputPreprocessor(self.info[i][root], self.info[i])  
                self.__inputCleaner(self.info[i][root], self.info[i])
                keys = [root]
                self.__cleanDict(keys, self.info[i][root], self.info[i])
                for j in self.info[i].keys():
                    if j not in keys:
                        del self.info[i][j]
                self.__removeSymbols(self.info[i])
                if self.verbose: myLog.info("RESULT: ", self.info[i])
            else:
                # if the original is empty, then create 
                self.info[i] = {root:['LEAF0'], 'LEAF0':[ str(i) ]}
        
    def getUpdatedInfo(self):
        return self.info
    
def readConfig(filename):
    myLog.info("Importing file: ", filename)
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
        myLog.error(mskVarsKeyword, "was not defined in ", filename); sys.exit(-1)
    elif info == None:
        myLog.error(infoKeyword, "was not defined in ", filename); sys.exit(-1)
    elif skVars == None:
        myLog.error(skVarsKeyword, "was not defined in ", filename); sys.exit(-1)
    
    info[skVars].sort()
    ci = CleanInfo(info, skVars)
    ci.clean()
    info = ci.getUpdatedInfo()
    
    if len(mskVars) > 0:
        cvr = CleanVarRefs(info, skVars, mskVars)
        cvr.setIsMsk()
        mskVars = cvr.clean()
    if len(rndVars) > 0:
        cvr = CleanVarRefs(info, skVars, rndVars)
        rndVars = cvr.clean()
    #myLog.info("New MSK LIST: ", mskVars)
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
        myLog.info("selected factors :", factors)
        
        # blinding factors
        Factors, self.factorsList = EnumSort('Factors', factors)
        myLog.info("factorList :", self.factorsList)
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
                    myLog.info("newDataList=", newRuleList)
                    myLog.info("attrList=", attrList)
                    if len(attrList) > 0:
                        res = self.rule(newRuleList, data, True, excludeList)
#                        myLog.info("RESULT0: ", res[0])
#                        myLog.info("RESULT1: ", res[1] + attrList)
                        data[ i ] = res[1] + attrList # updating current ADD* key/value
                        excludeList += list(res[1])
                        res2 = self.rule([ i ], data, excludeList)
#                        myLog.info("RESULT2: ", res[0], res2[0])
                        finalConstraints += res[0] + res2[0]
                    else:
                        finalConstraints += self.rule(newRuleList, data, retList, excludeList)
            elif MUL in i:
                if self.baseCase(data[i]):
                    if retList: newData = data[i]
                    finalConstraints += self.__mulRule(data[i], excludeList)
                else:
                    myLog.info("dealing with mix modes!!!")
                    newRuleList, attrList = self.getFirstNonAttr(data[i])
                    myLog.info("newDataList=", newRuleList)
                    myLog.info("attrList=", attrList)
                    if len(attrList) > 0:
                        res = self.rule(newRuleList, data, True, excludeList)
                        myLog.info("RESULT0: ", res[0])
#                        myLog.info("RESULT1: ", res[1] + attrList)
                        bindList = excludeList
                        data[ i ] = [ res[1] ] + attrList # updating current ADD* key/value
                        myLog.info("RESULT1: ", data[i])
                        bindList += list(res[1])
                        res2 = self.rule([ i ], data, bindList)
#                        myLog.info("RESULT2: ", res2)
                        finalConstraints += res2[0]  + res[0] 
                        myLog.info("finalConstraints: ", finalConstraints)
                    else:
                        finalConstraints += self.rule(newRuleList, data, retList, excludeList)                        
            elif LEAF in i:
                finalConstraints += self.__attrRule(data[i]) # base case
            elif LIST in i:
                print("Handle LIST: ", data[i])
                for i in data[i]:
                    print('i: ', i)
                    finalConstraints += self.rule(data[i].get(root), data[i])
                    print("Result: ", finalConstraints)
        if retList: return finalConstraints, newData
        return finalConstraints
    
    def __attrRule(self, data):
        """base rule: a ==> Or(a != nil). In other words, if attr is part of LEAF, then certainly needs to be blinded. 
        We do not allow any sk element to go unblinded."""
        orObjects = []
        myLog.info("ATTR Rule: ", data)
        for i in data:
            self.usedVars = self.usedVars.union([ i ])
            orObjects.append(self.varMap.get(i) != self.nil)
#            orObjects.append(self.varMap.get(i) == nil)
        myLog.info("Result:", Or(orObjects))
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
        myLog.info("MUL Rule: ", data)
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
        myLog.info("MUL Result: ", Or(orObjects))
        return [ Or(orObjects) ]
    
    def __addRule(self, data, excludeList):
        """base rule: a + b ==> And(a == b), a + b + c ==> And(a == b, a == c, b == c), etc"""        
        myLog.info("ADD Rule: ", data)
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
                    myLog.info("DEBUG: ", i, "==", j)
                    objects.append(ii == jj)
        
        myLog.info("ADD Result: ", And(objects))
        return [ And(objects) ]
    

class BFSolver:
    def __init__(self, skList, mskVars, constraintsDict, constraintsDictVars, unsatIDs, verbose=False):
        self.skList = skList
        self.mskVars = mskVars
        self.constraintsDict = constraintsDict
        self.constraintsDictVars = constraintsDictVars # shows variables that were used
        self.unsatIDs = unsatIDs
        self.usedBFs = None
        self.finalMapOfBFs = {}
        self.solution = {}
        self.verbose = verbose
        
    def __getPlaceholder(self):
        newUF ="uf" + str(self.index) 
        self.index += 1
        return newUF
    
    def run(self, theSolver, unsat_id=None):
        global includeMskVarsInDict
        self.index = 0
        self.usedBFs = set()
        self.theSolver = Solver() # theSolver # copy
        self.theSolver.set(unsat_core=True)
        self.theSolver.add( theSolver.assertions() )
        
        for i in self.skList:
            if self.verbose: myLog.info("BFSolver: key =", i, ", info =", info[i])
            refs = self.unsatIDs[i][0]
            if unsat_id != None and refs in unsat_id: 
                if self.verbose: myLog.info("BFSolver: skipping :", refs,"\n")
                continue
            for j in range(len(self.constraintsDict[ i ])):
                if self.verbose: myLog.info("BFSolver: ref: ", refs, ", constraint: ", self.constraintsDict[i][j])
                self.theSolver.assert_and_track(self.constraintsDict[i][j], refs)
            if self.verbose: myLog.info("\n")
        
        if self.verbose: myLog.info(self.theSolver, "\n")
        myLog.info(self.theSolver.check(), "\n")
        if self.theSolver.check() != unsat:
            myLog.info("<=== Interpret Results ===>")
            self.solution = {}
            self.finalMapOfBFs = {}
            model = self.theSolver.model()
            myLog.info(model)            
            for i in self.skList:
                myLog.info("SK: ", i, self.unsatIDs[i], )
                refs = self.unsatIDs[i][0]
                self.solution[ i ] = {}
                self.finalMapOfBFs[ i ] = set()
                if unsat_id != None and refs in unsat_id: 
                    myLog.info("unique blinding factor for: ", i, "\n")
                    bfNew = self.__getPlaceholder()
                    self.usedBFs = self.usedBFs.union([ bfNew ])
                    self.solution[ i ] = bfNew
                    self.finalMapOfBFs[ i ] = self.finalMapOfBFs[ i ].union([ bfNew ])
                    continue
                for k in self.constraintsDictVars[i]:
                    for l in model.decls():
                        lKey = str(l.name())
                        if lKey in k:
                            myLog.info("%s = %s" % (l.name(), model[l]))
                            lVal = str(model[l])
                            if lVal != 'nil':
                                self.usedBFs = self.usedBFs.union([ lVal ])
                                self.solution[ i ][ lKey ] = lVal
                                self.finalMapOfBFs[ i ] = self.finalMapOfBFs[ i ].union([ lVal ])
#                self.solution[ i ] = skSolution
                myLog.info("")
            if includeMskVarsInDict: 
                # rare cases where msk does not show up directly in any sk elements. 
                # We just include in dictionary to be safe 
                for i in self.mskVars:
                    for l in model.decls():
                        lKey = str(l.name())
                        lVal = str(model[l])
                        if lKey == i:
                            self.solution[ i ] = lVal
                            self.finalMapOfBFs[ i ] = set([ lVal ])
            myLog.info("<=== Interpret Results ===>")
            myLog.info("Unique blinding factors: ", self.usedBFs)
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
        if self.verbose: myLog.info("BFSolver.writeToFile: ", BFMapForProof)
        f.write( BFMapForProof )
        if self.verbose: myLog.info("BFSolver.writeToFile: ", SKMapForKeygen)
        f.write( SKMapForKeygen )
        f.close()
        return
    
def isSubset(hashList, hashDict, unsatIDs):
    for i in hashDict.keys():
        if set(hashList).issubset( hashDict[i] ):
            myLog.info("Found a subset. Existing reference = ", unsatIDs[i])
            return unsatIDs[i]
    return 

def searchForSolution(BFSolverObj, SolverRef, skipList):
    """description: flush out this algorithm better
    """
    myLog.info("<=== START ===>")
    myLog.info("skipList: ", skipList)
    satisfied, skipList2 = BFSolverObj.run(SolverRef, skipList)
    if satisfied:
        myLog.info("FINAL unsat_core=", skipList)
        return (True, skipList)
    elif satisfied == False and len(skipList2) > 0:
        skipList3 = list(skipList2)
        myLog.error("FAILED: ", skipList3) # new list of identifiers then recurse
        while len(skipList3) > 0:
            pID = str(skipList3.pop())
            satisfied, newList3 = BFSolverObj.run(SolverRef, skipList + [ pID ])
            if satisfied:
                return (True, skipList + [ pID ])
        
        # if all combinations failed above, then continue to the next level
        skipList3 = list(skipList2)
        while len(skipList3) > 0:
             pID = str(skipList3.pop())
             satisfied, newList4 = searchForSolution(BFSolverObj, SolverRef, skipList + [ pID ])
             if satisfied:
                 return (True, newList4) # skipList + [ pID ])
        
        return (satisfied, None)
    else:
        myLog.error("TODO: handle this scenario.")
        return (satisfied, skipList)
        
if __name__ == "__main__":
    filename = sys.argv[1]
    logname = filename.split('.')[0]
    myLog.logger = myLog.setup(logname, "/var/tmp/" + logname + ".log")
    myLog.print2screen = True
    (mskVars, rndVars, skVars, info) = readConfig(filename)
    # 1. construct the SetupBF Solver w/ initial 
    # compute upper bound on number of possible blinding factors
    bfCount = max(len(info.get(skVars)), len(mskVars))
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
        myLog.info("key: ", i)
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
    bf = BFSolver(skList, mskVars, constraintsDict, constraintsDictVars, unsatIDs, True)
    
    myLog.info("constraintsDictVars=", constraintsDictVars)
    myLog.info("constraintDict=", constraintsDict)
    myLog.info("unsatIDs=", unsatIDs, "\n")
    
    skipList = []
    satisfied, newList = bf.run(theSolver)
    myLog.info("\n<=== Summary ===>")
    myLog.info("RESULTS: satisfied=", satisfied, "unsat_core=", newList)
    if satisfied: # iff satsified on the first go around.
        myLog.info("bfVarsMap = ", bf.getBFSolution())
        myLog.info("skVarsMap = ", bf.getSKSolution())
        bf.writeToFile(filename) # success!
        exit(0)
    else:
        myLog.info("\n<=== UNSAT CORE PHASE 2 ===>")
        # if execution makes it here then we
        bf.verbose = False
        newList2 = [ str(i) for i in newList ]
        satisfied, finalUnsatIDs = searchForSolution(bf, theSolver, newList2)
        if satisfied: 
            myLog.info("<=== END ===>")
            myLog.info("SUCCESS: unsat IDs= ", finalUnsatIDs)
            satisfied, newList = bf.run(theSolver, finalUnsatIDs)
            myLog.info("bfVarsMap = ", bf.getBFSolution())
            myLog.info("skVarsMap = ", bf.getSKSolution())
            myLog.info("\n")
            bf.writeToFile(filename) # success!
            exit(0)
