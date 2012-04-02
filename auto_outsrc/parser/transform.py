from SDLParser import *
from outsrctechniques import AbstractTechnique,Technique1,Technique2,Technique3,FindT1
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
    secret = config.keygenSecVar
    # secret = str(stmtsKg[outputKgLine].getAssignNode().right)
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
    
    traverseBackwards(stmtsDec, identifyT2, partDecCT)
    T0_sdlObj, T2_sdlObj, output_sdlObj, transform_output_sdlObj = createLOC(partDecCT)
    
#    traverseLines(stmtsDec, identifyMessage, ans)
    print("Results =>", partDecCT)
    t2 = partDecCT[CTprime.T2].getAssignVar()
    if t2 == "T2": # in other words, this is something we just added to dec, then 
        print("Dep list =>", t2)
        depListDec[t2] = partDecCT[CTprime.T2].getVarDeps()
        print("new dep list for t1 :=>", depListDec[t2])
    else:
        print("Dep list for non T1 case =>", t2, depListDec[t2])

    # program slice for t1 (including the t1 assignment line)
    last_line = partDecCT[CTprime.T2].getLineNo()
    t2_slice = {'depList':depListDec[t2], 'lines':[last_line], 'block':decrypt_block }
    traverseBackwards(stmtsDec, programSliceT2, t2_slice)
    t2_slice['lines'].sort()
    transform = t2_slice['lines']
    print("Optimize these lines: ", transform) 
    print("<===\tTransform Slice\t===>") 
    traverseForwards(stmtsDec, printStmt, t2_slice)
    print("<===\tEND\t===>") 

    # rewrite pairing equations 
    print("Rewrite pairing equations....")   
    traverseBackwards(stmtsDec, applyRules, t2_slice)
    
    allLines = getLinesOfCode()
    last_line = len(allLines) + 1
    cur_line = last_line
    
    transformVarInfos = [ ]
    transformVarInfos.extend(t2_slice['lines'])
    print("Current transform LOCs: ", transformVarInfos)

    # add statements to new transform block
    traverseForwards(stmtsDec, printStmt, t2_slice)


    # get function prologue for decrypt
    transformIntro = "BEGIN :: func:%s" % config.transformFunctionName
    cur_list = ["", transformIntro]
    startLineNo = getLineNoOfInputStatement("decrypt")
    endLineNo   = getLineNoOfOutputStatement("decrypt")
    intro = list(range(startLineNo, transformVarInfos[0]))
    transformVarInfos = intro + transformVarInfos
    print("New LOCs: ", intro) 
    transformOutro = "END :: func:%s" % config.transformFunctionName
    
    print("Delete these lines: ", transformVarInfos)
    
    newObj = [T0_sdlObj, T2_sdlObj, output_sdlObj, transform_output_sdlObj]
    newFunc = config.transformFunctionName # 'transform' string
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
        if newObj[o] != None:
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

def programSliceT2(varInf, data):
    depList = data['depList']
    if varInf.getAssignVar() in depList:
        data['lines'].append(varInf.getLineNo())
    elif varInf.getVarDeps() in depList:
        data['lines'].append(varInf.getLineNo())

#def depCheck(varInf, data):
#    target

def identifyT2(varInf, data):
    targetFunc = 'decrypt'
    s = varInf.getAssignNode()
    if s.left.getAttribute() == 'output': 
        data['msg'] = s.right.getAttribute()
    elif data.get('msg') == s.left.getAttribute(): 
        print("Found it: ", s, varInf.varDeps) # I want non-T0 var
        t0_varname = data[CTprime.T0].getAssignNode().left.getAttribute()
        t2_varname = list(varInf.varDeps)
        t2_varname.remove(t0_varname)
        print("T0 :=>", t0_varname, t2_varname, varInf.varDeps)
        if len(t2_varname) == 1:
            # M := T0 / T1 form
            i = t2_varname[0]
            print("T2: ", AssignInfo[targetFunc][i])
            data[CTprime.T2] = AssignInfo[targetFunc][i]
        else:
            # TODO: need to create a new assignment for T1 and set to common operation of remaining
            # variables
            copy_s = BinaryNode.copy(s.right)
            # find and exlcude T0
            findT1 = FindT1(t0_varname)
            ASTVisitor( findT1 ).preorder( copy_s )
            # create new stmt "T1 := operations" 
            t2_node = BinaryNode(ops.EQ, BinaryNode("T2"), findT1.T1)
            # merge changes back into original line with M
            t2_vi = varInf
            t2_vi.updateAssignNode(t2_node)
            t2_vi.getVarDeps().remove(t0_varname)
#            print("t1_vi =>>>", t1_vi.getVarDeps())
            data[CTprime.T2] = t2_vi

def createLOC(partialCT):
    varName0 = partialCT[CTprime.T0].getAssignNode().left
    
    T0, T1, T2 = "T0", "T1", "T2"
    targetFunc = 'decrypt'    
    partialCiphertextName = config.partialCT
    T0_node = BinaryNode(ops.EQ)
    T0_node.left = BinaryNode(T0)
    T0_node.right = varName0
    
    T2_node = None    
    varName1 = partialCT[CTprime.T2].getAssignNode().left.getAttribute()
    print("varName1 :=>", varName1)
    if varName1 != T2:
        T2_node = BinaryNode(ops.EQ)
        T2_node.left = BinaryNode(T2)
        T2_node.right = AssignInfo[targetFunc][varName1].getAssignNode().left
        print("T2 node :=", T2_node)
        
    output_node = BinaryNode(ops.EQ)
    output_node.left = BinaryNode(partialCiphertextName)
    output_node.right = BinaryNode(ops.LIST)
    output_node.right.listNodes = [T0, T1, T2]
    
    transform_output = BinaryNode(ops.EQ)
    transform_output.left = BinaryNode("output")
    transform_output.right = BinaryNode(partialCiphertextName) 
    
    return T0_node, T2_node, output_node, transform_output

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
    
    
