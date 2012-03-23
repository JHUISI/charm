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

def transform(sdl_scheme, verbosity=False):
    parseFile2(sdl_scheme, verbosity)
    partDecCT = { CTprime.T0: None, CTprime.T1: None, CTprime.T2: None }
    print("Building partially decrypted CT: ", partDecCT)
    print("Assign Info =>", assignInfo)
    encrypt_block = assignInfo['encrypt']
    decrypt_block = assignInfo['decrypt']
    protectsM_enc = varsThatProtectM['encrypt']
    protectsM_dec = varsThatProtectM['decrypt']
    
    print("Variables that protect the message:\n")
    print("Encrypt func: ", protectsM_enc)
    print("Decrypt func: ", protectsM_dec)
    print("assignInfo =>", list(decrypt_block.keys()), "\n")
    
    (stmtsEnc, typesEnc, depListEnc, infListEnc) = getFuncStmts("encrypt")
    (stmtsDec, typesDec, depListDec, infListDec) = getFuncStmts("decrypt")

    print("<=== Encrypt ===>") 
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
    T0_sdlObj, T1_sdlObj = createLOC(partDecCT)
    
#    traverseLines(stmtsDec, identifyMessage, ans)
    print("Results =>", partDecCT)
    t1 = partDecCT[CTprime.T1].getAssignVar()
    print("Dep list =>", t1, depListDec[t1])

    # program slice for t1 (including the t1 assignment line)
    t1_slice = {'depList':depListDec[t1], 'lines':[partDecCT[CTprime.T1].getLineNo() ], 'block':decrypt_block }
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

    print("<===\tNew Transform\t===>") 
    traverseForwards(stmtsDec, printStmt, t1_slice)
    print("\t", T0_sdlObj)
    print("\t", T1_sdlObj)
    print("\t output := list{T0, T1}")
    print("<===\tEND\t===>") 
    
            
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
            print("T1: ", assignInfo[targetFunc][i])
            data[CTprime.T1] = assignInfo[targetFunc][i]
        else:
            # TODO: need to create a new assignment for T1 and set to common operation of remaining
            # variables 
            pass

def createLOC(partialCT):
    varName0 = partialCT[CTprime.T0].getAssignNode().left
    
    varName1 = partialCT[CTprime.T1].getAssignNode().left.getAttribute()
    T0, T1 = "T0","T1"
    targetFunc = 'decrypt'    
    T0_node = BinaryNode(ops.EQ)
    T0_node.left = BinaryNode(T0)
    T0_node.right = varName0
    
    T1_node = BinaryNode(ops.EQ)
    T1_node.left = BinaryNode(T1)
    T1_node.right = assignInfo[targetFunc][varName1].getAssignNode().left

    return T0_node, T1_node

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
    file = sys.argv[1]
    sdlVerbose = False
    if len(sys.argv) > 2 and sys.argv[2] == "-v":  sdlVerbose = True
    transform(file, sdlVerbose)
    print("\n")
    
    
