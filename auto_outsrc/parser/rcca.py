from SDLParser import *
from outsrctechniques import AbstractTechnique,Technique1,Technique2,Technique3,FindT1,SubstituteVar
from transform import CTprime, transform, traverseForwards, traverseBackwards
import config
import sys


def addVarToInputOfFunc(varName, targetVar, funcName):
    AssignInfo = getAssignInfo()
    block = AssignInfo[funcName]
    lineNo = getLineNoOfInputStatement(funcName)
    (stmts, types, depList, infList) = getFuncStmts(funcName)
    
    inputLine = stmts[lineNo].getAssignNode().right
    
    if Type(inputLine) == ops.LIST and targetVar in inputLine.listNodes:
        print("Found it...")
        targetVarObj = block[targetVar]
        targetList = targetVarObj.getAssignNode().right
        if Type(targetList) == ops.EXPAND: 
            targetList.addToList(varName)
            newLine = str(targetVarObj.getAssignNode()) + "\n"
            replaceLineNo = targetVarObj.getLineNo()
            substituteOneLineOfCode(newLine, replaceLineNo)            
        else:
            print("addVarToInputOfFunc: targetVar not of EXPAND type: ", varName, targetVar, funcName)
            sys.exit(-1)
    else:
        print("addVarToInputOfFunc: input of %s not of LIST type. Please fix in SDL" % funcName)
        sys.exit(-1)

def addVarToOutputOfFunc(varName, funcName):
    AssignInfo = getAssignInfo()
    block = AssignInfo[funcName]
    lineNo = getLineNoOfOutputStatement(funcName)
    (stmts, types, depList, infList) = getFuncStmts(funcName)
    outputLine = stmts[lineNo].getAssignNode().right
    
    if Type(outputLine) == ops.ATTR:
        # get assignment for this attribute
        cipherName = outputLine.getAttribute()
        ciphertext = block[cipherName]
        replacelineNo = ciphertext.getLineNo()
        node = ciphertext.getAssignNode().right
        if Type(node) == ops.LIST: node.addToList(varName)
        # result after adding variable to list node        
#        print("result: ", ciphertext.getAssignNode())
        newLine = str(ciphertext.getAssignNode()) + "\n"
    else:
        print("addVarToOutputOfFunc: expected output line in", funcName,"to be a ATTR variable node. Please fix.")
        sys.exit(-1)
    
    # update the line of code
    print("Adding new line :=>", newLine)
    print("replacing this line: ", replacelineNo)
    substituteOneLineOfCode(newLine, replacelineNo)
    return cipherName

def rcca(var_info):
    encFunc = "encrypt"
    setupFunc = "setup"
    transformFunc = config.transformFunctionName
    (stmtsEnc, typesEnc, depListEnc, infListEnc) = getFuncStmts(encFunc)
    message = config.M # user-configured message
    
    myAssignInfo = getAssignInfo()
    enc_block  = myAssignInfo[encFunc]
    varsForDec = {'s':None, 's_type':None, 'dec_op':var_info['dec_op'] }

#    other_block = myAssignInfo[setupFunc]
#    print("Message type : ", typesEnc)
#    how do I get the type of config.M
    
    # must ensure order of operations occurs as expected e.g., shouldn't be possible to perform computation
    # with s, then define 's' for first time --> See hibe04
    print("\n<=== Encrypt ===>") 
    linesEnc = list(stmtsEnc.keys())
    linesEnc.sort()
    for i in linesEnc:
        print(i, ": ", stmtsEnc[i].getAssignNode())      
        if stmtsEnc[i].getProtectsM():
            n = stmtsEnc[i].getAssignNode()
            msgProtLineNo = stmtsEnc[i].getLineNo()
            vars = list(stmtsEnc[i].getVarDeps())
            vars.remove(message)
            print("\t=> protects message!")
            print("\t=> assign node : T0 :=>", n.left)
            print("\t=> deps : ", vars)
            # build up assignments of var deps in encrypt
            depAssign = []
            lineDepRef = {}
            for j in vars:
                if enc_block.get(j): 
                    lineStmt = str(enc_block[j].getAssignNode() )
                    lineDepRef[ lineStmt ] = enc_block[j].getLineNo()
                 
            for j in vars: 
                if enc_block.get(j) != None and enc_block[j].getHasRandomness():
                    remLine = str(enc_block[j].getAssignNode() )
                    del(lineDepRef[remLine])

                    lineNo = enc_block[j].getLineNo()
                    randomLine = config.rccaRandomVar + " := random(%s)\n" % var_info[config.M]
                    # build up data structure for generating dec_out SDL
                    varsForDec['s'] = j
                    varsForDec['session_key'] = j + '_sesskey'
                    varsForDec['s_type'] = str(typesEnc[j].getType())                    
                    # replaces encrypt randomness or 's' symbolically
                    sLine   = j + " := H(list{" + config.rccaRandomVar + "," + message + "}," + varsForDec['s_type'] + ")\n" 
                    remCode = [msgProtLineNo, lineNo] + list(lineDepRef.values()) 
                    removeFromLinesOfCode(remCode)
                    print("Randomness :=>", enc_block[j].getAssignNode())
                    ASTVisitor( SubstituteVar(message, config.rccaRandomVar) ).preorder( n ) 
                    # line for hashing 'r' into a session key 
                    rLine = varsForDec['session_key'] + " := SHA1(" + config.rccaRandomVar + ")\n"
                    t1Line = "T1 := SymEnc(" + varsForDec['session_key'] + " , " + message + ")\n"
                    protectMsgLine = str(n) + "\n"
                    # figure out if there are any statements that need to be computed before protecting
                    # the message in str(n)
                    addCode = []
                    if len(lineDepRef.keys()) > 0:
                        addCode = list(lineDepRef.keys())
                    addCode.extend([randomLine, sLine, rLine, protectMsgLine])
                    appendToLinesOfCode(addCode, lineNo)                    
                    # fix final output for encrypt
                    outputLineNo = getLineNoOfOutputStatement(encFunc)
                    outputStmt = stmtsEnc[outputLineNo]
                    appendToLinesOfCode([t1Line], outputLineNo)

                    parseLinesOfCode(getLinesOfCode(), True)
                    cipherInEnc = addVarToOutputOfFunc('T1', encFunc)
                    addVarToInputOfFunc('T1', cipherInEnc, transformFunc)
                    break # analysis is done
                elif infListEnc.get(j) != None and set(config.keygenPubVar).intersection(infListEnc.get(j)):                        
                    # checking whether variable inside j is influenced by the public variable of the scheme 
                    print("public key influences", j, ":=>", infListEnc[j])
                    varsForDec['pk_value'] = j
                elif enc_block.get(j) != None:  
                    # want to determine whether 'pk' influences particular variable by
                    # checking if an assignment exists in the current block that has is influenced by pk
                    for i in enc_block.get(j).getVarDeps():
                        if set(config.keygenPubVar).intersection(infListEnc.get(i)):
                            # successfully traced it back to public values in scheme
                            varsForDec['pk_value'] = j                      
                            break
                    

    print("<=== END ===>")    
    # update the type info for 'M'
    sdl_types      = myAssignInfo["types"]
    M_varinfo = sdl_types[config.M]
    new_M_type = config.M + ":= str" 
    MLineNo = M_varinfo.getLineNo()
    substituteOneLineOfCode(new_M_type, MLineNo)
    
    parseLinesOfCode(getLinesOfCode(), False)
    newLinesOfSDL = rcca_decout(varsForDec)
    # append lines to the last line of SDL
    lastLineNo = len(getLinesOfCode()) + 1
    appendToLinesOfCode(newLinesOfSDL, lastLineNo)
    parseLinesOfCode(getLinesOfCode(), True)

def rcca_decout(vars):
    decout_sdl = ["\n","BEGIN :: func:%s\n" % config.decOutFunctionName,
"input := list{%s, %s, %s}\n" % (config.partialCT, config.keygenBlindingExponent, vars['pk_value']),
"%s := expand{T0, T1, T2}\n" % config.partialCT,
"%s := T0 %s (T2^%s)\n" % (config.rccaRandomVar, vars['dec_op'], config.keygenBlindingExponent), # recover R
"%s := SHA1( %s )\n" % (vars['session_key'], config.rccaRandomVar), # recover session key
"%s := SymDec(%s, T1)\n" % (config.M, vars['session_key']), # use session key to recover M
"%s := H(list{R, M}, %s)\n" % (vars['s'], vars['s_type']), # recover 'randomness' calculated for encrypt
"BEGIN :: if\n",
"if { (T0 == (%s * (%s ^ %s))) and (T2 == (%s * (%s ^ (%s / %s)))) }\n" 
% (config.rccaRandomVar, vars['pk_value'], vars['s'], config.rccaRandomVar, vars['pk_value'], vars['s'], config.keygenBlindingExponent), # verify T0 and T1 are well-formed
"output := %s\n" % config.M,
"else\n",
"error('invalid ciphertext')\n",
"END :: if\n",
"END :: func:%s\n" % config.decOutFunctionName]
    return decout_sdl

if __name__ == "__main__":
    sdl_file = sys.argv[1]
    sdlVerbose = False
    if len(sys.argv) > 2 and sys.argv[2] == "-v":  sdlVerbose = True
    parseFile2(sdl_file, sdlVerbose)
    keygenVarList, var_info = transform(sdlVerbose)
    rcca(var_info)
    
    
    print("\n")
