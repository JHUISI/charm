from SDLParser import *
import sys


# 1. Get the assignment that protects the message in encrypt
# 2. find this variable in the decrypt routine and retrieve a program slice that affects M (potentially the entire routine)
# 3. identify all the lines that perform pairings in that slice of decrypt
# 4. try our best to combine pairings where appropriate then apply rewriting rules to move as much info into pairing as possible
# 5. iterate through each pairing line and move things in distribute so that they all look like this: e(a^b, c^d) * e(e^f,g^h) * ...

def transform(sdl_scheme):
    parseFile2(sdl_scheme)
    getVarsThatProtectM()
    printFinalOutput()
    encrypt_block = assignInfo['encrypt']
    decrypt_block = assignInfo['decrypt']
    protectsM_enc = varsThatProtectM['encrypt']
    protectsM_dec = varsThatProtectM['decrypt']
    
    print("Variables that protect the message:\n")
    print("Encrypt func: ", protectsM_enc)
    print("Decrypt func: ", protectsM_dec)
    print("assignInfo =>", encrypt_block)    
    (stmtsEnc, typesEnc) = getFuncStmts("encrypt")
    (stmtsDec, typesDec) = getFuncStmts("decrypt")   

    print("<=== Encrypt ===>") 
    # first step is to identify message and how its protected   
    linesEnc = list(stmtsEnc.keys())
    linesEnc.sort()
    for i in linesEnc:
        print(i, ": ", stmtsEnc[i].getAssignNode())      
        if stmtsEnc[i].getProtectsM():
            n = stmtsEnc[i].getAssignNode()
            print("\t=> protects message!")
            print("\t=> assign node: ", n.left)
    print("<=== END ===>")
    
    print("<=== Decrypt ===>")    
    linesDec = list(stmtsDec.keys())
    linesDec.sort()
    for i in linesDec:
        print(i, ": ", stmtsDec[i].getAssignNode())
        if stmtsDec[i].getHasPairings():
            print("\t=> has pairings True!")
        elif stmtsDec[i].getProtectsM():
            print("\t=> protects message!")
    print("<=== END ===>")
    
if __name__ == "__main__":
    file = sys.argv[1]
    transform(file)
#    parseFile2(sys.argv[1])
#    getVarsThatProtectM()
#    encrypt_block = assignInfo['encrypt']
#    decrypt_block = assignInfo['decrypt']
#    protectsM_enc = varsThatProtectM['encrypt']
#    protectsM_dec = varsThatProtectM['decrypt']
#    
#    print("Variables that protect the message:\n")
#    print("Encrypt func: ", protectsM_enc)
#    print("Decrypt func: ", protectsM_dec)
#    print("assignInfo =>", encrypt_block)
    
    
    print("\n")
    
    
