from SDLParser import *
from outsrctechniques import AbstractTechnique,Technique1,Technique2,Technique3
import config
import sys

CTprime = Enum('T0', 'T1', 'T2') # T2 is for RCCA security

techMap = {1:Technique1, 2:Technique2, 3:Technique3}
debug = False

# 1. Get the assignment that protects the message in encrypt
# 2. find this variable in the decrypt routine and retrieve a program slice that affects M (potentially the entire routine)
# 3. identify all the lines that perform pairings in that slice of decrypt
# 4. try our best to combine pairings where appropriate then apply rewriting rules to move as much info into pairing as possible
# 5. iterate through each pairing line and move things in distribute so that they all look like this: e(a^b, c^d) * e(e^f,g^h) * ...

# description: should return a list of VarObjects that make up the new
# 
def transform(sdl_scheme, verbosity=False):
    global AssignInfo
    partDecCT = { CTprime.T0: None, CTprime.T1: None, CTprime.T2: None }
    print("Building partially decrypted CT: ", partDecCT)
    AssignInfo = getAssignInfo()

#    encrypt_block = AssignInfo['encrypt']
    decrypt_block = AssignInfo['decrypt']
    # 1 get output line for keygen 
    # 2 get the reference and list definition (e.g., vars of secret key)
    # 3 see which ones appear in transform and mark them as needing to be blinded
    keygen = "keygen"
    (stmtsKg, typesKg, depListKg, infListKg) = getFuncStmts(keygen)
    outputKgLine = getLineNoOfOutputStatement(keygen)
    secret = str(stmtsKg[outputKgLine].getAssignNode().right)
    print("output :=>", secret)
    secretVars = AssignInfo[keygen][secret].getAssignNode().right
    print("list :=>", secretVars.listNodes)
    if Type(secretVars) == ops.LIST:
        secretList = secretVars.listNodes
    elif Type(secretVars) == ops.ATTR:
        secretList = [secretVars]
    else:
        sys.exit("ERROR: invalid structure definition in", keygen)    
    
    (stmtsEnc, typesEnc, depListEnc, infListEnc) = getFuncStmts("encrypt")
    (stmtsDec, typesDec, depListDec, infListDec) = getFuncStmts("decrypt")
    finalSecretList = []
    for i in secretList:
        for k,v in depListDec.items():
            if  i in v: finalSecretList.append(i); break
    
    print("INFO: Variables in Keygen that need to be blinded: ", finalSecretList)

    print("\n<=== Encrypt ===>") 
    # first step is to identify message and how its protected   
    t0_var = None
    linesEnc = list(stmtsEnc.keys())
    linesEnc.sort()
    for i in linesEnc:
        print(i, ": ", stmtsEnc[i].getAssignNode())      
        if stmtsEnc[i].getProtectsM():
            n = stmtsEnc[i].getAssignNode()
            print("\t=> protects message!")
            print("\t=> assign node : T0 :=>", n.left)
            t0_var = stmtsEnc[i]
            partDecCT[CTprime.T0] = stmtsEnc[i] # record T0
            print("\t=> object: ", t0_var.getAssignVar(), t0_var.getVarDeps())
        if stmtsEnc[i].getHasRandomness():
            print("\t=> has randomness!")
    print("<=== END ===>")
    
    traverseBackwards(stmtsDec, identifyT1, partDecCT)
    T0_sdlObj, T1_sdlObj, output_sdlObj, transform_output_sdlObj = createLOC(partDecCT)
    
#    traverseLines(stmtsDec, identifyMessage, ans)
    print("Results =>", partDecCT)
    t1 = partDecCT[CTprime.T1].getAssignVar()
    print("Dep list =>", t1, depListDec[t1])

    # program slice for t1 (including the t1 assignment line)
    last_line = partDecCT[CTprime.T1].getLineNo()
    t1_slice = {'depList':depListDec[t1], 'lines':[last_line], 'block':decrypt_block }
    traverseBackwards(stmtsDec, programSliceT1, t1_slice)
    t1_slice['lines'].sort()
    transform = t1_slice['lines']
    print("Optimize these lines: ", transform) 
    print("<===\tTransform Slice\t===>") 
    traverseForwards(stmtsDec, printStmt, t1_slice)
    print("<===\tEND\t===>") 

    # rewrite pairing equations 
    print("Rewrite pairing equations....")   
    traverseBackwards(stmtsDec, applyRules, t1_slice)
    
    allLines = getLinesOfCode()
    last_line = len(allLines) + 1
    cur_line = last_line
    
    transformVarInfos = [ ]
    transformVarInfos.extend(t1_slice['lines'])
    print("Current transform LOCs: ", transformVarInfos)

    # add statements to new transform block
    traverseForwards(stmtsDec, printStmt, t1_slice)


    # get function prologue for decrypt
    transformIntro = "BEGIN :: func:transform"
    cur_list = [transformIntro]
    startLineNo = getLineNoOfInputStatement("decrypt")
    endLineNo   = getLineNoOfOutputStatement("decrypt")
    intro = list(range(startLineNo, transformVarInfos[0]))
    transformVarInfos = intro + transformVarInfos
    print("New LOCs: ", intro) 
    transformOutro = "END :: func:transform"
    
    print("Delete these lines: ", transformVarInfos)
    
    newObj = [T0_sdlObj, T1_sdlObj, output_sdlObj, transform_output_sdlObj]
    newFunc = 'transform'
#    AssignInfo[newFunc] = {}
    for i in range(len(transformVarInfos)):
        ref = transformVarInfos[i]
        if stmtsDec.get(ref):
            cur_list.append(str(stmtsDec[ref].getAssignNode()))
            cur_line += 1
#            varName = stmtsDec[ref].getAssignVar()
#            newVF   = VarInfo.copy(stmtsDec[ref])
            #print("new lines :=>\t", cur_line, newVF.getAssignNode())
#            newVF.setLineNo(cur_line)
#            AssignInfo[newFunc][varName] = newVF
    
    for o in range(len(newObj)):
       c = cur_line + o
       transformVarInfos.append(c)
       cur_list.append(str(newObj[o]))
#       varInfo = createVarInfo(c, newObj[o], newFunc)
#       varName = varInfo.getAssignVar()
#       AssignInfo[newFunc][varName] = varInfo
#       cur_list.append(str(varInfo.getAssignNode()))
       
    cur_list.append(transformOutro)
    appendToLinesOfCode(cur_list, last_line)
    removeRangeFromLinesOfCode(startLineNo, endLineNo)
    
    parseLinesOfCode(getLinesOfCode(), False)
    # Confirm that transform was added correctly by retrieving its statements 
    (stmtsTrans, typesTrans, depListTrans, infListTrans) = getFuncStmts(newFunc)

    newLines = list(stmtsTrans.keys())
    newLines.sort()
    print("<===\tNew Transform\t===>") 
    for i in newLines:
        print(i, ":", stmtsTrans[i].getAssignNode())    
    print("<===\tEND\t===>") 
    
    return finalSecretList

def createVarInfo(i, node, currentFuncName):
    varInfoObj = VarInfo()
    varInfoObj.setLineNo(i)
    varInfoObj.setAssignNode(node, currentFuncName, None)
    
    return varInfoObj
            
def applyRules(varInf, data):
    if varInf.getHasPairings():
        equation = varInf.getAssignNode()
        print("Found pairing: ", equation)
        code_block = data.get('block')
        path = []
        new_equation = Optimize(equation, path, code_block)
        varInf.updateAssignNode(new_equation)
            
def printStmt(varInf, data):
    if varInf.getLineNo() in data['lines']:
        print(varInf.getLineNo(), ":", varInf.getAssignNode())

def programSliceT1(varInf, data):
    depList = data['depList']
    if varInf.getAssignVar() in depList:
        data['lines'].append(varInf.getLineNo())
    elif varInf.getVarDeps() in depList:
        data['lines'].append(varInf.getLineNo())

#def depCheck(varInf, data):
#    target

def identifyT1(varInf, data):
    targetFunc = 'decrypt'
    s = varInf.getAssignNode()
    if s.left.getAttribute() == 'output': 
        data['msg'] = s.right.getAttribute()
    elif data.get('msg') == s.left.getAttribute(): 
        print("Found it: ", s, varInf.varDeps) # I want non-T0 var
        t0_varname = data[CTprime.T0].getAssignNode().left.getAttribute()
        t1_varname = list(varInf.varDeps)
        t1_varname.remove(t0_varname)
        print("T0 :=>", t0_varname, t1_varname, varInf.varDeps)
        if len(t1_varname) == 1:
            # M := T0 / T1 form
            i = t1_varname[0]
            print("T1: ", AssignInfo[targetFunc][i])
            data[CTprime.T1] = AssignInfo[targetFunc][i]
        else:
            # TODO: need to create a new assignment for T1 and set to common operation of remaining
            # variables 
            pass

def createLOC(partialCT):
    varName0 = partialCT[CTprime.T0].getAssignNode().left
    
    varName1 = partialCT[CTprime.T1].getAssignNode().left.getAttribute()
    T0, T1 = "T0","T1"
    targetFunc = 'decrypt'    
    partialCiphertextName = 'ct_pr' # maybe search for a unique name
    T0_node = BinaryNode(ops.EQ)
    T0_node.left = BinaryNode(T0)
    T0_node.right = varName0
    
    T1_node = BinaryNode(ops.EQ)
    T1_node.left = BinaryNode(T1)
    T1_node.right = AssignInfo[targetFunc][varName1].getAssignNode().left

    output_node = BinaryNode(ops.EQ)
    output_node.left = BinaryNode(partialCiphertextName)
    output_node.right = BinaryNode(ops.LIST)
    output_node.right.listNodes = [T0, T1]
    
    transform_output = BinaryNode(ops.EQ)
    transform_output.left = BinaryNode("output")
    transform_output.right = BinaryNode(partialCiphertextName) 
    
    return T0_node, T1_node, output_node, transform_output

def printHasPair(varInf, data):
    if varInf.getHasPairings():
        print("Found pairings: ", varInf.getAssignNode())

def traverseForwards(stmts, funcToCall, dataObj=None):
    assert type(stmts) == dict, "invalid stmt object!"
    lines = list(stmts.keys())
    lines.sort()
    if not dataObj: dataObj = {}
    for i in lines:
        funcToCall(stmts[i], dataObj)
    return dataObj


def traverseBackwards(stmts, funcToCall, dataObj=None):
    assert type(stmts) == dict, "invalid stmt object!"
    lines = list(stmts.keys())
    lines.sort()
    lines.reverse()
    if not dataObj: dataObj = {}
    for i in lines:
        funcToCall(stmts[i], dataObj)
    return dataObj

# figures out which optimizations apply
def Optimize(equation, path, code_block=None):
    tech_list = [1, 2, 3]
    # 1. apply the start technique to equation
    new_eq = equation
    while True:
        cur_tech = tech_list.pop()
        if debug: print("Testing technique: ", cur_tech)
        (tech, new_eq) = testTechnique(cur_tech, new_eq, code_block)
        
        if tech.applied:
            if debug: print("Technique ", cur_tech, " successfully applied.")
            path.append(cur_tech)
            tech_list = [1, 2, 3]
            continue
        else:
            if len(tech_list) == 0: break
    print("path: ", path)
    print("optimized equation: ", new_eq)
    return new_eq        
        

def testTechnique(tech_option, equation, code_block=None):
    eq2 = BinaryNode.copy(equation)
        
    tech = None
    if tech_option in techMap.keys():
        tech = techMap[tech_option](code_block)
    else:
        return None
        
    # traverse equation with the specified technique
    ASTVisitor(tech).preorder(eq2)

    # return the results
    return (tech, eq2)

    
if __name__ == "__main__":
    print(sys.argv)
    sdl_file = sys.argv[1]
    sdlVerbose = False
    if len(sys.argv) > 2 and sys.argv[2] == "-v":  sdlVerbose = True
    parseFile2(sdl_file, sdlVerbose)
    keygenVarList = transform(sdlVerbose)
    print("\n")
    
    
