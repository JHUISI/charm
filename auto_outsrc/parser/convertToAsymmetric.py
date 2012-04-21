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
        exit(0)
    
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

    # TODO: 
    print("<===== Derive Rules =====>")
    rules = deriveRules(info, generators)
    print("<===== Derive Rules =====>\n")

    print("<===== Determine Assignment =====>")
    determineTypeAssignments(rules)
    print("<===== Determine Assignment =====>\n")

    print("<===== Determine Splits =====>")    
    replaceGenerators = deriveSetupGenerators(rules)
    print("<===== Determine Splits =====>\n")
    
    print("<===== Transform Setup =====>")
#    transformSetup()    
    print("<===== Transform Setup =====>\n")    
    

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
            typeI = getVarTypeFromVarName(i, None, True)
#            print("getVarTypeFromVarName:  ", i,":", typeI)
            if typeI == types.NO_TYPE:
                node = BinaryNode(ops.ATTR)
                node.setAttribute(i)
                (funcName , newVarName) = getVarNameFromListIndices(node, True)
                if newVarName != None: 
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


def transformSetup(data):
    pass


if __name__ == "__main__":
    print(sys.argv)
    sdl_file = sys.argv[1]
    sdlVerbose = False
    if len(sys.argv) > 2 and sys.argv[2] == "-v":  sdlVerbose = True
    parseFile2(sdl_file, sdlVerbose)
    retrieveGenList()
