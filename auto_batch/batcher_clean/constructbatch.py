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

dc_for_begin = """
BEGIN :: for
for{%s := %s, %s}\n"""
end_for_loop = "END :: for"


dc_for_inner_begin = """
BEGIN :: forinner
forinner{%s := %s, %s}\n"""

end_for_inner_loop = "END :: forinner"

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
linkVar = "_link"

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

batch_loop_signer = """
BEGIN :: for
%s
BEGIN :: forinner
%s
END :: forinner

END :: for
"""
SPACES = ' '
zero = '0'
sigIterator = 'z'
signerIterator = 'y'
signerVarCount = 'l'
PRECHECK = "check" # means we need to check stuff over signatures

sigIteratorTuple = (sigIterator, zero, NUM_SIGNATURES)
signerIteratorTuple = (signerIterator, zero, signerVarCount)
signatureProd = "prod{%s := %s,%s}" % sigIteratorTuple
signerProd = "prod{%s := %s,%s}" % signerIteratorTuple

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

    # for variables that are precomputed over signatures        
    def ReplaceAppropArgs(self, map, forLoopIndex, node, exceptList=[]):
        sa = SubstituteAttr(map, forLoopIndex)
        eq = BinaryNode.copy(node)
        ASTVisitor(sa).preorder(eq)
        exceptList.extend(self.sdlData.get(CONST)) # add list of constant variables here
        dp = DropIndexForPrecomputes(self.precomputeVarList + exceptList, forLoopIndex)
        ASTVisitor(dp).preorder(eq)
        return Filter(eq)

    def ReplaceAppropArgsExcept(self, map, forLoopIndex, node, exceptList, exceptMap):
        sa = SubstituteAttr(map, forLoopIndex)
        eq = BinaryNode.copy(node)
        ASTVisitor(sa).preorder(eq)
        exceptList.append(delta_word) # just added
        exceptList.extend(self.sdlData.get(CONST)) # add list of constant variables here        
        dp = DropIndexForPrecomputes(self.precomputeVarList + exceptList, forLoopIndex)
        ASTVisitor(dp).preorder(eq)

        eqStr = Filter(eq)
        for k,v in exceptMap.items():
            eqStr = eqStr.replace(k, v)
        return eqStr


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

    def __generateDivideAndConquerFlexible(self, eqStr, divConqArgList, divAndConqBodyFunction, *args):
        """think about how to make this more flexible"""
        divConqArgs = str(divConqArgList).replace("[", '').replace("]",'').replace("'", '')
        output = ""
        output += dc_header % divConqArgs
        
        output += divAndConqBodyFunction(output, *args)        
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
            print("Divide and Conquer...")
            print(output)
        return output

    
    def __isVarDepsAllConstants(self, node_tree):
        constList = self.sdlData.get(CONST)
        if self.debug: print("node_tree: ", node_tree, constList)
        gvi = GetVarsInEq([])
        ASTVisitor(gvi).preorder(node_tree)
        varDepList = gvi.getVarList()
        if len(varDepList) > 1 and set(varDepList).issubset(constList):
            return True
        else:
            return False # TODO: might need to look for other cases here
    
    def __generatePrecomputeLinesForBV(self, loopIndex, dotCacheVarList):
#        self.debug = True
        outputBeforePrecompute = ""
        outputPrecompute = ""
        nonPrecomputeDict = {}
        newPrecomputeDict = {}
            
        # preprocess precompute lines
        if self.debug: 
            print("compute outside the loop over signatures:")
            print("dotCacheVarList: ", dotCacheVarList)
        for i,j in self.precomputeDict.items():
            if str(i) == PRECHECK:
                print("variable map :=>>> ", self.sdlData[BATCH_VERIFY_MAP])
                mapDict = self.sdlData[BATCH_VERIFY_MAP]
                mapKeys = [ str(x) for x in mapDict.keys() ]
                jList = j.getListNode()
                for k in range(len(jList)):
                    if jList[k] in mapKeys:
                        jList[k] = mapDict[ jList[k] ] + "#" + sigIterator
                
                outputBeforePrecompute += dc_for_begin % (sigIteratorTuple)
                outputBeforePrecompute += "BEGIN :: if\n"
                outputBeforePrecompute += "if {" + str( j ) + " == False }\n"
                outputBeforePrecompute += " output := False\n"
                outputBeforePrecompute += " return := output\n"
                outputBeforePrecompute += "END :: if\n"
                outputBeforePrecompute += end_for_loop + "\n"
            elif str(i) not in dotCacheVarList:
#                print("took this branch: ", i, ":", dotCacheVarList)
                nonPrecomputeDict[i] = j
                if self.debug: print(i, ":= ", j)
                outputBeforePrecompute += "%s := %s\n" % (i, j)
            # see if attrs in statement are all constants, if so then non
            elif str(i) != delta_word and self.__isVarDepsAllConstants(j):
                nonPrecomputeDict[i] = j
                if self.debug: print(i, ":= ", j)
                outputBeforePrecompute += "%s := %s\n" % (i, j)   
            else:
                newPrecomputeDict[i] = j
        
        if self.debug: 
            print("compute inside loop over signatures but before dotCache calculations:")
            print("dotCacheVarList: ", dotCacheVarList)
        for i,j in newPrecomputeDict.items():
            if str(i) != "delta" and str(i) in dotCacheVarList: # JAA: bandaid. fix: remove delta from batch precompute list
                sa = SubstituteAttr(self.sdlData[BATCH_VERIFY_MAP], loopIndex, self.sdlData.get(CONST))
                eq = BinaryNode.copy(j)
                ASTVisitor(sa).preorder(eq)                
                line = "%s := %s\n" % (i, Filter(eq))
                if self.debug: print(line)
                outputPrecompute += line
        
       # mark precompute variables we have already seen
        keysToPrecomputeVars = list(self.precomputeDict.keys())
        for i in keysToPrecomputeVars:
            if str(i) in dotCacheVarList:
                del self.precomputeDict[i]
       
        print("outputBeforePrecompute: ", outputBeforePrecompute)
        print("outputPrecompute: ", outputPrecompute)
        return (outputBeforePrecompute, outputPrecompute)
    
    def __generatePrecomputeLinesForDV(self, loopIndex, dotCacheVarList):
        # note: dotCacheVarList needs to be comprehensive for all variables needed in DV
        outputBeforePrecompute = ""
        outputPrecompute = ""
        nonPrecomputeDict = {}
        newPrecomputeDict = {}
            
        # preprocess precompute lines
        if self.debug: 
            print("compute outside the loop over signatures:")
            print("dotCacheVarList: ", dotCacheVarList)
        for i,j in self.precomputeDict.items():
            # see if attrs in statement are all constants...
            if str(i) != delta_word and (self.__isVarDepsAllConstants(j) and str(i) in dotCacheVarList):
                nonPrecomputeDict[i] = j
                if self.debug: print(i, ":= ", j)
                outputBeforePrecompute += "%s := %s\n" % (i, j)   
            else:
                newPrecomputeDict[i] = j
        
        if self.debug: 
            print("compute inside loop over signatures but before dotCache calculations:")
            print("dotCacheVarList: ", dotCacheVarList)
        for i,j in newPrecomputeDict.items():
            if str(i) != "delta" and str(i) in dotCacheVarList: # JAA: bandaid. fix: remove delta from batch precompute list
                sa = SubstituteAttr(self.sdlData[BATCH_VERIFY_MAP], loopIndex, self.sdlData.get(CONST))
                eq = BinaryNode.copy(j)
                ASTVisitor(sa).preorder(eq)                
                line = "%s := %s\n" % (i, Filter(eq))
                if self.debug: print(line)
                outputPrecompute += line
        
       # mark precompute variables we have already seen
        keysToPrecomputeVars = list(self.precomputeDict.keys())
        for i in keysToPrecomputeVars:
            if str(i) in dotCacheVarList:
                del self.precomputeDict[i]
       
#        print("outputBeforePrecompute: ", outputBeforePrecompute)
#        print("outputPrecompute: ", outputPrecompute)
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
            
        if output == "":
            output = delta_stmt % ("#" + loopVar)
            if newList != None: 
                newList.append(delta_word)
                self.defaultBatchTypes[delta_word] = delta_type
        return output
    
    def __generateBatchVerify(self, batchVerifyArgList, membershipTestList, divConqArgList, dotCacheCalcList, dotCacheVarList, dotDepComputationMap=None):
        output = ""
        bVerifyArgs = str(list(batchVerifyArgList)).replace("[", '').replace("]",'').replace("'", '')
        divConqArgs = str(list(divConqArgList)).replace("[", '').replace("]",'').replace("'", '')
        # pruned list of values we need to pass on to the membership test.
        membershipTest = str(list(membershipTestList)).replace("[", '').replace("]",'').replace("'", '')

        outputBeforePrecompute, outputPrecompute = self.__generatePrecomputeLinesForBV(sigIterator, dotCacheVarList)
        deltaLines = self.__generateDeltaLines(sigIterator)
        
        forLoopStmtOverSigs = sigForLoop % (sigIterator, NUM_SIGNATURES)
        output += batch_verify_header % (bVerifyArgs, forLoopStmtOverSigs, deltaLines)# membershipTest)
        output += membershipTestLine % membershipTest
        output += outputBeforePrecompute # if non empty
        output += forLoopStmtOverSigs
        output += outputPrecompute
        for i in dotCacheCalcList:
            if dotDepComputationMap != None and dotDepComputationMap.get(i) != None:
                output += dotDepComputationMap[i]
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
        
    
    def __searchForDependencies(self, dict1, dict2):
        """ if there are no deps, then the two can be calculated over their respective for loops separately,
            otherwise, need to figure out which calculation goes in the outer and which one in the inner."""
        # if dict2 has any var references into dict1 or vice versa, then the list that HAS the reference should
        # be in the OUTER LOOP and the variable that IS referenced is in the INNER LOOP
        precomputeBeforeDV = {}
        notPrecomputeBeforeDV = {}
        references = {}
        dotPrefix = "dot"
        dotList1 = list(dict1.keys())
        dotList2 = list(dict2.keys())
        print("list over signatures:", dotList1)
        for i,j in dict1.items():
            gviq = GetVarsInEq([])
            ASTVisitor(gviq).preorder(j.getRight())
            references[str(i)] = ([x for x in gviq.getVarList() if dotPrefix in x], j.getLeft())
            print(i, ":", j, ", var list: ", references[str(i)])
        print("list over signers:", dotList2)
        for i, j in dict2.items():
            gviq = GetVarsInEq([])
            ASTVisitor(gviq).preorder(j.getRight())
            references[str(i)] = ([x for x in gviq.getVarList() if dotPrefix in x], j.getLeft())
            print(i, ":", j, ", var list: ", references[str(i)])
        
        listOfDots = list(references.keys())
        listOfDots.sort()
        for i in listOfDots:
            # for each dot value, go through the list of dependencies
            for k in references[i][0]:
                if dotPrefix in k:
                    del references[k]                

        # pruned version
        print("pruned dot lists")
        listOfDots = list(references.keys())
        listOfDots.sort()
        for i in listOfDots:
            print(i, ":", references[i][0], ": range:", references[i][1])
            if str(references[i][1]) == signatureProd and len(references[i][0]) == 0:
                # means we can precompute this entirely b/c it doesn't have any dependencies
                precomputeBeforeDV[i] = references[i]
            elif str(references[i][1]) == signatureProd and len(references[i][0]) >= 1:
                # search list to see if any of the dotValues have the same 'signatureProd' reference[i][1]
                # if so, then we can precompute as before
                precomputeBeforeDV[i] = references[i] # handles case where sigProd on outside and signerProd on inside too
#                print("this condition met for: ", i, "len()", len(references[i][0]))                
            elif str(references[i][1]) == signerProd and len(references[i][0]) == 0:
                precomputeBeforeDV[i] = references[i]
            elif str(references[i][1]) == signerProd and len(references[i][0]) >= 1: 
                notPrecomputeBeforeDV[i] = references[i]
            else:
                pass
        return precomputeBeforeDV, notPrecomputeBeforeDV  

    def __searchForDependenciesGeneric(self, dict1, dict2):
        """ if there are no deps, then the two can be calculated over their respective for loops separately,
            otherwise, need to figure out which calculation goes in the outer and which one in the inner."""
        # if dict2 has any var references into dict1 or vice versa, then the list that HAS the reference should
        # be in the OUTER LOOP and the variable that IS referenced is in the INNER LOOP
        precomputeBeforeDV = {}
        notPrecomputeBeforeDV = {}
        references = {}
        dotPrefix = "dot"
        dotList1 = list(dict1.keys())
        dotList2 = list(dict2.keys())
        print("list over signatures:", dotList1)
        for i,j in dict1.items():
            gviq = GetVarsInEq([])
            ASTVisitor(gviq).preorder(j.getRight())
            references[str(i)] = ([x for x in gviq.getVarList() if dotPrefix in x], j.getLeft())
            print(i, ":", j, ", var list: ", references[str(i)])
        print("list over signers:", dotList2)
        for i, j in dict2.items():
            gviq = GetVarsInEq([])
            ASTVisitor(gviq).preorder(j.getRight())
            references[str(i)] = ([x for x in gviq.getVarList() if dotPrefix in x], j.getLeft())
            print(i, ":", j, ", var list: ", references[str(i)])
        
        listOfDots = list(references.keys())
        listOfDots.sort()
        for i in listOfDots:
            # for each dot value, go through the list of dependencies
            for k in references[i][0]:
                if dotPrefix in k:
                    del references[k]                

        # pruned version
        print("pruned dot lists")
        listOfDots = list(references.keys())
        listOfDots.sort()
        dotDependency = None
        for i in listOfDots:
            print(i, ":", references[i][0], ": range:", references[i][1])
            if str(references[i][1]) == signatureProd and len(references[i][0]) == 0:
                # means we can precompute this entirely b/c it doesn't have any dependencies
                dotDependency = False
                precomputeBeforeDV[i] = {'dotDep': references[i], 'hasDep':dotDependency} # second argument represents dependency
            elif str(references[i][1]) == signatureProd and len(references[i][0]) >= 1:
                # search list to see if any of the dotValues have the same 'signatureProd' reference[i][1]
                # if so, then we can precompute as before
                dotDependency = True
                precomputeBeforeDV[i] = {'dotDep': references[i], 'hasDep':dotDependency} # handles case where sigProd on outside and signerProd on inside too
            elif str(references[i][1]) == signerProd and len(references[i][0]) == 0:
                dotDependency = False
                precomputeBeforeDV[i] = {'dotDep': references[i], 'hasDep':dotDependency}
            elif str(references[i][1]) == signerProd and len(references[i][0]) >= 1: 
                dotDependency = True
                notPrecomputeBeforeDV[i] = {'dotDep': references[i], 'hasDep':dotDependency}
            else:
                pass
        return precomputeBeforeDV, notPrecomputeBeforeDV  

    
    def construct(self):
        (subProds, subProds1) = self.__computeDotProducts()
        
        # dot products over signatures
        # keys: dotA, dotB ... dotZ
        VarsForDotOverSigs = subProds.dotprod['list']
        # types: dotA: G1 , dotB: G2, ..., dotZ: GT
        VarsForDotTypesOverSigs = subProds.dotprod['types'] 
        # assignment for each dot value.
        # dotA := x#z ^ y#z , etc
        VarsForDotASTOverSigs = subProds.dotprod['dict'] 

        # dot products over signers
        # keys: dotA, dotB ...
        VarsForDotOverSign = subProds1.dotprod['list']
        # types: see above
        VarsForDotTypesOverSign = subProds1.dotprod['types']
        # assignment AST for each dot value
        VarsForDotASTOverSign = subProds1.dotprod['dict']
#        print("list over signers: ", VarsForDotOverSign)
        
#        print("len over signatures: ", len(VarsForDotOverSigs))
#        for i in VarsForDotOverSigs:
#            print(i, ":=", VarsForDotASTOverSigs[i])
#        print("len over signers: ", len(VarsForDotOverSign))
#        sys.exit(0)
        # dotValues in signature list is greater than 1 and the one of the signers is 0, then no brainer
        if len(VarsForDotOverSigs) >= 1 and len(VarsForDotOverSign) == 0:
            # TODO: Rework this to handle dependencies between dotValues better.
            self.__constructSDLBatchOverSignaturesGeneric(VarsForDotOverSigs, VarsForDotTypesOverSigs, VarsForDotASTOverSigs)
#            self.__constructSDLBatchOverSignaturesOnly(VarsForDotOverSigs, VarsForDotTypesOverSigs, VarsForDotASTOverSigs)
        elif len(VarsForDotOverSigs) >= 1 and len(VarsForDotOverSign) >= 1:
            # mixed mode between loops over ...
            self.__constructSDLBatchOverSignaturesAndSigners(VarsForDotOverSigs, VarsForDotTypesOverSigs, VarsForDotASTOverSigs, 
                                                             VarsForDotOverSign, VarsForDotTypesOverSign, VarsForDotASTOverSign)
        elif len(VarsForDotOverSigs) == 0 and len(VarsForDotOverSign) >= 1:
            print("TODO: this is a new case.")
            sys.exit(0)
        else:
            print("TODO: JAA - what case is this: ", len(VarsForDotOverSigs), len(VarsForDotOverSign))
    
    def __cleanType(self, typeVar):
        newTypeTmp = ""
        if typeVar == "listZR":
            newTypeTmp = "ZR"
        elif typeVar == "listG1":
            newTypeTmp = "G1"
        elif typeVar == "listG2":
            newTypeTmp = "G2"
        elif typeVar == "listGT":
            newTypeTmp = "GT"
        elif typeVar == "listStr":
            newTypeTmp = "str"
        else:
            return typeVar
        return newTypeTmp

    def __createStatements(self, VarsForDotOverSigs, VarsForDotTypesOverSigs, VarsForDotASTOverSigs, varIterator, combineLoopAndCacheStmt=False, exceptList=[]):
        dotLoopValTypesSig = {}
        dotCacheTypesSig = {}
        dotInitStmtDivConqSig = []
        divConqLoopValStmtSig = []
        dotVerifyEq = {}
        dotCacheCalc = []
        dotList = []
        dotCacheVarList = [] # list of variables that appear in dotCache list of precompute section
        divConqArgList = []
#        divConqArgList = self.newDeltaList + ["startSigNum", "endSigNum", "incorrectIndices"] # JAA: make variable names more configurable
        gvi = GetVarsInEq([])
        
#        print("Pre-compute over signatures...")
        for i in VarsForDotOverSigs:
            print(i,":=", VarsForDotTypesOverSigs[i])
            loopVal = "%sLoopVal" % i
            dotCache = "%sCache" % i
            getType = self.__cleanType(VarsForDotTypesOverSigs[i])
            dotLoopValTypesSig[ loopVal ] = getType
            dotInitStmtDivConqSig.append("%s := init(%s)\n" % (loopVal, getType))
            dotVerifyEq[str(i)] = loopVal
            dotList.append(str(i))
            dotCacheRHS = VarsForDotASTOverSigs[i].getRight()
            ASTVisitor(gvi).preorder(dotCacheRHS)
            dotCacheVarList.extend(gvi.getVarList())
            dotCacheVarList = list(set(dotCacheVarList))            
            if combineLoopAndCacheStmt:
                compStmt = self.ReplaceAppropArgs(self.sdlData[BATCH_VERIFY_MAP], varIterator, dotCacheRHS)
                divConqLoopValStmtSig.append("%s := %s * %s\n" % (loopVal, loopVal, compStmt)) # this is mul specifically
            else:
                divConqLoopValStmtSig.append("%s := %s * %s#%s\n" % (loopVal, loopVal, dotCache, varIterator)) # this is mul specifically
                dotCacheTypesSig[dotCache] = "list{%s}" % getType
                divConqArgList.append(dotCache)
                dotCacheCalc.append("%s#%s := %s\n" % (dotCache, varIterator, self.ReplaceAppropArgs(self.sdlData[BATCH_VERIFY_MAP], varIterator, dotCacheRHS, exceptList))) # JAA: need to write Filter function
        
        self.printList("0: dotLoopValTypesSig", dotLoopValTypesSig)
        self.printList("1: dotCacheTypesSig", dotCacheTypesSig)
        self.printList("2: dotInitStmtDivConqSig", dotInitStmtDivConqSig)
        self.printList("3: divConqLoopValStmtSig", divConqLoopValStmtSig)
        self.printList("4: dotVerifyEq", dotVerifyEq)
        self.printList("5: dotCacheCalc", dotCacheCalc)
        self.printList("6: dotList", dotList)
        self.printList("7: dotCacheVarList", dotCacheVarList)
        self.printList("8: divConqArgList", divConqArgList)
        return dotLoopValTypesSig, dotCacheTypesSig, dotInitStmtDivConqSig, divConqLoopValStmtSig, dotVerifyEq, dotCacheCalc, dotList, dotCacheVarList, divConqArgList

    def __createStatementsNoCache(self, VarsForDotOverSigs, VarsForDotTypesOverSigs, VarsForDotASTOverSigs, varIterator, dotList2):
        dotLoopValTypesSig = {}
        dotCacheTypesSig = {}
        dotInitStmtDivConqSig = []
        divConqLoopValStmtSig = []
        dotVerifyEq = {}
        dotCacheCalc = []
        dotList = []
        dotList2Map = {}
        dotCacheVarList = [] # list of variables that appear in dotCache list of precompute section
        divConqArgList = []
#        divConqArgList = self.newDeltaList + ["startSigNum", "endSigNum", "incorrectIndices"] # JAA: make variable names more configurable
        gvi = GetVarsInEq(dotList2)

        for i in dotList2:
            loopVal = "%sLoopVal" % i
            dotList2Map[i] = loopVal
        
#        print("Pre-compute over signatures...")
        for i in VarsForDotOverSigs:
            print(i,":=", VarsForDotTypesOverSigs[i])
            loopVal = "%sLoopVal" % i
            getType = self.__cleanType(VarsForDotTypesOverSigs[i])
            dotLoopValTypesSig[ loopVal ] = getType
            dotInitStmtDivConqSig.append("%s := init(%s)\n" % (loopVal, getType))
            dotVerifyEq[str(i)] = loopVal
#            dotCacheTypesSig[dotCache] = "list{%s}" % VarsForDotTypesOverSigs[i]
#            divConqArgList.append(dotCache)
            dotList.append(str(i))
            dotCacheRHS = VarsForDotASTOverSigs[i].getRight()
            ASTVisitor(gvi).preorder(dotCacheRHS)
            # need to modify it a bit differently here: replace dot values with real computations
            divConqLoopValStmtSig.append("%s := %s * %s\n" % (loopVal, loopVal, self.ReplaceAppropArgsExcept(self.sdlData[BATCH_VERIFY_MAP], varIterator, dotCacheRHS, dotList2, dotList2Map))) # this is mul specifically
            dotCacheVarList.extend(gvi.getVarList())
            dotCacheVarList = list(set(dotCacheVarList))
#            dotCacheCalc.append("%s#%s := %s\n" % (dotCache, varIterator, self.ReplaceAppropArgs(self.sdlData[BATCH_VERIFY_MAP], varIterator, dotCacheRHS))) # JAA: need to write Filter function
        
        self.printList("0: dotLoopValTypesSig", dotLoopValTypesSig)
        self.printList("1: dotCacheTypesSig", dotCacheTypesSig)
        self.printList("2: dotInitStmtDivConqSig", dotInitStmtDivConqSig)
        self.printList("3: divConqLoopValStmtSig", divConqLoopValStmtSig)
        self.printList("4: dotVerifyEq", dotVerifyEq)
        self.printList("5: dotCacheCalc", dotCacheCalc)
        self.printList("6: dotList", dotList)
        self.printList("7: dotCacheVarList", dotCacheVarList)
        self.printList("8: divConqArgList", divConqArgList)
        return dotLoopValTypesSig, dotCacheTypesSig, dotInitStmtDivConqSig, divConqLoopValStmtSig, dotVerifyEq, dotCacheCalc, dotList, dotCacheVarList, divConqArgList

    def __getSecParamLine(self):
        secparamLine = ""
        if self.sdlData[SECPARAM] == None: secparamLine = "secparam := 80\n" # means NOT already defined in SDL        
        return secparamLine

    def __constructSDLBatchOverSignaturesGeneric(self, VarsForDotOverSigs, VarsForDotTypesOverSigs, VarsForDotASTOverSigs):
        secparamLine = self.__getSecParamLine()
        batchVerifyArgList = []
        _batchVerifyArgList = list(self.sdlData[BATCH_VERIFY].keys())
        for i in _batchVerifyArgList:
            if linkVar not in str(i):
                batchVerifyArgList.append(i)
        batchVerifyArgTypes = self.sdlData[BATCH_VERIFY]
        batchVerifyArgList.sort()
        
        refSignatureDict, refSignerDict = self.__searchForDependenciesGeneric(VarsForDotASTOverSigs, {})
        dotKeys = list(refSignatureDict.keys())
        print("refSignatureDict keys: ", dotKeys)
        
        topLevelDotDict = {}
        
        for i in dotKeys:
            print("<====== CREATING STATEMENTS ======> : ", i)
            if refSignatureDict[i]['hasDep']: # 
                # if so, then need to precompute those dot values as well since they're necessary
                # to compute this top level dot computation.
                print("<====== CREATING NO CACHE STATEMENTS ======> : ", refSignatureDict[i]['dotDep'][0])
                listForDepSigs = self.__createStatementsNoCache(refSignatureDict[i]['dotDep'][0], VarsForDotTypesOverSigs, VarsForDotASTOverSigs, signerIterator, [])
                listForSigs = self.__createStatements([i], VarsForDotTypesOverSigs, VarsForDotASTOverSigs, sigIterator, False, listForDepSigs[6])
                topLevelDotDict[i] = (listForSigs, listForDepSigs)
            else: # this doesn't have any dependencies can pre-calc as usual
                listForSigs = self.__createStatements([i], VarsForDotTypesOverSigs, VarsForDotASTOverSigs, sigIterator)
                topLevelDotDict[i] = (listForSigs, None)  
            
        # now we should combine everything into the lists & dicts expected by: div-n-conq, membershiptest and batch_verify
        dotLoopValTypesSig = {}
        dotCacheTypesSig = {}
        dotInitStmtDivConqSig = []
        divConqLoopValStmtSig = []
        dotVerifyEq = {}
        dotCacheCalc = []
        dotList = []
        dotCacheVarList = [] # list of variables that appear in dotCache list of precompute section
        divConqArgList = self.newDeltaList + ["startSigNum", "endSigNum", "incorrectIndices"] # JAA: make variable names more configurable
        dotDepComputationMap = {}
        
        topLevelKeys = list(topLevelDotDict.keys())
        topLevelKeys.sort()
        for i in topLevelKeys:
            statementTuple = topLevelDotDict[i][0]            
            dotLoopValTypesSig.update(statementTuple[0])
            dotCacheTypesSig.update(statementTuple[1])
            dotInitStmtDivConqSig.extend(statementTuple[2])
            divConqLoopValStmtSig.extend(statementTuple[3])
            dotVerifyEq.update(statementTuple[4])
            dotCacheCalc.extend(statementTuple[5])
            dotList.extend(statementTuple[6])
            dotCacheVarList.extend(statementTuple[7])
            divConqArgList.extend(statementTuple[8])
            statementDep = topLevelDotDict[i][1] # this means current statementTuple has a ref in tree to statementDep
            if statementDep: # meaning this top level computation has dependencies, then proceed as follows:
                depOutput = self.__buildInnerForLoop(statementDep, signerIteratorTuple)
                for k in range(len(dotCacheCalc)):
                    for r,c in statementDep[4].items():
                        newCacheCalc = dotCacheCalc[k].replace(r, c)
                        if len(newCacheCalc) > len(dotCacheCalc[k]): # replacement was successful!
                            dotCacheCalc[ k ] = newCacheCalc
                            dotDepComputationMap[ newCacheCalc ] = depOutput
                        
        
        gvi2 = GetVarsInEq(dotList)
        ASTVisitor(gvi2).preorder(self.finalBatchEq)
        divConqArgList.extend(gvi2.getVarList())

        eqStr = str(self.finalBatchEq)
        for k,v in dotVerifyEq.items():
            eqStr = eqStr.replace(k, v)
        print("Final eq: ", eqStr)

        membershipTestList, outputLines1 = self.__generateMembershipTest(batchVerifyArgList, batchVerifyArgTypes) 
        outputLines2 = self.__generateDivideAndConquer(dotInitStmtDivConqSig,  divConqLoopValStmtSig, eqStr, divConqArgList)
        outputLines3 = self.__generateBatchVerify(batchVerifyArgList, membershipTestList, divConqArgList, dotCacheCalc, dotCacheVarList, dotDepComputationMap)

        typeOutputLines = self.__generateTypes(dotLoopValTypesSig, dotCacheTypesSig, batchVerifyArgTypes)
        output = secparamLine + outputLines1 + outputLines2 + outputLines3
        self.__generateNewSDL(typeOutputLines, output)
        return
    
    def __buildInnerForLoop(self, dotDepStmts, loopIterator):
        #TODO: need to get var list so that we can properly pull the precompute variables needed
        my_output = ""
        dotCacheVarList = dotDepStmts[7]
        outputBeforePrecompute, outputPrecompute = self.__generatePrecomputeLinesForBV(loopIterator[0], dotCacheVarList)
        
        dotInitStmtDivConqSig, divConqLoopValStmtSig = dotDepStmts[2], dotDepStmts[3]
        for i in dotInitStmtDivConqSig:
            my_output += i
        my_output += outputBeforePrecompute # precompute values outside of for loop
        my_output += dc_for_inner_begin % (loopIterator[0], loopIterator[1], loopIterator[2])
        my_output += outputPrecompute # precompute values inside but before dot calculations
        for l in divConqLoopValStmtSig:
            my_output += l
        my_output += end_for_inner_loop + "\n"            
        
        print("Build inner For loop :=> ")
        print(my_output)
        return my_output
    
    def __constructSDLBatchOverSignaturesOnly(self, VarsForDotOverSigs, VarsForDotTypesOverSigs, VarsForDotASTOverSigs):
        secparamLine = self.__getSecParamLine()
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

#        print("Results over signatures...")
#        num_types = len(dotInitStmtDivConqSig)
#        for i in range(num_types):
#            print(i, ": ", dotInitStmtDivConqSig[i], end='')
#
#        num_types = len(divConqLoopValStmtSig)
#        for i in range(num_types):
#            print(i, ": ", divConqLoopValStmtSig[i], end='')

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
        return

    def __constructSDLBatchOverSignaturesAndSigners(self, VarsForDotOverSigs, VarsForDotTypesOverSigs, VarsForDotASTOverSigs, VarsForDotOverSign, VarsForDotTypesOverSign, VarsForDotASTOverSign):
        secparamLine = self.__getSecParamLine()
        refSignatureDict, refSignerDict = self.__searchForDependencies(VarsForDotASTOverSigs, VarsForDotASTOverSign)
#        print("refSignatureDict", refSignatureDict)
#        print("refSignerDict", refSignerDict)

        batchVerifyArgList = []
        _batchVerifyArgList = list(self.sdlData[BATCH_VERIFY].keys())
        for i in _batchVerifyArgList:
            if linkVar not in str(i):
                batchVerifyArgList.append(i)
        batchVerifyArgTypes = self.sdlData[BATCH_VERIFY]
        batchVerifyArgList.sort()
        print("batch: ", batchVerifyArgList, batchVerifyArgTypes)
        # get the membership list
        membershipTestList, outputLines1 = self.__generateMembershipTest(batchVerifyArgList, batchVerifyArgTypes)
        print("membership test ...")
        print("outputLines: ", outputLines1, end="\n\n")
        finalEqDotMap = {}
         
        dotLoopValTypesSig, dotCacheTypesSig, dotInitStmtDivConqSig, divConqLoopValStmtSig, dotVerifyEq, dotCacheCalc, dotList, dotCacheVarList, _divConqArgList = \
                          self.__createStatements(list(refSignatureDict.keys()), VarsForDotTypesOverSigs, VarsForDotASTOverSigs, sigIterator)        
        finalEqDotMap.update(dotVerifyEq)
                          
        for i in list(refSignerDict.keys()):
            if len(refSignerDict[i][0]) > 0 and str(refSignerDict[i][1]) == signerProd:
                print("\n\n\n")
                listForSigs = self.__createStatements(refSignerDict[i][0], VarsForDotTypesOverSigs, VarsForDotASTOverSigs, sigIterator, combineLoopAndCacheStmt=True)
                finalEqDotMap.update(listForSigs[4])

        dotList2 = listForSigs[6]
        listForSigner = self.__createStatementsNoCache(list(refSignerDict.keys()), VarsForDotTypesOverSign, VarsForDotASTOverSign, signerIterator, dotList2)
        finalEqDotMap.update(listForSigner[4])
        divConqArgList = self.newDeltaList + ["startSigNum", "endSigNum", "incorrectIndices"] + _divConqArgList + list(batchVerifyArgList)
        
        eqStr = str(self.finalBatchEq)
        for k,v in finalEqDotMap.items():
            eqStr = eqStr.replace(k, v)
        statementForSig = (dotInitStmtDivConqSig, divConqLoopValStmtSig, False)
        statementForSubSig = (listForSigs[2], listForSigs[3], False, listForSigs[7] + listForSigner[7])
        statementForSigner = (listForSigner[2], listForSigner[3], True, signatureProd, statementForSubSig)
        
        outputLines2 = self.__generateDivideAndConquerFlexible(eqStr, divConqArgList, self.callBackForDVSignerThenSignature, statementForSig, statementForSigner)
        
        outputLines3 = self.__generateBatchVerify(batchVerifyArgList, membershipTestList, divConqArgList, dotCacheCalc, dotCacheVarList)
        output = secparamLine + outputLines1 + outputLines2 + outputLines3
        
        dotLoopValTypesSig.update(listForSigs[0])
        dotCacheTypesSig.update(listForSigs[1])
        dotLoopValTypesSig.update(listForSigner[0])
        dotCacheTypesSig.update(listForSigner[1])

        typeOutputLines = self.__generateTypes(dotLoopValTypesSig, dotCacheTypesSig, batchVerifyArgTypes)
        self.printList("New type section", typeOutputLines)
        self.__generateNewSDL(typeOutputLines, output)


    def callBackForDVSignerThenSignature(self, output, statementForSig, statementForSigner):
        my_output = ""
        dotInitStmtDivConqSig, divConqLoopValStmtSig = statementForSig[0], statementForSig[1]
        for l in dotInitStmtDivConqSig:
            my_output += l
        my_output += dc_for_begin % (sigIterator, "startSigNum", "endSigNum")
        for l in divConqLoopValStmtSig:
            my_output += l
        my_output += end_for_loop + "\n\n"
        
        dotInitStmtDivConqSign, divConqLoopValStmtSign = statementForSigner[0], statementForSigner[1]
        for l in dotInitStmtDivConqSign:
            my_output += l
        my_output += dc_for_begin % (signerIterator, "0", "l")
        if statementForSigner[2] == True and statementForSigner[3] == signatureProd:
            # need to add sub stuff
            dotInitStmtDivConqSig, divConqLoopValStmtSig = statementForSigner[4][0], statementForSigner[4][1]
            dotCacheVarListForSigners = statementForSigner[4][3]
            outputBeforePrecompute, outputPrecompute = self.__generatePrecomputeLinesForDV(sigIterator, dotCacheVarListForSigners)
            for l in dotInitStmtDivConqSig:
                my_output += l
            my_output += outputBeforePrecompute # precompute values outside of for loop
            my_output += dc_for_inner_begin % (sigIterator, "startSigNum", "endSigNum")
            my_output += outputPrecompute # precompute values inside but before dot calculations
            for l in divConqLoopValStmtSig:
                my_output += l
            my_output += end_for_inner_loop + "\n"            
            
        for l in divConqLoopValStmtSign:
            my_output += l
        my_output += end_for_loop
        return my_output

    def printList(self, prefix, theList):
        print(prefix, "statements...")
        for i in theList:
            print("DEBUG: ", i)
        return
        
