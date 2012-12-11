# TODO: automatically convert SDL from symmetric to aymmetric 
# 
# Approach: 
# 1. parse the scheme (start from the pairing operations)
# 2. identify variables that must be in different groups. e.g., pair(a, b) means a <- G1 and b <- G2
# 3. values that have type G2 -> work backwards to change them into G2 
#    - should invoke our type inference to verify that we haven't violated rules.
#    - spit out types at the end of all variables that have changed assignments - note that 
#    - this doesn't consider the ciphertext reduction problem.

# 4. Label ciphertext elements and identify all the variables that can be moved to G1 vs. G2: 
#     - must verify that we don't compromise on the security
import sdlpath, sys, os, random, string
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *
from outsrctechniques import SubstituteVar, SubstitutePairings

assignInfo = None
SHORT_KEYS = "keys" # for
SHORT_CIPHERTEXT = "ciphertext" # in case, an encryption scheme
SHORT_SIGNATURE  = "signature" # in case, a sig algorithm
SHORT_FORALL = "both"
variableKeyword = "variables"
clauseKeyword = "clauses"
constraintKeyword = "constraints"
PUB_SCHEME = "PUB"
SIG_SCHEME = "SIG"
length = 5 # length of temporary file

class GetPairingVariables:
    def __init__(self, list1, list2):
        assert type(list1) == type(list2) and type(list1) == list, "GetPairingVariables: invalid input type"
        self.listLHS = list1
        self.listRHS = list2
        
    def visit(self, node, data):
        pass
    
    def visit_pair(self, node, data):
        if Type(node.left) == ops.ATTR and Type(node.right) == ops.ATTR:
            self.listLHS.append(str(node.left.getRefAttribute()))
            self.listRHS.append(str(node.right.getRefAttribute()))
        elif Type(node.left) == ops.ATTR and Type(node.right) != ops.ATTR:
            pass
        elif Type(node.left) != ops.ATTR and Type(node.right) == ops.ATTR:
            pass

class transformXOR:
    def __init__(self, fixedValues):
        self.groundTruth = fixedValues
        self.varMap = {}
        self.varsList = [] # records variable instances?
        self.xorList = [] # records tuple
        self.alphabet = list(string.ascii_lowercase)
        self.count = 0

    def __getNextVar(self):
        suffixCount = int(self.count / len(self.alphabet))
        if suffixCount > 0: suffix = str(suffixCount)
        else: suffix = ''
        
        count = self.count % len(self.alphabet)
        a = self.alphabet[ count ] + suffix
        self.count += 1
        return a
    
    def visit(self, node, data):
        return
    
    def visit_xor(self, node, data):
        var1 = str(node.left)
        var2 = str(node.right)
        if var1 not in self.varMap.keys():
            alpha_x = self.__getNextVar()
        else:
            alpha_x = self.varMap[ var1 ]
            
        if var2 not in self.varMap.keys():
            alpha_y = self.__getNextVar()
        else:
            alpha_y = self.varMap[ var2 ]
        
        self.varMap[ var1 ] = alpha_x
        self.varMap[ var2 ] = alpha_y
        
        self.xorList.append( (alpha_x, alpha_y) )
        return
        
    def getVarMap(self):
        return self.varMap
    
    def getVariables(self):
        keys = list(set(self.varMap.values()))
        keys.sort()
        return keys
    
    def getClauses(self):
        return self.xorList        


"""
1. generic function that takes three lists of group assignments..
    { 'G1' : varList, 'G2' : varList, 'both': varList }
2. goes through a given 'block' and goes each statement:
    - exponentiation, multiplication and pairing
    - rewrite each statement where a generator appears (or derivative of one) using three lists:
        if leftAssignVar in 'both': create 2 statements
        if leftAssignVar in 'G1': create 1 statement in G1
        if leftAssignVar in 'G2': create 1 statement in G2
"""
def transformFunction(funcName, blockStmts, info, noChangeList, startLines=[]):
    begin = "BEGIN :: func:" + funcName
    end = "END :: func:" + funcName
    newLines = [begin] # + list(startLines)
    lines = list(blockStmts.keys())
    lines.sort()
    for i in lines:
        assign = blockStmts[i].getAssignNode()
        print(i, ":", assign, end="")
        if Type(assign) == ops.EQ:
            assignVar = blockStmts[i].getAssignVar()
            # store for later
            if assignVar == sdl.inputVarName:
                newLines.append(str(assign))
                newLines.extend(startLines)
            elif blockStmts[i].getHasRandomness():
                if not assignVarIsGenerator(assignVar, info):
                    print(" :-> not a generator, so add to newLines.", end="") # do not include in new setup 
                    newLines.append(str(assign)) # unmodified
            elif assignVarOccursInBoth(assignVar, info):
                print(" :-> split computation in G1 & G2:", blockStmts[i].getVarDepsNoExponents(), end="")
                newLines.extend(updateAllForBoth(assign, assignVar, blockStmts[i].getVarDepsNoExponents(), info, True, noChangeList))
            elif assignVarOccursInG1(assignVar, info):
                print(" :-> just in G1:", blockStmts[i].getVarDepsNoExponents(), end="")
                noChangeList.append(str(assignVar))
                newLines.append(updateAllForG1(assign, assignVar, blockStmts[i].getVarDepsNoExponents(), info, False, noChangeList))
            elif assignVarOccursInG2(assignVar, info):
                print(" :-> just in G2:", blockStmts[i].getVarDepsNoExponents(), end="")
                noChangeList.append(str(assignVar))
                newLines.append(updateAllForG2(assign, assignVar, blockStmts[i].getVarDepsNoExponents(), info, False, noChangeList))                
            elif blockStmts[i].getHasPairings(): # in GT so don't need to touch assignVar
                print(" :-> update pairing.", end="")
                noChangeList.append(str(assignVar))
                newLines.append(updatForPairing(blockStmts[i], info))
            elif blockStmts[i].getIsList() or blockStmts[i].getIsExpandNode():
                print(" :-> updating list...", end="")
                newLines.append(updateForLists(blockStmts[i], info))
            else:
                newLines.append(str(assign))
        else:
            newLines.append(str(assign)) 
            # TODO: expand for IF, FOR and other types of non-EQ nodes that will come up.
            # TODO: will need to update this section as you see more schemes
        print("")
    
    newLines.append(end)
    return newLines
    
def main(config):
    global assignInfo
    assignInfo = sdl.getAssignInfo()
    setting = sdl.assignInfo[sdl.NONE_FUNC_NAME][ALGEBRAIC_SETTING].getAssignNode().getRight().getAttribute()
    bv_name = sdl.assignInfo[sdl.NONE_FUNC_NAME][BV_NAME].getAssignNode().getRight().getAttribute()
    typesBlock = sdl.getFuncStmts( TYPES_HEADER )
    print("name is", bv_name)
    print("setting is", setting)
    
    lines = list(typesBlock[0].keys())
    lines.sort()
    typesBlockLines = [ i.rstrip() for i in sdl.getLinesOfCodeFromLineNos(lines) ]
    begin = ["BEGIN :: " + TYPES_HEADER]
    end = ["END :: " + TYPES_HEADER]

    newLines0 = [ BV_NAME + " := " + bv_name, setting + " := " + sdl.ASYMMETRIC_SETTING ] 
    newLines1 = begin + typesBlockLines + end
    
    if setting != sdl.SYMMETRIC_SETTING:
        print("No need to convert to asymmetric setting.\n")
        exit(0) # or continue
    
    # determine user preference in terms of keygen or encrypt
    contarget = sdl.assignInfo[sdl.NONE_FUNC_NAME]['short']
    if contarget:
        target = contarget.getAssignNode().right.getAttribute()
    if contarget == None:
        short = SHORT_KEYS
    else:
        short = target
    print("reducing size of '%s'" % short) 

    varTypes = sdl.getVarTypes()
    (stmtS, typesS, depListS, depListNoExpS, infListS, infListNoExpS) = sdl.getFuncStmts( config.setupFuncName )
    generators = []
    print("List of generators for scheme")
    lines = stmtS.keys()
    for i in lines:
        if stmtS[i].getHasRandomness() and Type(stmtS[i].getAssignNode()) == ops.EQ:
            t = stmtS[i].getAssignVar()
            if typesS.get(t) == None: 
                typ = stmtS[i].getAssignNode().right.left.attr
                print("Retrieved type directly: ", typ)
            else:
                typ = typesS[t].getType()
            if typ == types.G1:
                print(i, ": ", typ, " :=> ", stmtS[i].getAssignNode())
                generators.append(str(stmtS[i].getAssignVar()))
    #print("depListNoExp :=", depListNoExp)
    #print("infListNoExp :=", infListNoExp)

    # need a Visitor class to build these variables   
    pair_vars_G1_lhs = [] # ['C#1', 'C#2', 'C#3', 'C#4', 'C#5', 'C#6', 'C#7', 'E1', 'E2']
    pair_vars_G1_rhs = [] # ['D#1', 'D#2', 'D#3', 'D#4', 'D#5', 'D#6', 'D#7', 'D#7', 'K']
    gpv = GetPairingVariables(pair_vars_G1_lhs, pair_vars_G1_rhs) 
    (stmtD, typesD, depListD, depListNoExpD, infListD, infListNoExpD) = sdl.getFuncStmts( config.decryptFuncName )
    lines = stmtD.keys()
    for i in lines:
        if stmtD[i].getHasPairings():
            sdl.ASTVisitor( gpv ).preorder( stmtD[i].getAssignNode() )
            
    print("pair vars LHS:", pair_vars_G1_lhs)
    print("pair vars RHS:", pair_vars_G1_rhs) 
    print("list of gens :", generators)
    info = {}
    info[ 'G1_lhs' ] = (pair_vars_G1_lhs, assignTraceback(generators, varTypes, pair_vars_G1_lhs))
    info[ 'G1_rhs' ] = (pair_vars_G1_rhs, assignTraceback(generators, varTypes, pair_vars_G1_rhs))

    print("info => G1 lhs : ", info['G1_lhs'])
    print("info => G1 rhs : ", info['G1_rhs'])
    print("<===== Determine Asymmetric Generators =====>")
    (generatorLines, generatorMapG1, generatorMapG2) = Step1_DeriveSetupGenerators(generators, info)
    print("Generators in G1: ", generatorMapG1)
    print("Generators in G2: ", generatorMapG2)
    print("<===== Determine Asymmetric Generators =====>\n")
    
    print("<===== Generate XOR clauses =====>")  
    # let the user's preference for fixing the keys or ciphertext guide this portion of the algorithm.
    # info[ 'G1' ] : represents (varKeyList, depVarMap). 
    if len(pair_vars_G1_lhs) == len(pair_vars_G1_rhs):
        varsLen = len(pair_vars_G1_lhs)
    xorList = []
    for i in range(varsLen):
        xor = BinaryNode(ops.XOR)
        xor.left = BinaryNode(pair_vars_G1_lhs[i])
        xor.right = BinaryNode(pair_vars_G1_rhs[i])
        xorList.append(xor)
    
    ANDs = [ BinaryNode(ops.AND) for i in range(len(xorList)-1) ]
    for i in range(len(ANDs)):
        ANDs[i].left = BinaryNode.copy(xorList[i])
        if i < len(ANDs)-1: ANDs[i].right = ANDs[i+1]
        else: ANDs[i].right = BinaryNode.copy(xorList[i+1])
    print("XOR clause: ", ANDs[0])
    txor = transformXOR(None) # accepts dictionary of fixed values
    sdl.ASTVisitor(txor).preorder(ANDs[0])
    print("<===== Generate XOR clauses =====>")
    
    print("\n<===== Generate Constraints =====>")
    xorVarMap = txor.getVarMap()
    (stmtK, typesK, depListK, depListNoExpK, infListK, infListNoExpK) = sdl.getFuncStmts( config.keygenFuncName )
    (stmtE, typesE, depListE, depListNoExpE, infListE, infListNoExpE) = sdl.getFuncStmts( config.encryptFuncName )
    constraints = "[]"
    if short == SHORT_KEYS:
        # create constraints around keys
        assert type(config.keygenSecVar) == list, "keygenSecVar in config file expected as list of variables"
        keygenSecVarList = []
        for i in config.keygenSecVar:
            if xorVarMap.get(i) != None: keygenSecVarList.append( xorVarMap.get(i) )
        constraints = str(keygenSecVarList)
    elif short == SHORT_CIPHERTEXT:
        assert type(config.ciphertextVar) == list, "ciphertextVar in config file expected as list of variables"
        ciphertextVarList = []
        for i in config.ciphertextVar:
            if xorVarMap.get(i) != None: ciphertextVarList.append( xorVarMap.get(i) )
        constraints = str(ciphertextVarList)
    elif short == SHORT_SIGNATURES:
        pass #TODO
    elif short == SHORT_FORALL:
        pass #default
    print("<===== Generate Constraints =====>\n")    
    
    print("<===== Generate SAT solver input =====>")
    
    # TODO: process constraints and add to output
    print("map: ", xorVarMap)
    print("variables = ", txor.getVariables())
    outputVariables = variableKeyword + " = " + str(txor.getVariables()) + "\n"
    print("clauses = ", txor.getClauses())
    outputClauses   = clauseKeyword + " = " + str(txor.getClauses()) + "\n"
    print("constraints = ", constraints)
    outputConstraints = constraintKeyword + " = " + str(constraints) + "\n"
    # get random file
    name = ""
    for i in range(length):
        name += random.choice(string.ascii_lowercase + string.digits)
    name += ".py"
    f = open(name, 'w')
    f.write(outputVariables)
    f.write(outputClauses)
    f.write(outputConstraints)
    f.close()
    print("<===== Instantiate Z3 solver =====>")
    os.system("python2.7 z3solver.py %s" % name)
    newName = name.split('.')[0]
    results = __import__(newName)
    print(results.resultDictionary)
    print("<===== Instantiate Z3 solver =====>")
        
    res, resMap = NaiveEvaluation(results.resultDictionary, short)
    print("Group Mapping: ", res)
    # determine whether to make True = G1 and False = G2. 
    # It depends on which counts more since they're interchangeable...
    groupInfo = DeriveSolution(res, resMap, xorVarMap, info)
    groupInfo['generators'] = generators 
    groupInfo['generatorMapG1'] = generatorMapG1
    groupInfo['generatorMapG2'] = generatorMapG2
    groupInfo['baseGeneratorG1'] = info['baseGeneratorG1'] # usually 'g'
    groupInfo['baseGeneratorG2'] = info['baseGeneratorG2']
    groupInfo['varTypes'] = {}
    
    noChangeList = []
    
    assert config.schemeType == PUB_SCHEME, "Cannot work with any other type of scheme at the moment"
    print("<===== transforming setup =====>")
    groupInfo['varTypes'].update(typesS)
    newLinesS = transformFunction(config.setupFuncName, stmtS, groupInfo, noChangeList, generatorLines)
    print("<===== transforming setup =====>\n")
    
    print("<===== transforming keygen =====>")            
    groupInfo['varTypes'].update(typesK)
    newLinesK = transformFunction(config.keygenFuncName, stmtK, groupInfo, noChangeList)
    print("<===== transforming keygen =====>")            

    print("<===== transforming encrypt =====>")
    groupInfo['varTypes'].update(typesE)
    newLinesE = transformFunction(config.encryptFuncName, stmtE, groupInfo, noChangeList)
    print("<===== transforming encrypt =====>")

    print("<===== transforming decrypt =====>")
    groupInfo['varTypes'].update(typesD)
    newLinesD = transformFunction(config.decryptFuncName, stmtD, groupInfo, noChangeList)
    print("<===== transforming decrypt =====>")

    print("<===== new SDL =====>")
    for i in newLinesS:
        print(i)
    print("\n\n")
    for i in newLinesK:
        print(i)
    print("\n\n")
    for i in newLinesE:
        print(i)
    print("\n\n")
    for i in newLinesD:
        print(i)
    print("<===== new SDL =====>")
    
    writeConfig(bv_name + "_asym.bv", newLines0, newLines1, newLinesS, newLinesK, newLinesE, newLinesD)
    os.system("rm -f " + name + "*")
    return

# temporary placement
def NaiveEvaluation(solutionList, preference):
    trueCount = 0
    falseCount = 0
    resMap = {}
    for tupl in solutionList:
        (k, v) = tupl
        if v == True: trueCount += 1
        elif v == False: falseCount += 1
        else: sys.exit("z3 results have been tampered with.")
        resMap[ k ] = v
    
    if preference in [SHORT_KEYS, SHORT_CIPHERTEXT, SHORT_SIGNATURE]:
        return {True:'G1', False:'G2'}, resMap
    
    if trueCount >= falseCount: 
        G1 = True; G2 = False
    elif falseCount > trueCount:
        G1 = False; G2 = True

    return { G1:'G1', G2:'G2' }, resMap

def DeriveSolution(groupMap, resultMap, xorMap, info):
    print("<===== Deriving Solution from Results =====>")
    G1_deps = set()
    G2_deps = set()
    for i in info['G1_lhs'][0] + info['G1_rhs'][0]:
        # get the z3 var for it
        z3Var = xorMap.get(i) # gives us an alphabet
        # look up value in resultMap
        varValue = resultMap.get(z3Var)
        # get group
        group = groupMap.get(varValue)
        if i in info['G1_lhs'][0]: deps = info['G1_lhs'][1].get(i)
        else: deps = info['G1_rhs'][1].get(i)
        deps = list(deps); deps.append(i) # var name to the list
        print(i, ":=>", group, ": deps =>", deps)
        if group == 'G1': G1_deps = G1_deps.union(deps)
        elif group == 'G2': G2_deps = G2_deps.union(deps)
    print("<===== Deriving Solution from Results =====>")    
    both = G1_deps.intersection(G2_deps)
    G1 = G1_deps.difference(both)
    G2 = G2_deps.difference(both)
    print("Both G1 & G2: ", both)
    print("Just G1: ", G1)
    print("Just G2: ", G2)
    return {'G1':G1, 'G2':G2, 'both':both}
    

def assignTraceback(generators, varTypes, listVars):
    varProp = []
    data = {}
    # get variable names from all pairing
    for i in listVars:
        #print("var name := ", i)
        var = i
        buildMap(generators, varTypes, varProp, var)
        data[i] = set(varProp)
        varProp = []
    
    for i in listVars:
        print("key: ", i, ":=>", data[i])
#    print("varProp for ", listVars[0], ": ", varProp)
    return data

        
def buildMap(generators, varTypes, varList, var):
    global assignInfo
    removeList = []
    if (not set(var).issubset(generators)):
        print("var keys: ", var)
        (name, varInf) = getVarNameEntryFromAssignInfo(assignInfo, var)
        if(name == None):             
            print("Var : ", varInf.getVarDepsNoExponents())
            return
        l = varInf.getVarDepsNoExponents()
#        print("var:", var, ", output: ", l)
        # prune 'l' here
        for i in l:
            print("name: ", i) # uncomment for ckrs09 error
            typeI = sdl.getVarTypeFromVarName(i, None, True)
            print("getVarTypeFromVarName:  ", i,":", typeI)
            if typeI == types.NO_TYPE:
                node = BinaryNode(ops.ATTR)
                node.setAttribute(i)
                print("getVarNameFromListIndices req node: ", node)
                (funcName , newVarName) = getVarNameFromListIndices(assignInfo, varTypes, node, True)
                print("funcName: ", funcName)
                print("newVarName: ", newVarName)
                if newVarName != None: 
                    print("newVarName := ", newVarName)
                    resultVarName = getVarTypeFromVarName(newVarName, None, True)
#                    print("second attempt: ", newVarName, ":", resultVarName)
                    varList.append(newVarName)
                else:
                    varList.append(i)
            elif typeI in [types.G1]:
                varList.append(i)
            elif typeI in [types.ZR, types.str, types.list, types.object]:
                removeList.append(str(i))
                continue
            else:
                pass
#                print("TODO: missing a case in buildMap: ", typeI)
                
#        varList.extend(l)
        varsToCheck = list(l)
        for i in varsToCheck:
            lenBefore = len(varList)
            buildMap(generators, varTypes, varList, i)
            lenAfter  = len(varList)
            if lenBefore == lenAfter:
                node = BinaryNode(ops.ATTR)
                node.setAttribute(i)
                print("Node :=>", node)
                (funcName, string) = getVarNameFromListIndices(assignInfo, varTypes, node, True)
                if string != None: varList.append(string)

        for i in removeList:
            print("REMOVING: ", i)
            print("varList: ", varList)
            
    return    

def Step1_DeriveSetupGenerators(generators, info):
    generatorLines = []
    generatorMapG1 = {}
    generatorMapG2 = {}

    if len(generators) == 0:
        sys.exit("The scheme selects no generators in setup? Please try again.\n")
    
    G1Prefix = "_G1"
    G2Prefix = "_G2"
    base_generator = generators[0]
    # split the first generator
    base_generatorG1 = base_generator + G1Prefix
    base_generatorG2 = base_generator + G2Prefix
    generatorLines.append(base_generatorG1 + " := random(G1)")
    generatorLines.append(base_generatorG2 + " := random(G2)")
    generatorMapG1[ base_generator ] = base_generatorG1
    generatorMapG2[ base_generator ] = base_generatorG2
    info['baseGeneratorG1'] = base_generatorG1
    info['baseGeneratorG2'] = base_generatorG2
    
    for j in range(1, len(generators)):
        i = generators[j]
        generatorLines.append(i + " := random(ZR)")
        generatorLines.append(i + G1Prefix + " := " + base_generatorG1 + " ^ " + i)
        generatorLines.append(i + G2Prefix + " := " + base_generatorG2 + " ^ " + i)
        generatorMapG1[ i ] = i + G1Prefix
        generatorMapG2[ i ] = i + G2Prefix
    
    print("....New Generators...")
    for line in generatorLines:
        print(line)
    print("....New Generators...")
    return (generatorLines, generatorMapG1, generatorMapG2)


def assignVarOccursInBoth(varName, info):
    if varName in info['both']:
        return True
    return False

def assignVarOccursInG1(varName, info):
    if varName in info['G1']:
        return True
    return False

def assignVarOccursInG2(varName, info):
    if varName in info['G2']:
        return True
    return False


def assignVarIsGenerator(varName, info):
    generatorList = info['generators']
    return varName in generatorList

def updateAllForBoth(node, assignVar, varDeps, info, changeLeftVar=True, noChangeList=[]):
    newLine1 = updateAllForG1(node, assignVar, varDeps, info, changeLeftVar, noChangeList)
    newLine2 = updateAllForG2(node, assignVar, varDeps, info, changeLeftVar, noChangeList)
    return [newLine1, newLine2]

def updateAllForG1(node, assignVar, varDeps, info, changeLeftVar, noChangeList=[]):
    varTypes = info['varTypes']
    new_node2 = BinaryNode.copy(node)
    # 1. assignVar
    if changeLeftVar: new_assignVar = assignVar + "_G1"
    else: new_assignVar = str(assignVar)
    sdl.ASTVisitor( SubstituteVar(assignVar, new_assignVar) ).preorder( new_node2 )
    info['generatorMapG1'][assignVar] = new_assignVar
    newVarDeps = set(varDeps).difference(noChangeList)
    for i in newVarDeps:
        v = varTypes.get(i)
        if v != None: v = v.getType()
        # prune (as a second effort)
        if v in [types.ZR, types.listZR, types.int, types.listInt, types.str, types.listStr]: 
            continue        
        new_i = i + "_G1"
        sdl.ASTVisitor( SubstituteVar(i, new_i) ).preorder( new_node2 )
        info['generatorMapG1'][i] = new_i
    print("\n\tChanged: ", new_node2, end="")
    return str(new_node2)

def updateAllForG2(node, assignVar, varDeps, info, changeLeftVar, noChangeList=[]):
    varTypes = info.get('varTypes')    
    new_node2 = BinaryNode.copy(node)
    # 1. assignVar
    if changeLeftVar: new_assignVar = assignVar + "_G2"
    else: new_assignVar = str(assignVar)
    sdl.ASTVisitor( SubstituteVar(assignVar, new_assignVar) ).preorder( new_node2 )
    info['generatorMapG2'][assignVar] = new_assignVar
    newVarDeps = set(varDeps).difference(noChangeList)
    for i in newVarDeps:
        v = varTypes.get(i)
        if v != None: v = v.getType()
        # prune (as a second effort)
        if v in [types.ZR, types.listZR, types.int, types.listInt, types.str, types.listStr]: 
            continue
        new_i = i + "_G2"
        sdl.ASTVisitor( SubstituteVar(i, new_i) ).preorder( new_node2 )
        info['generatorMapG2'][i] = new_i
    print("\n\tChanged: ", new_node2, end="")
    return str(new_node2)

def updateForLists(varInfo, info):
    newList = []
    inBoth = info['both']
    orig_list = varInfo.getAssignNode().getRight().listNodes
#    orig_list = varInfo.getListNodesList()

    for i in orig_list:
        if i in inBoth:
            newList.extend([i + "_G1", i + "_G2"])
        else:
            newList.append(i)
    new_node = BinaryNode.copy(varInfo.getAssignNode())
    new_node.right.listNodes = newList
    print("\n\tnewList: ", new_node)
    return str(new_node)

def updatForPairing(varInfo, info):    
    node = BinaryNode.copy(varInfo.getAssignNode())
    
    for i in varInfo.getVarDepsNoExponents():
        if i in info['generators']: #only if the attr's refer to generators directly...
            # action: always revert to base generators selected for asymmetric as opposed to maintain
            # symmetricity in asymmetric setting...if that makes any sense!
            sdl.ASTVisitor( SubstitutePairings(i, info['baseGeneratorG1'], 'left')).preorder( node )
            sdl.ASTVisitor( SubstitutePairings(i, info['baseGeneratorG2'], 'right')).preorder( node )    
    print("\n\t Changed: ", node)
    return str(node)

def writeConfig(filename, *args):
    f = open(filename, 'w')
    for block in args:
        for line in block:
            f.write(line + "\n")
        f.write('\n')
    f.close()
    return
    

if __name__ == "__main__":
    print(sys.argv)
    sdl_file = sys.argv[1]
    sdlVerbose = False
    if len(sys.argv) > 2: # and sys.argv[3] == "-v":  sdlVerbose = True
        config = sys.argv[2]
        config = config.split('.')[0]

        configModule = __import__(config)
#        print(dir(configModule))
        sdl.masterPubVars = configModule.masterPubVars
        sdl.masterSecVars = configModule.masterSecVars
#        except:
#            print("Could not find module: ", config)
#            sys.exit(-1)
            
    sdl.parseFile2(sdl_file, sdlVerbose)
    main(configModule)
