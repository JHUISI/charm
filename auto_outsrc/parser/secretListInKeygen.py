from SDLParser import *
import sys

debug = False

def getSecretList(config, verbose=False):
    global AssignInfo
    AssignInfo = getAssignInfo()

#    encrypt_block = AssignInfo['encrypt']
    decrypt_block = AssignInfo['decrypt']
    # 1 get output line for keygen
    # 2 get the reference and list definition (e.g., vars of secret key)
    # 3 see which ones appear in transform and mark them as needing to be blinded
    keygen = config.keygenFuncName
    (stmtsKg, typesKg, depListKg, depListKgNoExponents, infListKg, infListKgNoExponents) = getFuncStmts(keygen)
    outputKgLine = getLineNoOfOutputStatement(keygen)
    secret = config.keygenSecVar
    # secret = str(stmtsKg[outputKgLine].getAssignNode().right)
    #print("output :=>", secret)
    secretVars = AssignInfo[keygen][secret].getAssignNode().right
    #print("list :=>", secretVars.listNodes)

    if Type(secretVars) == ops.LIST:
        secretList = secretVars.listNodes
    elif Type(secretVars) == ops.ATTR:
        secretList = [str(secretVars)]
    else:
        sys.exit("ERROR: invalid structure definition in", keygen)
    
    (stmtsEnc, typesEnc, depListEnc, depListEncNoExponents, infListEnc, infListEncNoExponents) = getFuncStmts("encrypt")
    (stmtsDec, typesDec, depListDec, depListDecNoExponents, infListDec, infListDecNoExponents) = getFuncStmts("decrypt")

    finalSecretList = []
    for i in secretList:
        for k,v in depListDec.items():
            if  i in v: finalSecretList.append(i); break
    #print("INFO: Variables in Keygen that need to be blinded: ", finalSecretList)
    return finalSecretList

if __name__ == "__main__":
    print(sys.argv)
    config = __import__('config') # better way to import configuration files dynamically
    if len(sys.argv) == 1: sys.exit("ERROR: please supply an SDL file.")
    sdl_file = sys.argv[1]
    sdlVerbose = False
    if len(sys.argv) > 2 and sys.argv[2] == "-v":  sdlVerbose = True
    parseFile2(sdl_file, sdlVerbose)
    keygenVarList = getSecretList(config, sdlVerbose)
    print("\n")
