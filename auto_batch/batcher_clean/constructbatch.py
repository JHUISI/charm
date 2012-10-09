import sdlpath
from sdlparser.SDLParser import *
from batchoptimizer import SubstituteSigDotProds, SubstituteAttr, DropIndexForPrecomputes
from batchconfig import *

#JAA: notes - updates types structure and fill in precompute / dotCache computations

membership_check = """\n
BEGIN :: if
if { ismember(%s) == False }
    output := False
END :: if"""

membership_header = """
BEGIN :: func:membership
 input := list{%s}
"""
membership_footer = """\n
 output := True
END :: func:membership\n
"""


# delta, dotACache, dotBCache, startSigNum, endSigNum, incorrectIndices, pk, Mlist, siglist, g (e.g)
dc_header = """
BEGIN :: func:dividenconquer
 input := list{%s}
"""
dc_footer = """
 output := None
END ::func:dividenconquer\n
"""
dc_dot_loopVal_begin_for = """
BEGIN :: for
for{%s := startSigNum, endSigNum}\n"""
# dotALoopVal := dotALoopVal * dotACache#z
# dotBLoopVal := dotBLoopVal * dotBCache#z
end_for_loop = """END :: for"""

dc_batch_verify_check = """
BEGIN :: if
 if { %s }
    return := None
 else
    midwayFloat := ((endSigNum - startSigNum) / 2)
    midway := integer(midwayFloat)
END :: if\n
"""

dc_recursive_call = """
BEGIN :: if
 if { midway == 0 } 
    addToList(incorrectIndices, startSigNum)
    output := None
 else
    midSigNum := startSigNum + midway
    dividenconquer(%s)
    dividenconquer(%s)
END :: if\n
"""

defaultBatchTypes = {"delta" : "list{ZR}",
"incorrectIndices" : "list{int}",
"startSigNum" : "int",
"endSigNum " : "int"}
                 
secparamLine = ""

membership_test = """
BEGIN :: if\n
  if {(membership(%s)) == False)}\n
     output := False\n
END :: if\n
"""

sigForLoop = """
BEGIN :: for
for{%s := 0, %s}
"""

batch_verify_header = """
BEGIN :: func:batchverify
input := list{%s, incorrectIndices}
%s delta#z := SmallExp(secparam)
END :: for

BEGIN :: if
 if {(membership(%s) == False)}
     output := False
END :: if\n
"""

batch_verify_body = """# precompute lines 
# dotCache computations
"""

# replace startSigNum with 0, and endSigNum with N.
batch_verify_footer = """
 dividenconquer(%s)

 output := incorrectIndices
END ::func:batchverify\n
"""

SPACES = ' '
sigIterator = 'z'
signerIterator = 'y'

def Filter(node):
    return node.sdl_print()

class SDLBatch:
    def __init__(self, sdlOutfile, sdlData, varTypes, finalSdlBatchEq, precompDict, variableCount=0):
        self.sdlOutfile = sdlOutfile
        self.sdlData = sdlData
        self.varTypes = varTypes
        self.precomputeDict = precompDict
        self.precomputeVarList = []
        for i in list(precompDict.keys()):
            if str(i) != 'delta': self.precomputeVarList.append(i.getAttribute())
        self.finalBatchEq = BinaryNode.copy(finalSdlBatchEq)
        self.variableCount = variableCount
        self.debug = False
        
    def ReplaceAppropArgs(self, map, forLoopIndex, node):
        sa = SubstituteAttr(map, forLoopIndex)
        eq = BinaryNode.copy(node)
        ASTVisitor(sa).preorder(eq)
        dp = DropIndexForPrecomputes(self.precomputeVarList, forLoopIndex)
        ASTVisitor(dp).preorder(eq)
        return Filter(eq)
        
    def __generateMembershipTest(self, verifyArgList):
        output = ""
        verifyArgs = str(list(verifyArgList)).replace("[", '').replace("]",'').replace("'", '')
        output += membership_header % verifyArgs
        for eachArg in verifyArgList:
            output += membership_check % eachArg
        output += membership_footer 
        if self.debug: 
            print("Membership Test :=>")
            print(output)
        return output
    
    def __generateTypes(self, dotLoopValTypesSig, dotCacheTypesSig, verifyArgTypes):
        output = []
        typeSdlFormat = "%s := %s\n"
        for i,j in defaultBatchTypes.items():
            output.append(typeSdlFormat % (i, j))
        for i,j in dotLoopValTypesSig.items():
            output.append(typeSdlFormat % (i, j))
        for i,j in dotCacheTypesSig.items():
            output.append(typeSdlFormat % (i, j))
        for i,j in verifyArgTypes.items():
            output.append(typeSdlFormat % (i, j))
        
        print("New SDL types for Batch Stuff...")
        print(output)
        return output

    def __generateDivideAndConquer(self, dotInitStmtDivConqSig,  divConqLoopValStmtSig, eqStr, divConqArgList):
        """think about how to make this more flexible"""
        divConqArgs = str(divConqArgList).replace("[", '').replace("]",'').replace("'", '')
        output = ""
        output += dc_header % divConqArgs
        for l in dotInitStmtDivConqSig:
            output += l
        output += dc_dot_loopVal_begin_for % sigIterator
        for l in divConqLoopValStmtSig:
            output += l
        output += end_for_loop
        
        # add the verification check(s)
        if type(eqStr) == str:
            output += dc_batch_verify_check % eqStr
            output += dc_recursive_call % (divConqArgs.replace("endSigNum", "midway"), divConqArgs.replace("startSigNum", "midSigNum"))
        elif type(eqStr) == list:
            pass
        else:
            pass
        
        output += dc_footer
        if self.debug:
            print("Divide and Conquer: ")
            print(output)
        return output
    
    def __generatePrecomputeLines(self, loopIndex):
        output = ""
        for i,j in self.precomputeDict.items():
            if str(i) != "delta": # JAA: bandaid. fix: remove delta from batch precompute list
                sa = SubstituteAttr(self.sdlData[BATCH_VERIFY_MAP], loopIndex)
                eq = BinaryNode.copy(j)
                ASTVisitor(sa).preorder(eq)                
                output += "%s := %s\n" % (i, Filter(eq))
        if self.debug:
            print("Precompute Lines: ")
            print(output)
        return output
                
    
    def __generateBatchVerify(self, batchVerifyArgList, divConqArgList, dotCacheCalcList):
        output = ""
        bVerifyArgs = str(list(batchVerifyArgList)).replace("[", '').replace("]",'').replace("'", '')
        divConqArgs = str(list(divConqArgList)).replace("[", '').replace("]",'').replace("'", '')

        forLoopStmtOverSigs = sigForLoop % (sigIterator, NUM_SIGNATURES)
        output += batch_verify_header % (bVerifyArgs, forLoopStmtOverSigs, bVerifyArgs)
        output += forLoopStmtOverSigs
        output += self.__generatePrecomputeLines(sigIterator) 
        for i in dotCacheCalcList:
            output += i
        output += end_for_loop
        output += batch_verify_footer % (divConqArgs.replace("startSigNum", "0").replace("endSigNum", NUM_SIGNATURES))
        if self.debug:
            print("Batch verify: ")
            print(output)
        return output            
    
    def __generateNewSDL(self, typesLinesList, sdlBatchVerifierLines):
        # get the types section from original SDL source
        # 1. update types section first
        oldSDL = getLinesOfCode()
        startTypeLine = getStartLineNoOfFunc(TYPES_HEADER)+1
        endTypeLine = getEndLineNoOfFunc(TYPES_HEADER)
        newTypeList = []
        # 1.5 record old type definitions from sdl
        for i in range(startTypeLine, endTypeLine-1):
            stripI = oldSDL[i].strip(SPACES)
            newTypeList.append(stripI)
        # 1.8 record new type definitions into list
        for i in typesLinesList:
            stripI = i.strip(SPACES)
            if stripI not in newTypeList:
                newTypeList.append(stripI)
        
        removeRangeFromLinesOfCode(startTypeLine, endTypeLine-1)
        appendToLinesOfCode(newTypeList, startTypeLine)
        # 2. re-run the parseLinesOfCode()
        parseLinesOfCode(getLinesOfCode(), False, True)
        
        # 3. get the new last line #, append the sdlBatchVerifierLines to it.
        outputBatchVerifyLines = sdlBatchVerifierLines.split('\n')
        outputBatchVerifyLinesFinal = []
        lastLineSDL = len(getLinesOfCode())+1
#        print("last line: ", lastLineSDL)
        
        for i in outputBatchVerifyLines:
            outputBatchVerifyLinesFinal.append(i + '\n')
        appendToLinesOfCode(outputBatchVerifyLinesFinal, lastLineSDL)        
        parseLinesOfCode(getLinesOfCode(), True, True)
        print("DONE!!")
        
        # 4. write the file to 
        writeLinesOfCodeToFileOnly(self.sdlOutfile)
        return
    
    def construct(self):
        secparamLine = ""
        if self.sdlData[SECPARAM] == None: secparamLine = "secparam := 80\n" # means NOT already defined in SDL
        # compute pre-cache values for signatures
        subProds = SubstituteSigDotProds(self.varTypes, sigIterator, NUM_SIGNATURES, self.variableCount)
        ASTVisitor(subProds).preorder(self.finalBatchEq)
        # update variable counter
        self.variableCount = subProds.getVarCount()
        
        # for loop over signers, right?
        subProds1 = SubstituteSigDotProds(self.varTypes, signerIterator, 'l', self.variableCount)
        ASTVisitor(subProds1).preorder(self.finalBatchEq)
        self.variableCount = subProds1.getVarCount()
        
        verifyArgTypes = self.sdlData[BATCH_VERIFY]
        verifyArgKeys = verifyArgTypes.keys()
        
        dotLoopValTypesSig = {}
        dotCacheTypesSig = {}
        dotInitStmtDivConqSig = []
        divConqLoopValStmtSig = []
        dotVerifyEq = {}
        dotCacheCalc = []
        divConqArgList = ["delta", "startSigNum", "endSigNum", "incorrectIndices"] # JAA: make variable names more configurable
        print("Pre-compute over signatures...")
        for i in subProds.dotprod['list']:
            if self.debug: print(i,":=", subProds.dotprod['types'][i])
            loopVal = "%sLoopVal" % i
            dotCache = "%sCache" % i
            dotLoopValTypesSig[ loopVal ] = str(subProds.dotprod['types'][i])
            dotInitStmtDivConqSig.append("%s := init(%s)\n" % (loopVal, subProds.dotprod['types'][i]))
            divConqLoopValStmtSig.append("%s := %s * %s#%s\n" % (loopVal, loopVal, dotCache, sigIterator)) # this is mul specifically
            dotVerifyEq[str(i)] = loopVal
            dotCacheTypesSig[dotCache] = "list{%s}" % subProds.dotprod['types'][i]
            divConqArgList.append(dotCache)
            dotCacheCalc.append("%s#%s := %s\n" % (dotCache, sigIterator, self.ReplaceAppropArgs(self.sdlData[BATCH_VERIFY_MAP], sigIterator, subProds.dotprod['dict'][i].getRight()))) # JAA: need to write Filter function
                                
        divConqArgList.extend(verifyArgKeys)
        print("Results over signatures...")
        num_types = len(dotInitStmtDivConqSig)
        for i in range(num_types):
            print(i, ": ", dotInitStmtDivConqSig[i], end='')

        num_types = len(divConqLoopValStmtSig)
        for i in range(num_types):
            print(i, ": ", divConqLoopValStmtSig[i], end='')

        eqStr = str(self.finalBatchEq)
        for k,v in dotVerifyEq.items():
            eqStr = eqStr.replace(k, v)
        print("Final eq: ", eqStr)
        
        outputLines1 = self.__generateMembershipTest(verifyArgKeys) 
        outputLines2 = self.__generateDivideAndConquer(dotInitStmtDivConqSig,  divConqLoopValStmtSig, eqStr, divConqArgList)
        outputLines3 = self.__generateBatchVerify(verifyArgKeys, divConqArgList, dotCacheCalc)
        
        typeOutputLines = self.__generateTypes(dotLoopValTypesSig, dotCacheTypesSig, verifyArgTypes)
        output = secparamLine + outputLines1 + outputLines2 + outputLines3
        self.__generateNewSDL(typeOutputLines, output)
#                
#        print("Pre-compute over signers...")
#        dotLoopValTypesSigner = []
#        dotCacheTypesSigner = []
#        dotInitStmtDivConqSigner = []
#        divConqLoopValStmtSigner = []
#        if subProds1.dotprod['list']:
#            for i in subProds1.dotprod['list']:
#                if self.debug: print(i,":=", subProds1.dotprod['types'][i])
#                dotLoopValTypesSigner.append("%sLoopVal := %s\n" % (i, subProds1.dotprod['types'][i]))
#                dotCacheTypesSigner.append("%sCache := list{%s}\n" % (i, subProds1.dotprod['types'][i]))
#                dotInitStmtDivConqSigner.append("%sLoopVal := init(%s)\n" % (i, subProds1.dotprod['types'][i]))
#        else:
#            print("None Yet")

        return

        
        
        
        