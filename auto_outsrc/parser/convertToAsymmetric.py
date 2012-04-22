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
from SDLParser import *
from outsrctechniques import SubstituteVar, SubstitutePairings

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

def retrieveGenList():
    setting = getAssignInfo()[NONE_FUNC_NAME]['setting'].getAssignNode().right.getAttribute()
    print("setting is", setting)
    if setting != SYMMETRIC_SETTING:
        print("No need to convert to asymmetric setting.\n")
        exit(0) # or continue
    
    setupFuncName = "setup"
    setup = setupFuncName
    (stmtS, typesS, depList, depListNoExp, infList, infListNoExp) = getFuncStmts( setup )
#    (stmtS, typesS, depList, depListNoExp, infList, infListNoExp) = getFuncStmts( setup ) 
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
    pair_vars_G1 = [] # ['C#1', 'C#2', 'C#3', 'C#4', 'C#5', 'C#6', 'C#7', 'E1', 'E2']
    pair_vars_G2 = [] # ['D#1', 'D#2', 'D#3', 'D#4', 'D#5', 'D#6', 'D#7', 'D#7', 'K']
    gpv = GetPairingVariables(pair_vars_G1, pair_vars_G2) 
    decrypt = "decrypt"
    (stmtD, typesD, depListD, depListNoExpD, infListD, infListNoExpD) = getFuncStmts( decrypt )
    lines = stmtD.keys()
    for i in lines:
        if stmtD[i].getHasPairings():
            ASTVisitor( gpv ).preorder( stmtD[i].getAssignNode() )

    print("pair vars LHS:", pair_vars_G1)
    print("pair vars RHS:", pair_vars_G2) 
    info = {}
    info[ 'G1' ] = (pair_vars_G1, assignTraceback(generators, pair_vars_G1))
    info[ 'G2' ] = (pair_vars_G2, assignTraceback(generators, pair_vars_G2))
    info['generators'] = generators 

    # TODO: 
    print("<===== Derive Rules =====>")
    rules = deriveRules(info, generators)
    print("<===== Derive Rules =====>\n")
    print("<===== Determine Assignment =====>")
    info['genMapG1'], info['genMapG2'] = determineTypeAssignments(rules)
    print("<===== Determine Assignment =====>\n")

    print("<===== Determine Splits =====>")    
    replaceGenerators = deriveSetupGenerators(rules)
    print("<===== Determine Splits =====>\n")
    
    info['rules'] = rules
    info['setupGenerators'] = replaceGenerators 
    print("<===== Transform Setup =====>")
    transformSetup(stmtS, info)    
    print("<===== Transform Setup =====>\n")    
    
#    print("info on G1 :=>", info['genMapG1'].keys())
#    print("info on G2 :=>", info['genMapG2'].keys())    

def assignTraceback(generators, listVars):
    varProp = []
    data = {}
    # get variable names from all pairing
    for i in listVars:
        #print("var name := ", i)
        var = i
        buildMap(generators, varProp, var)
        data[i] = set(varProp)
        varProp = []
    
    for i in listVars:
        print("key: ", i, ":=>", data[i])
#    print("varProp for ", listVars[0], ": ", varProp)
    return data

        
def buildMap(generators, varList, var):
    if (not set(var).issubset(generators)):
        (name, varInf) = getVarNameEntryFromAssignInfo(var)
        if(name == None):             
            #print("Var : ", varInf.getVarDepsNoExponents())
            return
        l = varInf.getVarDepsNoExponents()
#        print("var:", var, ", output: ", l)
        # prune 'l' here
        for i in l:
#            print("name: ", i) # uncomment for ckrs09 error
            typeI = getVarTypeFromVarName(i, None, True)
#            print("getVarTypeFromVarName:  ", i,":", typeI)
            if typeI == types.NO_TYPE:
                node = BinaryNode(ops.ATTR)
                node.setAttribute(i)
                (funcName , newVarName) = getVarNameFromListIndices(node, True)
                if newVarName != None: 
                    print("newVarName := ", newVarName)
                    resultVarName = getVarTypeFromVarName(newVarName, None, True)
#                    print("second attempt: ", newVarName, ":", resultVarName)
                    varList.append(newVarName)
                else:
                    varList.append(i)
            elif typeI in [types.G1]:
                varList.append(i)
            elif typeI in [types.str, types.list, types.object]:
                continue
            else:
                pass
#                print("TODO: missing a case in buildMap: ", typeI)
                
#        varList.extend(l)
        varsToCheck = list(l)
        for i in varsToCheck:
            lenBefore = len(varList)
            buildMap(generators, varList, i)
            lenAfter  = len(varList)
            if lenBefore == lenAfter:
                node = BinaryNode(ops.ATTR)
                node.setAttribute(i)
#                print("Node :=>", node)
                (funcName, string) = getVarNameFromListIndices(node, True)
                if string != None: varList.append(string)

            
    return    

# 
def deriveRules(info, generators):
    keyG1, G1data = info[ 'G1' ]
    keyG2, G2data = info [ 'G2' ]
    assert len(keyG1) == len(keyG2), "cannot have an uneven number of pairing lhs and rhs."
    
    rules = []
    for i in range(len(keyG1)):
        list1 = G1data[ keyG1[i] ].intersection( generators )        
        list2 = G2data[ keyG2[i] ].intersection( generators )
#        print("lhs: ", keyG1[i], ":", list1)
#        print("rhs: ", keyG2[i], ":", list2)
        for k in list1:
            for v in list2:
        #        print(k, "!=", v)
                rules.append( (k, v) )
        print()
    # all the rules
    uniqueRules = set(rules)
    print("Rules: ", uniqueRules)
    return uniqueRules

def determineTypeAssignments(rules):
    listG1 = {}
    listG2 = {}
    for l, r in rules:
        # mapping
        listG1[ l ] = str(l + "_G1")
        listG2[ r ] = str(r + "_G2")
        
    print("Left changes: ", listG1)
    print("Right changes: ", listG2)
    return (listG1, listG2)

def deriveSetupGenerators(rules):
    # there should be 
    setupLines = []
    generatorSet = False
    for l, r in rules:
        if l == r:
            print("should be split: ", l, r)
            setupLines.append(l + "_G1 := random(G1)")
            setupLines.append(r + "_G2 := random(G2)")
            newGeneratorL = l
            newGeneratorR = r
            generatorSet = True
            break
        
    
    for l, r in rules:
        if l != r and generatorSet:
            print("generate from split: ", l, r)
            if l == newGeneratorL and r != newGeneratorR:
                newLine = r + " := random(ZR)"
                if not newLine in setupLines:
                    setupLines.append(newLine)
#                newR = r + "_G2 := " + newGeneratorR + "_G2 ^ " + r
            elif l != newGeneratorL and r == newGeneratorR:
                newLine = l + " := random(ZR)"
                if not newLine in setupLines:
                    setupLines.append(newLine)
            else:
                print("generate both sides with new generators:")

    for l, r in rules:
        if l != r and generatorSet:
            if l == newGeneratorL and r != newGeneratorR:
                newLine = r + "_G2 := " + newGeneratorR + "_G2 ^ " + r
                if not newLine in setupLines:
                    setupLines.append(newLine)
            elif l != newGeneratorL and r == newGeneratorR:
                newLine = l + "_G1 := " + newGeneratorL + "_G1 ^ " + l
                if not newLine in setupLines:
                    setupLines.append(newLine)
            else:
                print("determineSplit invalid case!")
    
    print("New Setup: ", setupLines)
    return setupLines

def assignVarOccursInBoth(varName, info):
    varKeysG1 = info['G1'][1].keys()
    varValuesG1 = info['G1'][1]
    varKeysG2 = info['G2'][1].keys()
    varValuesG2 = info['G2'][1]
    
    inG1 = inG2 = False
    for k in varKeysG1:
        if varName in varValuesG1[k]: 
            inG1 = True; break
    for k in varKeysG2:
        if varName in varValuesG2[k]:
            inG2 = True; break
    
    if inG1 == True and inG2 == True: return True    
    return False

def assignVarOccursInG1(varName, info):
    varKeysG1 = info['G1'][1].keys()
    varValuesG1 = info['G1'][1]
    for k in varKeysG1:
        if varName in varValuesG1[k]: 
            return True    
    return False

def assignVarOccursInG2(varName, info):
    varKeysG2 = info['G2'][1].keys()
    varValuesG2 = info['G2'][1]
    for k in varKeysG2:
        if varName in varValuesG2[k]: 
            return True    
    return False

def assignVarIsGenerator(varName, info):
    generatorList = info['generators']
    return varName in generatorList

def updateAllForBoth(node, assignVar, varDeps, info):
    newLine1 = updateAllForG1(node, assignVar, varDeps, info)
    newLine2 = updateAllForG2(node, assignVar, varDeps, info)
    return [newLine1, newLine2]

def updateAllForG1(node, assignVar, varDeps, info):
    new_node2 = BinaryNode.copy(node)
    # 1. assignVar
    new_assignVar = assignVar + "_G1"
    ASTVisitor( SubstituteVar(assignVar, new_assignVar) ).preorder( new_node2 )
    info['genMapG1'][assignVar] = new_assignVar
    for i in varDeps:
        new_i = i + "_G1"
        ASTVisitor( SubstituteVar(i, new_i) ).preorder( new_node2 )
        info['genMapG1'][i] = new_i
    print(" Changed: ", new_node2, end="")
    return str(new_node2)

def updateAllForG2(node, assignVar, varDeps, info):
    new_node2 = BinaryNode.copy(node)
    # 1. assignVar
    new_assignVar = assignVar + "_G2"
    ASTVisitor( SubstituteVar(assignVar, new_assignVar) ).preorder( new_node2 )
    info['genMapG2'][assignVar] = new_assignVar
    for i in varDeps:
        new_i = i + "_G2"
        ASTVisitor( SubstituteVar(i, new_i) ).preorder( new_node2 )
        info['genMapG2'][i] = new_i
    print(" Changed: ", new_node2, end="")
    return str(new_node2)

#updateAllForBoth(node, assignVar, varDeps, )

def updateForLists(varInfo, info):
    newList = []
    inG1 = info['genMapG1'].keys()
    inG1dict = info['genMapG1']
    inG2 = info['genMapG2'].keys()
    inG2dict = info['genMapG2']
    
    orig_list = varInfo.getListNodesList()
    #print("list: ", orig_list)
    for i in orig_list:
        if i in inG1 and i in inG2:
            newList.extend( [inG1dict[i], inG2dict[i]] )
        elif i in inG1:
            newList.append(inG1dict[i])
        elif i in inG2:
            newList.append(inG2dict[i])
        else:
            newList.append(i)
    
    new_node = BinaryNode.copy(varInfo.getAssignNode())
    new_node.right.listNodes = newList
#    print("newList: ", new_node)
    return str(new_node)

def updatForPairing(varInfo, info):    
    node = BinaryNode.copy(varInfo.getAssignNode())
    
    for i in varInfo.getVarDepsNoExponents():
        if i in info['generators']:
            ASTVisitor( SubstitutePairings(i, info['genMapG1'].get(i), 'left')).preorder( node )
            ASTVisitor( SubstitutePairings(i, info['genMapG2'].get(i), 'right')).preorder( node )    
    print(" :=>", node)
    return str(node)

def transformSetup(setupStmts, info):
    # loop through statements and identify two things:
    # generator used in computation
    # AssignVar assignment based on the following logic:
    #   1. if AssignVar occurs in listG1 & listG2: then we need two assignments x_G1 := in blah_G1, x_G2 := in blah_G2
    #   2. if AssignVar occurs just in listG1: then x_G1 := in blah G1
    #   3. if AssignVar occurs just in listG2: then x_G2 := in blah G2 
    setupLines = info['setupGenerators']
    lines = setupStmts.keys()
    for i in lines:
        assign = setupStmts[i].getAssignNode()
        print(i, ":", assign, end="")
        if Type(assign) == ops.EQ:
            assignVar = setupStmts[i].getAssignVar()
            # store for later
            if setupStmts[i].getHasRandomness():
                if not assignVarIsGenerator(assignVar, info):
                    print(" :-> not a generator, so add to setupList.", end="") # do not include in new setup 
                    setupLines.append(str(assign))           
                else:
                    pass
            elif assignVarOccursInBoth(assignVar, info):
                print(" :-> split computation in G1 & G2:", setupStmts[i].getVarDepsNoExponents(), end="")
                setupLines.extend(updateAllForBoth(assign, assignVar, setupStmts[i].getVarDepsNoExponents(), info))
            elif assignVarOccursInG1(assignVar, info):
                print(" :-> just in G1:", setupStmts[i].getVarDepsNoExponents(), end="")
                setupLines.append(updateAllForG1(assign, assignVar, setupStmts[i].getVarDepsNoExponents(), info))
            elif assignVarOccursInG2(assignVar, info):
                print(" :-> just in G2:", setupStmts[i].getVarDepsNoExponents(), end="")
                setupLines.append(updateAllForG2(assign, assignVar, setupStmts[i].getVarDepsNoExponents(), info))                
            elif setupStmts[i].getHasPairings(): # in GT so don't need to touch assignVar
                print(" :-> update pairing.", end="")
                setupLines.append(updatForPairing(setupStmts[i], info))
            elif setupStmts[i].getIsList():
                print(" :-> updating list...", end="")
                setupLines.append(updateForLists(setupStmts[i], info))
                
        print()
        
        print(".....NEW SETUP.....")
        for i in setupLines:
            print(i)

        # update any lists with references to generators or assignVars

if __name__ == "__main__":
    print(sys.argv)
    sdl_file = sys.argv[1]
    sdlVerbose = False
    if len(sys.argv) > 2 and sys.argv[2] == "-v":  sdlVerbose = True
    parseFile2(sdl_file, sdlVerbose)
    retrieveGenList()
