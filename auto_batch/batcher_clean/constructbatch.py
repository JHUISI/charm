import sdlpath
from sdlparser.SDLParser import *
from batchoptimizer import SubstituteSigDotProds, SubstituteAttr, DropIndexForPrecomputes, GetVarsInEq, GetDeltaIndex
from batchconfig import *

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

delta_word = "delta"
delta_stmt = delta_word + "%s := SmallExp(secparam)\n"
delta_lhs = delta_word + "%s := "


batch_verify_header = """
BEGIN :: func:batchverify
input := list{%s, incorrectIndices}
%s %sEND :: for
"""

membershipTestLine = """
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
        self.defaultBatchTypes = {"incorrectIndices" : "list{int}", "startSigNum" : "int", "endSigNum " : "int"}
        for i in list(precompDict.keys()):
            if str(i) != 'delta': self.precomputeVarList.append(i.getAttribute())
        self.finalBatchEq = BinaryNode.copy(finalSdlBatchEq)
        self.variableCount = variableCount
        gdi = GetDeltaIndex()
        ASTVisitor(gdi).preorder(finalSdlBatchEq)
        self.deltaListFirst, self.deltaListSecond = gdi.getDeltaList() # default is none if single equation
        self.newDeltaList = []
        self.__generateDeltaLines(sigIterator, self.newDeltaList)
        self.debug = False
        
    def ReplaceAppropArgs(self, map, forLoopIndex, node):
        sa = SubstituteAttr(map, forLoopIndex)
        eq = BinaryNode.copy(node)
        ASTVisitor(sa).preorder(eq)
        dp = DropIndexForPrecomputes(self.precomputeVarList, forLoopIndex)
        ASTVisitor(dp).preorder(eq)
        return Filter(eq)
        
    def __generateMembershipTest(self, verifyArgKeys, verifyArgTypes):
        output = ""
        strTypeList = ["str", "list{str}"]
        verifyArgList = []
        # prune "str" and "list{str}" types out of membership test
        for i in verifyArgKeys:
            if self.varTypes.get(i) not in strTypeList and verifyArgTypes.get(i) not in strTypeList:
                # add to lists
                print("verify membership of: ", i)
                verifyArgList.append(i)
                 
        verifyArgs = str(list(verifyArgList)).replace("[", '').replace("]",'').replace("'", '')        
        output += membership_header % verifyArgs
        for eachArg in verifyArgList:
            output += membership_check % eachArg
        output += membership_footer 
        if self.debug: 
            print("Membership Test :=>")
            print(output)
        return (verifyArgList, output)
    
    def __generateTypes(self, dotLoopValTypesSig, dotCacheTypesSig, verifyArgTypes):
        output = []
        typeSdlFormat = "%s := %s\n"
        for i,j in self.defaultBatchTypes.items():
            output.append(typeSdlFormat % (i, j))
        for i,j in dotLoopValTypesSig.items():
            output.append(typeSdlFormat % (i, j))
        for i,j in dotCacheTypesSig.items():
            output.append(typeSdlFormat % (i, j))
        for i,j in verifyArgTypes.items():
            output.append(typeSdlFormat % (i, j))
        
        if self.debug:
            print("New SDL types for Batch Stuff...")
            for i in output:
                print(i, end="")        
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
    
    def __generatePrecomputeLines(self, loopIndex, dotCacheVarList):
        outputBeforePrecompute = ""
        outputPrecompute = ""
        nonPrecomputeDict = {}
        newPrecomputeDict = {}        
        # preprocess precompute lines
        if self.debug: print("compute outside the loop over signatures:")
        for i,j in self.precomputeDict.items():
            if str(i) not in dotCacheVarList:
                nonPrecomputeDict[i] = j
                if self.debug: print(i, ":= ", j)
                outputBeforePrecompute += "%s := %s\n" % (i, j)
            else:
                newPrecomputeDict[i] = j
        
        if self.debug: print("compute inside loop over signatures but before dotCache calculations:")
        for i,j in newPrecomputeDict.items():
            if str(i) != "delta": # JAA: bandaid. fix: remove delta from batch precompute list
                sa = SubstituteAttr(self.sdlData[BATCH_VERIFY_MAP], loopIndex, self.sdlData.get(CONST))
                eq = BinaryNode.copy(j)
                ASTVisitor(sa).preorder(eq)                
                line = "%s := %s\n" % (i, Filter(eq))
                if self.debug: print(line)
                outputPrecompute += line
        return (outputBeforePrecompute, outputPrecompute)
    
    
    def getShortForm(self, indexList):
        s = ""
        for i in indexList:
            s += i
        return s
    
    def __generateDeltaLines(self, loopVar, newList=None):
        output = ""
        delta_type = "list{ZR}"
        for i in self.deltaListFirst:
            output += delta_stmt % (i + "#" + loopVar)
            if newList != None: 
                newList.append(delta_word + i)
                self.defaultBatchTypes[delta_word + i] = delta_type
#        for i in self.deltaListSecond:
#            new_var = delta_word + self.getShortForm(i)  
#            if newList != None: newList.append(new_var) # adding to our list
#            output += new_var + "#" + loopVar + " := "
#            line = ""
#            for k in i:
#                line += delta_word + k + "#" + loopVar + " * "
#            line = line[:-2]
#            output += line + "\n"
            
        if output == "":
            output = delta_stmt % ("#" + loopVar)
            if newList != None: 
                newList.append(delta_word)
                self.defaultBatchTypes[delta_word] = delta_type
        return output
    
    def __generateBatchVerify(self, batchVerifyArgList, membershipTestList, divConqArgList, dotCacheCalcList, dotCacheVarList):
        output = ""
        bVerifyArgs = str(list(batchVerifyArgList)).replace("[", '').replace("]",'').replace("'", '')
        divConqArgs = str(list(divConqArgList)).replace("[", '').replace("]",'').replace("'", '')
        # pruned list of values we need to pass on to the membership test.
        membershipTest = str(list(membershipTestList)).replace("[", '').replace("]",'').replace("'", '')

        outputBeforePrecompute, outputPrecompute = self.__generatePrecomputeLines(sigIterator, dotCacheVarList)
        deltaLines = self.__generateDeltaLines(sigIterator)
        
        forLoopStmtOverSigs = sigForLoop % (sigIterator, NUM_SIGNATURES)
        output += batch_verify_header % (bVerifyArgs, forLoopStmtOverSigs, deltaLines)# membershipTest)
        output += membershipTestLine % membershipTest
        output += outputBeforePrecompute # if non empty
        output += forLoopStmtOverSigs
        output += outputPrecompute
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
        for i in range(startTypeLine-1, endTypeLine-1):
            print(i, ":", oldSDL[i], end="")
            stripI = oldSDL[i].replace(SPACES, "")
            addDelibSpace = stripI.replace(":=", " := ")             
            newTypeList.append(addDelibSpace)
        
        # 1.8 record new type definitions into list
        for i in typesLinesList:
            stripI = i.replace(SPACES, "")
            addDelibSpace = stripI.replace(":=", " := ") 
            if addDelibSpace not in newTypeList:
                newTypeList.append(addDelibSpace)
        
#        print("newTypeList: ", newTypeList)
        
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
        
        if ".bv" not in self.sdlOutfile: self.sdlOutfile += ".bv" # add appropriate extension to filename
        # 4. write the file to 
        writeLinesOfCodeToFileOnly(self.sdlOutfile)
        print("SDL file written to: ", self.sdlOutfile)
        return
    
    def __computeDotProducts(self):
        # compute pre-cache values for signatures
        subProdsOverSigs = SubstituteSigDotProds(self.varTypes, sigIterator, NUM_SIGNATURES, self.variableCount)
        ASTVisitor(subProdsOverSigs).preorder(self.finalBatchEq)
        # update variable counter
        self.variableCount = subProdsOverSigs.getVarCount()
        
        # for loop over signers, right?
        subProdsOverSigners = SubstituteSigDotProds(self.varTypes, signerIterator, 'l', self.variableCount)
        ASTVisitor(subProdsOverSigners).preorder(self.finalBatchEq)
        self.variableCount = subProdsOverSigners.getVarCount()
        
        return (subProdsOverSigs, subProdsOverSigners)
        
    
    def construct(self):        
        (subProds, subProds1) = self.__computeDotProducts()
        
        VarsForDotOverSigs = subProds.dotprod['list']
        VarsForDotTypesOverSigs = subProds.dotprod['types']
        VarsForDotASTOverSigs = subProds.dotprod['dict']

        VarsForDotOverSign = subProds1.dotprod['list']
        VarsForDotTypesOverSign = subProds1.dotprod['types']
        VarsForDotASTOverSign = subProds1.dotprod['dict']
#        print("list over signers: ", VarsForDotOverSign)
        
        self.__constructSDLBatchOverSignaturesOnly(VarsForDotOverSigs, VarsForDotTypesOverSigs, VarsForDotASTOverSigs)
    
    
    def __constructSDLBatchOverSignaturesOnly(self, VarsForDotOverSigs, VarsForDotTypesOverSigs, VarsForDotASTOverSigs):
        secparamLine = ""
        if self.sdlData[SECPARAM] == None: secparamLine = "secparam := 80\n" # means NOT already defined in SDL
        verifyArgTypes = self.sdlData[BATCH_VERIFY]
        if verifyArgTypes: verifyArgKeys = verifyArgTypes.keys()
        else: verifyArgKeys = verifyArgTypes = {}
        # everything as before
        dotLoopValTypesSig = {}
        dotCacheTypesSig = {}
        dotInitStmtDivConqSig = []
        divConqLoopValStmtSig = []
        dotVerifyEq = {}
        dotCacheCalc = []
        dotList = []
        dotCacheVarList = [] # list of variables that appear in dotCache list of precompute section
        divConqArgList = self.newDeltaList + ["startSigNum", "endSigNum", "incorrectIndices"] # JAA: make variable names more configurable
        gvi = GetVarsInEq([])
        
        print("Pre-compute over signatures...")
        for i in VarsForDotOverSigs:
            if self.debug: print(i,":=", VarsForDotTypesOverSigs[i])
            loopVal = "%sLoopVal" % i
            dotCache = "%sCache" % i
            dotLoopValTypesSig[ loopVal ] = str(VarsForDotTypesOverSigs[i])
            dotInitStmtDivConqSig.append("%s := init(%s)\n" % (loopVal, VarsForDotTypesOverSigs[i]))
            divConqLoopValStmtSig.append("%s := %s * %s#%s\n" % (loopVal, loopVal, dotCache, sigIterator)) # this is mul specifically
            dotVerifyEq[str(i)] = loopVal
            dotCacheTypesSig[dotCache] = "list{%s}" % VarsForDotTypesOverSigs[i]
            divConqArgList.append(dotCache)
            dotList.append(str(i))
            dotCacheRHS = VarsForDotASTOverSigs[i].getRight()
            ASTVisitor(gvi).preorder(dotCacheRHS)
            dotCacheVarList.extend(gvi.getVarList())
            dotCacheVarList = list(set(dotCacheVarList))
            dotCacheCalc.append("%s#%s := %s\n" % (dotCache, sigIterator, self.ReplaceAppropArgs(self.sdlData[BATCH_VERIFY_MAP], sigIterator, dotCacheRHS))) # JAA: need to write Filter function
        
        # get divide and conquer argument list and append to divConqArgList list
        # these are the values that are needed in the divide and conquer routine
        gvi2 = GetVarsInEq(dotList)
        ASTVisitor(gvi2).preorder(self.finalBatchEq)
        divConqArgList.extend(gvi2.getVarList())
#        divConqArgList.extend(verifyArgKeys)
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
        
        membershipTestList, outputLines1 = self.__generateMembershipTest(verifyArgKeys, verifyArgTypes) 
        outputLines2 = self.__generateDivideAndConquer(dotInitStmtDivConqSig,  divConqLoopValStmtSig, eqStr, divConqArgList)
        outputLines3 = self.__generateBatchVerify(verifyArgKeys, membershipTestList, divConqArgList, dotCacheCalc, dotCacheVarList)
        
        typeOutputLines = self.__generateTypes(dotLoopValTypesSig, dotCacheTypesSig, verifyArgTypes)
        output = secparamLine + outputLines1 + outputLines2 + outputLines3
        self.__generateNewSDL(typeOutputLines, output)

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

        
        
        
        
