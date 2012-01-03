import copy, os, sys
from ASTParser import *
from Parser_CodeGen_Toolbox import *
from LoopInfo import LoopInfo
from StringName import StringName
from PrecomputeVariable import PrecomputeVariable
from IntegerValue import IntegerValue
from Loop_Block_Toolbox import *
from OperationValue import OperationValue
from LoopBlock import LoopBlock

batchEqLoopVars = []
batchEqNotLoopVars = []
batchEqVars = None
batchVerFile = None
batchVerifierOutput = None
cachedCalcsToPassToDC = []
callListOfVerifyFuncs = None
finalBatchEq = None
finalBatchEqWithLoops = None
functionArgMappings = None
functionArgNames = None
functionNames = None
globalVars = []
indentationListVerifyLines = None
individualVerFile = None
lineInfo = None
lineNoOfFirstFunction = None
lineNosPerVar = None
loopBlocksForCachedCalculations = []
loopBlocksForNonCachedCalculations = []
loopInfo = []
loopNamesOfFinalBatchEq = []
loopsOuterNumSignatures = []
loopsOuterNotNumSignatures = []
linePairsOfVerifyFuncs = None
listVars = {}
loopVarGroupTypes = {}
numSpacesPerTab = None
numTabsOnVerifyLine = None
precomputeVars = []
pythonCodeLines = None
pythonCodeNode = None
var_varDependencies = None
varAssignments = None
verifyEqNode = None
verifyFuncArgs = None
verifyFuncNode = None
verifyLines = None
verifySigsFile = None
verifySigsPrereqs = None

'''
class ImportFromVisitor(ast.NodeVisitor):
	def __init__(self):
		self.lineNos = []

	def visit_ImportFrom(self, node):
		self.lineNos.append(node.lineno)

	def getImportFromLineNos(self):
		if (len(self.lineNos) == 0):
			return 0

		return self.lineNos

class GetBasicVariableTypes(ast.NodeVisitor):
	def __init__(self, namesList):
		self.variableTypes = {}
		self.namesList = namesList
		
	def visit_Assign(self, node):
		try:
			nodeName = node.targets[0].id
		except:
			return
		
		if nodeName not in self.namesList:
			return
		
		try:
			valueType = type(node.value).__name__
		except:
			return
		
		if (valueType == 'ListComp'):
			self.variableTypes[nodeName] = 'Subscript'
		else:
			self.variableTypes[nodeName] = 'NoSubscript'
			
	def getVariableTypesDict(self):
		return self.variableTypes

class GetKeysOfDictAssign(ast.NodeVisitor):
	def __init__(self, dictName):
		self.keys = {}
		self.dictName = dictName
		
	def visit_Assign(self, node):
		nodeName = ""
		
		try:
			nodeName = node.targets[0].id
		except:
			return
		
		if (nodeName != self.dictName):
			return

		nodeType = ""

		try:
			nodeType = type(node.value).__name__
		except:
			return
		
		if (nodeType != dictRepInAST):
			return
		
		if keysRepInAST not in node.value._fields:
			return
		
		keysList = node.value.keys
		
		for index in range(0, len(keysList)):
			if (stringRepInAST in node.value.keys[index]._fields):
				self.keys[index] = {}
				self.keys[index][typeRep] = stringRepInAST
				self.keys[index][valueRep] = node.value.keys[index].s
			elif (numRepInAST in node.value.keys[index]._fields):
				self.keys[index] = {}
				self.keys[index][typeRep] = numRepInAST
				self.keys[index][valueRep] = node.value.keys[index].n
				
	def getKeys(self):
		return self.keys


class BuildAssignMap(ast.NodeVisitor):
	def __init__(self):
		self.assignMap = {}
		
	def getName(self, node):
		if (idRepInAST in node._fields):
			name = node.id
			if name in reservedWords:
				return unknownType
			else:
				return name
		else:
			return unknownType

	def getAllIDs(self, node, allIDs):
		name = self.getName(node)
		if ( (name != unknownType) and (node.id not in allIDs) ):
			allIDs.append(node.id)
			return

		for childNode in ast.iter_child_nodes(node):
			self.getAllIDs(childNode, allIDs)
		
	def buildNameDictEntry(self, node):
		targetName = self.getName(node)
		if (targetName == unknownType):
			return
		if (targetName not in self.assignMap):
			self.assignMap[targetName] = {}		
		return targetName
		
	def buildValuesDictEntries(self, node, targetName):
		allIDs = []
		self.getAllIDs(node, allIDs)
		return allIDs

	def visit_Expr(self, node):
		try:
			targetName = node.value.func.value.id
		except:
			return
		
		targetName = self.buildNameDictEntry(node.value.func.value)
		if (targetName == unknownType):
			return
		
		#print(ast.dump(node))
		allIDs = self.buildValuesDictEntries(node.value, targetName)
		self.assignMap[targetName][node.lineno] = allIDs

	def visit_Assign(self, node):
		if (eltsRepInAST in node.targets[0]._fields):
			for eltsTargetIndex in range(0, len(node.targets[0].elts)):
				targetName = self.buildNameDictEntry(node.targets[0].elts[eltsTargetIndex])
				if (targetName == unknownType):
					return
				if (eltsRepInAST in node.value._fields):
					allIDs = self.buildValuesDictEntries(node.value.elts[eltsTargetIndex], targetName)
					self.assignMap[targetName][node.lineno] = allIDs
				elif (idRepInAST in node.value._fields):
					self.assignMap[targetName][node.lineno] = node.value.id
				
				
				#self.assignMap[targetName][node.lineno] = allIDs
		elif (idRepInAST in node.targets[0]._fields):
			targetName = self.buildNameDictEntry(node.targets[0])
			if (targetName == unknownType):
				return
			allIDs = self.buildValuesDictEntries(node.value, targetName)
			self.assignMap[targetName][node.lineno] = allIDs
		elif (sliceRepInAST in node.targets[0]._fields):
			targetName = self.buildNameDictEntry(node.targets[0].value)
			if (targetName == unknownType):
				return
			#print(targetName)
			#print(node.targets[0].slice._fields)
			#print(ast.dump(node))
			
			allIDs = self.buildValuesDictEntries(node.value, targetName)
			self.assignMap[targetName][node.lineno] = allIDs




		else:
			print(node.targets[0]._fields)
		#print(self.assignMap)
		
	def getAssignMap(self):
		if (len(self.assignMap) == 0):
			return {}
		
		return self.assignMap

class PrereqAssignVisitor(ast.NodeVisitor):
	def __init__(self):
		self.prereqAssignLineNos = []

	def visit_Assign(self, node):
		if (ast.dump(node.targets[0]).startswith('Name(')):
			if (idRepInAST in node.targets[0]._fields):
				if (type(node.value).__name__ == lambdaRepInAST):
					self.prereqAssignLineNos.append(node.lineno)
				elif (type(node.value).__name__ == callRepInAST):
					if (funcRepInAST in node.value._fields):
						if (idRepInAST in node.value.func._fields):
							if (node.value.func.id in pairFuncNames):
								self.prereqAssignLineNos.insert(0, node.lineno)

	def getPrereqAssignLineNos(self):
		return self.prereqAssignLineNos

class ASTVerifyFuncVisitor(ast.NodeVisitor):
	def __init__(self):
		self.verifyFunc = []

	def visit_FunctionDef(self, node):
		if (node.name == nameOfVerifyFunc):
			self.verifyFunc.append(node)

	def getVerifyFuncFromASTVisitor(self):
		if (len(self.verifyFunc) == 1):
			return self.verifyFunc[0]
		else:
			return []

class ASTEqCompareVisitor(ast.NodeVisitor):
	def __init__(self):
		self.eqCompareNodes = {}

	def visit_Compare(self, node):
		loopCounter = 0
		for childNode in ast.iter_child_nodes(node):
			if ( (loopCounter == 1) and (ast.dump(childNode) == equalityOperator) ):
				self.eqCompareNodes[node.lineno] = node
			loopCounter = loopCounter + 1
			if (loopCounter > 1):
				break

	def getLastEqOpFromVerify(self):
		if (len(self.eqCompareNodes) < 1):
			return 0
		lineNumsList = list(self.eqCompareNodes.keys())
		lineNumsList.sort()
		lineNumsList.reverse()
		return self.eqCompareNodes[lineNumsList[0]]



def isNextCharAlpha(line, currIndex):
	lastCharIndex = len(line) - 1
	if (currIndex == lastCharIndex):
		return False
	
	if (line[currIndex + 1].isalpha() == True):
		return True
	
	return False



def getVerifyEqNode(verifyFuncNode):
	astEqVisitor = ASTEqCompareVisitor()
	astEqVisitor.visit(verifyFuncNode)
	return astEqVisitor.getLastEqOpFromVerify()

def getVerifyFuncNode(astNode):
	astVerifyVisitor = ASTVerifyFuncVisitor()
	astVerifyVisitor.visit(astNode)
	return astVerifyVisitor.getVerifyFuncFromASTVisitor()

def getVerifyFuncArgs(verifyFuncNode):
	verifyFuncArgs = []
	if (argsRepInAST not in verifyFuncNode._fields):
		sys.exit("Could not locate arguments passed to \"verify\" function of signature scheme.")
	if (argsRepInAST not in verifyFuncNode.args._fields):
		sys.exit("Could not locate arguments passed to \"verify\" function of signature scheme.")

	numArgs = len(verifyFuncNode.args.args)
	for index in range(0, numArgs):
		if (argRepInAST not in verifyFuncNode.args.args[index]._fields):
			sys.exit("Could not locate arguments passed to \"verify\" function of signature scheme.")
		if (verifyFuncNode.args.args[index].arg != selfRepInAST):
			verifyFuncArgs.append(verifyFuncNode.args.args[index].arg)

	if (len(verifyFuncArgs) <= 0):
		sys.exit("Could not locate arguments passed to \"verify\" function of signature scheme.")

	return verifyFuncArgs

def removeLastCharNewline(buf):
	lenOfBuf = len(buf)
	lastChar = lenOfBuf - 1
	if (buf[lastChar] == 10):
		buf = buf[0:lastChar]

	return buf
'''


'''


def getImportFromLines(rootNode, codeLines):
	importVisitor = ImportFromVisitor()
	importVisitor.visit(rootNode)
	importLineNos = importVisitor.getImportFromLineNos()

	indentationList = []
	importFromLines = []

	for lineNo in importLineNos:
		importLineList = getLinesFromSourceCode(codeLines, lineNo, lineNo, indentationList)
		importFromLines.append(importLineList[0])

	if (len(importFromLines) == 0):
		return 0

	return importFromLines

def removeSelfDump(line):
	selfDumpIndex = line.find(selfDump)
	if (selfDumpIndex == -1):
		return line

	lenOfLine = len(line)
	line = line[0:selfDumpIndex] + line[(selfDumpIndex + selfDumpLen + 1):lenOfLine]
	line = line.rstrip(')')
	return line
'''

def cleanFinalBatchEq():
	global finalBatchEq
	
	finalBatchEq = finalBatchEq.replace(con.finalBatchEqString, '', 1)
	finalBatchEq = finalBatchEq.lstrip()	
	finalBatchEq = ensureSpacesBtwnTokens_CodeGen(finalBatchEq)

'''
def addDeltasAndArgSigIndexMap(batchOutputString, declaredLists):
	#batchOutputString += "\n\t" + deltaString + " = {}\n\n"
	
	#print(declaredLists)

	for declaredList in declaredLists:
		if (declaredList.startswith(deltaString) == True):
			deltaListSplit = declaredList.split("_")
			deltaList = deltaListSplit[0] + deltaListSplit[1]
			batchOutputString += "\tfor sigIndex in range(0, numSigs):\n"
			batchOutputString += "\t\t" + deltaList + "[sigIndex] = prng_bits(group, " + str(numBitsOfSecurity) + ")\n\n"
		
	return batchOutputString

def addIfElse(batchOutputString, finalBatchEq):
	finalBatchEq = finalBatchEq.rstrip()
	batchOutputString += "\tif " + finalBatchEq
	batchOutputString += " :\n"
	batchOutputString += "\t\tpass\n"
	batchOutputString += "\telse:\n"
	batchOutputString += "\t\tprint(\"Batch signature verification failed.\\n\")"
	return batchOutputString
'''

def getBatchEqVars():
	global batchEqVars

	batchEqVarsTemp = finalBatchEq.split()

	for removeString in con.batchEqRemoveStrings:
		while (batchEqVarsTemp.count(removeString) > 0):
			batchEqVarsTemp.remove(removeString)

	for dupVar in batchEqVarsTemp:
		while (batchEqVarsTemp.count(dupVar) > 1):
			batchEqVarsTemp.remove(dupVar)

	deltaVarsToRemove = []

	for deltaVar in batchEqVarsTemp:
		if ( (deltaVar == con.delta) or (deltaVar.startswith(con.delta + con.loopIndicator) == True) ):
			deltaVarsToRemove.append(deltaVar)

	for varToRemove in deltaVarsToRemove:
		batchEqVarsTemp.remove(varToRemove)

	batchEqVars = []

	for batchEqVarName in batchEqVarsTemp:
		batchEqVarStringName = StringName()
		batchEqVarStringName.setName(batchEqVarName)
		batchEqVars.append(copy.deepcopy(batchEqVarStringName))
		del batchEqVarStringName

def distillBatchEqVars():
	global batchEqLoopVars, batchEqNotLoopVars

	for varName in batchEqVars:
		isThisALoopVar = varName.getStringVarName().find(con.loopIndicator)
		if (isThisALoopVar == -1):
			batchEqNotLoopVars.append(copy.deepcopy(varName))
		else:
			batchEqLoopVars.append(copy.deepcopy(varName))

'''
def distillBatchEqVars(batchEqVars, batchEqNotSumOrDotVars):
	#batchEqDotProdVars = []
	
	for varIndex in range(0, len(batchEqVars)):
		sumOrDotSymbolIndex = batchEqVars[varIndex].find(sumOrDotSymbol)
		if (sumOrDotSymbolIndex == -1):
			batchEqNotSumOrDotVars.append(batchEqVars[varIndex])
		
		
		
		#if (dotProdSymbolIndex != -1):
			
			
			#batchEqDotProdVars.append(batchEqVars[varIndex][0:dotProdSymbolIndex])
		#else:
			#batchEqNotSumOrDotVars.append(batchEqVars[varIndex])
	#return batchEqDotProdVars

def getIndentedBlockIndex(listOfIndentedBlocks, lineNo):
	for counter in range(0, len(listOfIndentedBlocks)):
		indentedBlock = listOfIndentedBlocks[counter]
		startLineNo = indentedBlock[indentedBlockStartLineNo]
		endLineNo = indentedBlock[indentedBlockEndLineNo]
		if ( (lineNo >= startLineNo) and (lineNo <= endLineNo) ):
			#print(counter)
			return counter
		
	return -1

def addIndentedBlockDataToDotProdVars(indentedBlock, varsNeededForDotProds, lineNosNeededForDotProds, lastAssignLine):
	startLineNo = indentedBlock[indentedBlockStartLineNo]
	endLineNo = indentedBlock[indentedBlockEndLineNo]
	
	if ( (startLineNo - 1) > lastAssignLine):
		return
	
	for lineIndex in range( (startLineNo - 1) , (endLineNo + 1)):
		if lineIndex not in lineNosNeededForDotProds:
			lineNosNeededForDotProds.append(lineIndex)
			
	namesOfVarsInBlock = indentedBlock[indentedBlockVars]
	for nameOfVarsInBlock in namesOfVarsInBlock:
		if nameOfVarsInBlock not in varsNeededForDotProds:
			varsNeededForDotProds.append(nameOfVarsInBlock)

def getLastLineAssignOfVarGroup(varGroup, assignMap):	
	lastLineNo = 0
	
	for varName in varGroup:
		if varName not in assignMap:
			continue
		for lineNo in assignMap[varName]:
			if (lineNo > lastLineNo):
				lastLineNo = lineNo
	
	return lastLineNo

def getLastLineOfControlBlock(lastLine, listOfIndentedBlocks):
	
	for indentedBlock in listOfIndentedBlocks:
		startLineNo = indentedBlock[indentedBlockStartLineNo] - 1
		endLineNo = indentedBlock[indentedBlockEndLineNo]
		if ( (lastLine >= startLineNo) and (lastLine <= endLineNo) ):
			return endLineNo
		
	return lastLine

def getParentVarsRecursive(varName, varsForDotProduct, assignMap):
	if varName not in assignMap:
		return
	
	for lineNo in assignMap[varName]:
		for newVarName in assignMap[varName][lineNo]:
			if newVarName not in varsForDotProduct:
				varsForDotProduct.append(newVarName)
				getParentVarsRecursive(newVarName, varsForDotProduct, assignMap)


def getAllParentVars(varsForDotProduct, assignMap):
	varList = []
	
	for varName in varsForDotProduct:
		varList.append(varName)
	
	for varName in varList:
		getParentVarsRecursive(varName, varsForDotProduct, assignMap)

def getLinesForDotProd_OneVar(dotProdVarName, assignMap, listOfIndentedBlocks, lineNosNeededForDotProds):
	varsNeededForDotProds = []
	varsNeededForDotProds.append(dotProdVarName)

	lastAssignLine = 0

	if dotProdVarName not in assignMap:
		return lineNosNeededForDotProds
	
	lineNos = list(assignMap[dotProdVarName].keys())
	for lineNo in lineNos:
		if (lineNo > lastAssignLine):
			lastAssignLine = lineNo
		for varName in assignMap[dotProdVarName][lineNo]:
			if varName not in varsNeededForDotProds:
				varsNeededForDotProds.append(varName)

	tempVarsToAdd = []
					
	for varNeededForDotProds in varsNeededForDotProds:
		if varNeededForDotProds in assignMap:
			lineNos = list(assignMap[varNeededForDotProds].keys())
			for lineNo in lineNos:
				indentedBlockIndex = getIndentedBlockIndex(listOfIndentedBlocks, lineNo)
				if (indentedBlockIndex != -1):
					addIndentedBlockDataToDotProdVars(listOfIndentedBlocks[indentedBlockIndex], varsNeededForDotProds, lineNosNeededForDotProds, lastAssignLine)

	getAllParentVars(varsNeededForDotProds, assignMap)
	
	for varNeededForDotProds in varsNeededForDotProds:
		if varNeededForDotProds in assignMap:
			nextLines = list(assignMap[varNeededForDotProds].keys())
			for nextLine in nextLines:
				if ( (nextLine not in lineNosNeededForDotProds) and (nextLine <= lastAssignLine) ):
					lineNosNeededForDotProds.append(nextLine)

	return lineNosNeededForDotProds

def getLinesForDotProds(batchEqDotProdVars, assignMap, pythonCodeLines, listOfIndentedBlocks):
	varsNeededForDotProds = []
	lineNosNeededForDotProds = []
	linesForDotProds = []
	
	for batchEqVarName in batchEqDotProdVars:
		lineNosNeededForDotProds = getLinesForDotProd_OneVar(batchEqVarName, assignMap, listOfIndentedBlocks, lineNosNeededForDotProds)

	if (len(lineNosNeededForDotProds) == 0):
		return lineNosNeededForDotProds
		
	lineNosNeededForDotProds.sort()	
	lastLineAssignOfVarGroup = getLastLineAssignOfVarGroup(batchEqDotProdVars, assignMap)
	
	if (lastLineAssignOfVarGroup == 0):
		return lineNosNeededForDotProds
	
	lastLineOfControlBlock = getLastLineOfControlBlock(lastLineAssignOfVarGroup, listOfIndentedBlocks)
	totalNumOfLines = len(lineNosNeededForDotProds)
	
	for lineNo in range(0, totalNumOfLines):
		if (lineNosNeededForDotProds[lineNo] > lastLineOfControlBlock):
			break
		
	if (lineNo < (totalNumOfLines - 1) ):
		for lineIndex in range(lineNo, totalNumOfLines):
			lineNosNeededForDotProds.remove(lineNosNeededForDotProds[lineIndex])
	
	return lineNosNeededForDotProds

def determineNumSpacesBeforeText(line):
	if (line[0] != ' '):
		return 0
	
	numSpaces = 0
	
	for index in range(0, len(line)):
		if (line[index] == ' '):
			numSpaces += 1
		else:
			return numSpaces
			
	return numSpaces

def getVarsOfLine(linesOfCode, lineNo):
	if (lineNo == -1):
		line = linesOfCode
	else:
		line = linesOfCode[lineNo - 1]
	
	line = line.lstrip().rstrip().rstrip('\n')
	if ( (line.startswith(commentChar)) or (line == "") ):
		return []
	line = ensureSpacesBtwnTokens(line)

	vars = []
	
	for token in line.split():
		if ( (token not in reservedSymbols) and (token not in reservedWords) and (token.isdigit() == False) ):
			vars.append(token)

	#print(vars)			
	return vars

def buildMapOfControlFlow(pythonCodeLines, funcDefLineNo, endLineNo):
	withinIndentedBlock = False
	indentedBlockPairs = []
	
	for lineIndex in range(0, len(pythonCodeLines)):
		realLineNo = lineIndex + 1
		lineWithNoSpaces = pythonCodeLines[lineIndex].lstrip().rstrip()
		
		if (realLineNo < funcDefLineNo):
			continue
		elif (realLineNo > endLineNo):
			break
		elif (realLineNo == funcDefLineNo):
			baseNumSpacesBeforeText = determineNumSpacesBeforeText(pythonCodeLines[lineIndex]) + numSpacesPerTab
		elif ( (lineWithNoSpaces.startswith(commentChar)) or (lineWithNoSpaces == "") ):
			continue
		else:
			numSpacesBeforeText = determineNumSpacesBeforeText(pythonCodeLines[lineIndex])
			if (withinIndentedBlock == True):
				if (numSpacesBeforeText == baseNumSpacesBeforeText):
					withinIndentedBlock = False
					indentedBlockPairs.append(realLineNo - 1)
			else:
				if (numSpacesBeforeText == (baseNumSpacesBeforeText + numSpacesPerTab) ):
					withinIndentedBlock = True
					indentedBlockPairs.append(realLineNo)
					
	if ( (len(indentedBlockPairs) % 2) == 1):
		indentedBlockPairs.append(endLineNo)
		
	listOfIndentedBlocks = []
	indentedBlockDict = {}
	numIndentedBlocks = int(len(indentedBlockPairs) / 2)
	
	for indentedBlockIndex in range(0, numIndentedBlocks):
		indentedBlockDict[indentedBlockStartLineNo] = indentedBlockPairs[indentedBlockIndex * 2]
		indentedStart = indentedBlockDict[indentedBlockStartLineNo]
		indentedBlockDict[indentedBlockEndLineNo] = indentedBlockPairs[(indentedBlockIndex * 2) + 1]
		indentedEnd = indentedBlockDict[indentedBlockEndLineNo]
		varsInBlock = []
		for indentedLineNo in range( (indentedStart - 1), (indentedEnd + 1) ):
			varsOfLine = getVarsOfLine(pythonCodeLines, indentedLineNo)
			if (varsOfLine != []):
				for varOfLine in varsOfLine:
					if varOfLine not in varsInBlock:
						varsInBlock.append(varOfLine)
		indentedBlockDict[indentedBlockVars] = varsInBlock
		listOfIndentedBlocks.append(copy.deepcopy(indentedBlockDict))
		
	#print(listOfIndentedBlocks)
	return listOfIndentedBlocks

def getComputeLineVars(exp):
	varList = []
	
	exp = ensureSpacesBtwnTokens(exp)
	for token in exp.split():
		if ( (token not in reservedWords) and (token not in reservedSymbols) and (token not in varList) ):
			varList.append(token)
			
	return varList

def checkForPrecomputeValues(exp):
	exp = ensureSpacesBtwnTokens(exp)
	expSplit = exp.split()
	for token in expSplit:
		if token in precomputeVarReplacements:
			replacementString = precomputeVarReplacements[token]
			replacementString = replacementString.replace(multipleSubscriptIndicatorChar, '')
			replacementString = ' ' + replacementString + ' '
			tokenWithSpaces = ' ' + token + ' '
			exp = exp.replace(tokenWithSpaces, replacementString, 1)


	
			#if tempStringExp in precomputeVarReplacements:
				#tempStringExp = precomputeVarReplacements[tempStringExp]
				#tempStringExp = tempStringExp.replace(multipleSubscriptIndicatorChar, '')

	return exp
'''

def processComputeLine(line):
	global loopInfo

	if ( (line == None) or (type(line).__name__ != con.strTypePython) or (len(line) == 0) or (line.startswith(con.computeString) == False) ):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  problem with line passed in (" + line + ").")

	line = line.lstrip().rstrip()
	line = line.replace(con.computeString, '', 1)
	splitOnAssignment = line.split(con.batchVerifierOutputAssignment, 1)
	loopName = splitOnAssignment[0]
	fullExpression = splitOnAssignment[1].rstrip(con.newLineChar)
	if ( (fullExpression.count(con.dotDirector) == 1) and (fullExpression.count(con.sumDirector) == 0) ):
		splitExpression = fullExpression.split(con.dotDirector, 1)
	elif ( (fullExpression.count(con.dotDirector) == 0) and (fullExpression.count(con.sumDirector) == 1) ):
		splitExpression = fullExpression.split(con.sumDirector, 1)
	else:
		sys.exit("AutoBatch_CodeGen->processComputeLine:  compute line did not have only one " + con.dotDirector + " OR only one " + con.sumDirector + ".")

	loopDeclaration = splitExpression[0]
	initialExpression = splitExpression[1]

	if ( (loopDeclaration.count(',') != 1) or (loopDeclaration.count('}') != 1) ):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  loop declaration is improperly formatted.")

	commaLocation = loopDeclaration.find(',')
	rightCurlyBraceLocation = loopDeclaration.find('}')

	loopOverValue = loopDeclaration[(commaLocation + 1):rightCurlyBraceLocation].lstrip().rstrip()

	if (loopDeclaration.count(con.batchVerifierOutputAssignment) != 1):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  loop declaration is improperly formatted (not only one " + con.batchVerifierOutputAssignment + " symbol).")

	splitLoopDecl = loopDeclaration.split(con.batchVerifierOutputAssignment, 1)
	indexVarExp = splitLoopDecl[0]
	startValExp = splitLoopDecl[1]

	if (indexVarExp.count('{') != 1):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  index variable expression is improperly formatted (not only one \'{\' symbol.")

	leftCurlyBraceLocation = indexVarExp.find('{')
	indexVar = indexVarExp[(leftCurlyBraceLocation + 1):len(indexVarExp)]
	indexVar = indexVar.lstrip().rstrip()

	indexVarStringName = StringName()
	indexVarStringName.setName(indexVar)

	if (startValExp.count(',') != 1):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  start value expression is improperly formatted (not only one \',\' symbol.")

	commaLocation = startValExp.find(',')

	startVal = startValExp[0:commaLocation]
	startVal = startVal.lstrip().rstrip()

	initialExpression = initialExpression.lstrip().rstrip()
	lenInitExp = len(initialExpression)
	if (initialExpression[lenInitExp-1] == ')'):
		initialExpression = initialExpression[0:(lenInitExp-1)]

	expression = initialExpression.lstrip().rstrip()

	varListWithSubscripts = getVarNamesAsStringNamesFromLine(expression)

	varListAsStrings = getVarNamesAsStringsFromLine(expression)
	loopOrder = getLoopOrder(varListAsStrings)
	varListNoSubscripts = removeSubscriptsReturnStringNames(varListAsStrings)

	operationStringValue = returnOperationAsStringValue(loopName)
	if ( (operationStringValue == None) or (type(operationStringValue).__name__ != con.stringValue) ):
		sys.exit("AutoBatch_CodeGen->processComputeLine:  could not extract the operation value of one of the loops parsed from the batcher output.")

	myOperationValue = OperationValue()
	myOperationValue.setOperation(operationStringValue)

	loopNameStringName = StringName()
	loopNameStringName.setName(loopName)

	startValIntegerValue = IntegerValue()
	startValIntegerValue.setValue(int(startVal))

	loopOverValueStringName = StringName()
	loopOverValueStringName.setName(loopOverValue)

	expressionAsStringValue = StringValue()
	expressionAsStringValue.setValue(expression)

	nextLoopInfoObj = LoopInfo()
	nextLoopInfoObj.setLoopName(loopNameStringName)
	nextLoopInfoObj.setIndexVariable(indexVarStringName)
	nextLoopInfoObj.setStartValue(startValIntegerValue)
	nextLoopInfoObj.setLoopOverValue(loopOverValueStringName)
	nextLoopInfoObj.setOperation(myOperationValue)
	nextLoopInfoObj.setExpression(expressionAsStringValue)
	nextLoopInfoObj.setVarListWithSubscripts(varListWithSubscripts)
	nextLoopInfoObj.setVarListNoSubscripts(varListNoSubscripts)
	nextLoopInfoObj.setLoopOrder(loopOrder)

	loopInfo.append(copy.deepcopy(nextLoopInfoObj))


'''		
def getComputeLineInfo(batchVerifierOutput):
	computeLineInfo = {}
	
	for line in batchVerifierOutput:
		if (line.startswith(computeLineString)):
			line = line.replace(computeLineString, '', 1)
			line = line.replace(multipleSubscriptIndicatorChar, '')
			dotProdLine = line.split(dotProdAssignSymbol, 1)
			key = dotProdLine[0]
			initValue = dotProdLine[1].rstrip('\n')
			computeLineInfo[key] = {}
			tempString = initValue.split(dotProdAssignSymbol)
			tempStringIndexVar = tempString[0].split('{')
			computeLineInfo[key][computeLineIndex] = tempStringIndexVar[1]
			tempString = tempString[1].split('}')
			tempStringStartEndVals = tempString[0].split(',')
			computeLineInfo[key][computeLineStartValue] = tempStringStartEndVals[0]
			computeLineInfo[key][computeLineEndValue] = tempStringStartEndVals[1]
			computeLineInfo[key][computeLineRange] = str(computeLineInfo[key][computeLineIndex]) + str(computeLineInfo[key][computeLineStartValue]) + str(computeLineInfo[key][computeLineEndValue])
			if (' on ' in tempString[1]):
				tempString = tempString[1].split(' on ')
			elif (' of ' in tempString[1]):
				tempString = tempString[1].split(' of ')
			tempStringExp = tempString[1]			
			lenTempStringExp = len(tempStringExp)
			tempStringExp = tempStringExp[0:(lenTempStringExp - 1)]

			#tempStringExp = checkForPrecomputeValues(tempStringExp)

			computeLineInfo[key][computeLineExp] = tempStringExp			
			computeLineInfo[key][computeLineVars] = getComputeLineVars( computeLineInfo[key][computeLineExp] )
			varNames = computeLineInfo[key][computeLineVars]
			varNamesNoSubscripts = []
			for varName in varNames:
				varNameSplit = varName.split(dotProdSymbol)
				varNamesNoSubscripts.append(varNameSplit[0])
				cleanBatchEqVars[varNameSplit[0]] = 0
			computeLineInfo[key][computeLineVarsNoSubscripts] = varNamesNoSubscripts

	return computeLineInfo

def doesVarNeedList(varName, verifyFuncArgs):
	if ( (varName == 'i') or (varName == 'j') ):
		return False
	
	if (varName in verifyFuncArgs):
		return False
	
	if (   ( (varName.startswith(dotProdPrefix)) or (varName.startswith(sumPrefix))  ) and (len(varName) == 4)):
		return False
	
	return True

def addListDeclarations(batchOutputString, computeLineInfo, verifyFuncArgs, declaredLists):
	listVars = []
	dotProdListNames = []

	#print(computeLineInfo)
	
	batchOutputString += "\n"
	
	for key in computeLineInfo:
		if key not in dotProdListNames:
			dotProdListNames.append(key)
		for varIndex in range(0, len(computeLineInfo[key][computeLineVars])):
			varName = computeLineInfo[key][computeLineVars][varIndex]
			varNameNoSubscript = computeLineInfo[key][computeLineVarsNoSubscripts][varIndex]
			#if (varNameNoSubscript.startswith(deltaString) == True):
				#print(varName)
				#continue

			if (varNameNoSubscript == deltaString):
				if varName not in listVars:
					listVars.append(varName)
			
			#needsList = doesVarNeedList(varNameNoSubscript, verifyFuncArgs)
			#if (needsList == True):
				#if varName not in listVars:
					#listVars.append(varName)
					
	for listVar in listVars:
		listVarSplit = listVar.split(dotProdSymbol)
		listVarName = listVarSplit[0]
		listVarSuffixes = listVarSplit[1]
		
		lenOfSuffixes = len(listVarSuffixes)
		suffix = listVarSuffixes[lenOfSuffixes - 1]
		
		#suffixes = ""
		#for listVarSuffix in listVarSuffixes:
			#suffixes += listVarSuffix
			
		batchOutputString += "\t" + listVarName + suffix + " = {}\n"
		declaredListEntry = listVarName + "_" + suffix
		if declaredListEntry not in declaredLists:
			declaredLists.append(declaredListEntry)

	for dotProdListName in dotProdListNames:
		batchOutputString += "\t" + dotProdListName + " = {}\n"
		if dotProdListName not in declaredLists:
			declaredLists.append(dotProdListName) #IS THIS A PROBLEM?

		#if ( (dotProdListName.startswith(dotProdPrefix)) and (len(dotProdListName) == 4) ):
			#batchOutputString += "\t" + dotProdListName + "_runningProduct = 1\n"

	batchOutputString += "\n"

	#declaredLists.append(deltaString)

	#print(dotProdListNames)

	return batchOutputString

def getOuterDotProds(batchVerifierOutput):
	outerDotProds = []

	for line in batchVerifierOutput:
		if (line.startswith(finalEqLineString)):
			break

	line = line.replace(finalEqLineString, '', 1)
		
	line = ensureSpacesBtwnTokens(line)
	
	line = line.split()
	
	for token in line:
		if ( ( (token.startswith(dotProdPrefix) == True) or (token.startswith(sumPrefix) == True)) and (len(token) == 4) ):
			if (token not in outerDotProds):
				outerDotProds.append(token)
		elif ( (token not in reservedWords) and (token not in reservedSymbols) ):
			if (token not in finalEqLineVars):
				finalEqLineVars.append(token)
			
	
	return outerDotProds

def cleanVarsForDotProds(varsForDotProds):
	#print("this is it")
	#print(varsForDotProds)
	if (varsForDotProds.count(deltaString) > 0):
		varsForDotProds.remove(deltaString)
	
	varsToRemove = []
	
	for var in varsForDotProds:
		if (    ( (var.startswith(dotProdPrefix)) or (var.startswith(sumPrefix)  )   ) and (len(var) == 4) ):
			varsToRemove.append(var)
			
	for var in varsToRemove:
		varsForDotProds.remove(var)
		
	for var in varsForDotProds:
		while (varsForDotProds.count(var) > 1):
			varsForDotProds.remove(var)
		

def getListNameFromDeclaredLists(listName):
	if (listName.count("_") == 0):
		return listName
	
	listName = listName.split("_")
	return listName[0]

def getSuffixesFromDeclaredLists(listName):
	if (listName.count("_") == 0):
		return None
	
	listName = listName.split("_")
	return listName[1]

def getDotProdCalcStringForNumSigners(expression, listNamesToReplacementStrings, indexVar):
	expression = ensureSpacesBtwnTokens(expression)
	expressionSplit = expression.split()
	
	for token in expressionSplit:
		if (token.count("_") == 1):
			tokenSplit = token.split("_")
			listName = tokenSplit[0]
			if listName in listNamesToReplacementStrings:
				replacementString = listNamesToReplacementStrings[listName] + "[" + indexVar + "]"
			elif (listName == deltaString):
				replacementString = listName + indexVar + "[" + indexVar + "] "
			else:
				continue
			tokenWithSpaces = ' ' + token + ' '
			replacementString = ' ' + replacementString + ' '
			expression = expression.replace(tokenWithSpaces, replacementString, 1)			
		elif (   (  (token.startswith(dotProdPrefix)) or ( token.startswith(sumPrefix)  )    ) and (len(token) == 4) ):
			replacementStringForRunningProd = token + "_runningProduct"
			tokenWithSpaces = ' ' + token + ' '
			replacementStringForRunningProd = ' ' + replacementStringForRunningProd + ' '
			expression = expression.replace(tokenWithSpaces, replacementStringForRunningProd, 1)

	expression = expression.replace(" ^ ", " ** ")	
	return expression




def getSliceNameFromAST(dictName, sliceIndex):

	sliceIndex = int(sliceIndex)
	
	getKeysVar = GetKeysOfDictAssign(dictName)
	getKeysVar.visit(pythonCodeNode)
	keysDict = getKeysVar.getKeys()
	if (keysDict[sliceIndex][typeRep] == stringRepInAST):
		return "\'" + keysDict[sliceIndex][valueRep] + "\'"
	if (keysDict[sliceIndex][typeRep] == numRepInAST):
		return str(keysDict[sliceIndex][valueRep])
				

	return ""
				








def getDotProdCalcString(expression, listNamesToReplacementStrings, indexVar, verifyFuncArgs):
	expression = ensureSpacesBtwnTokens(expression)
	expressionSplit = expression.split()

	#expression = expression.replace(" e ", " pair ")
	
	for token in expressionSplit:
		if (token.count("_") == 1):
			tokenSplit = token.split("_")
			listName = tokenSplit[0]
			
			if (listName == deltaString):
				replacementString = listName + numSignaturesIndex + "[" + numSignaturesIndex + "]"
			
			
			elif listName in listNamesToReplacementStrings:
				replacementString = listNamesToReplacementStrings[listName] + "[" + indexVar + "]"


			elif listName in verifyFuncArgs:
				replacementString = "verifyArgsDict[argSigIndexMap[\'" + listName + "\']][\'" + listName + "\'][bodyKey]"
			#	expression = expression.replace(token, replacementString, 1)

				
			else:
				if (listName in varsThatAreLists):
					if (listName.find(newSliceSymbol) != -1):
						listNameSplit = listName.split(newSliceSymbol)
						
						sliceNameFromAST = getSliceNameFromAST(listNameSplit[0], listNameSplit[1][0])
						
						
						if (listNameSplit[0] in verifyFuncArgs):
							replacementString = " verifyArgsDict[argSigIndexMap[\'" + listNameSplit[0] + "\']][\'" + listNameSplit[0] + "\'][bodyKey]"
							replacementString += "[" + sliceNameFromAST + "]"
							replacementString += "[" + varsThatAreLists[listName] + "]"
						else:
							replacementString = listNameSplit[0] + "[" + sliceNameFromAST + "]"
							replacementString += "[" + varsThatAreLists[listName] + "]"
					else:
						replacementString = listName + "[" + varsThatAreLists[listName] + "]"
				else:
					replacementString = listName
			tokenWithSpaces = ' ' + token + ' '
			replacementString = ' ' + replacementString + ' '
			expression = expression.replace(tokenWithSpaces, replacementString, 1)			
		elif ( ( (token.startswith(dotProdPrefix)) or (token.startswith(sumPrefix))  ) and (len(token) == 4) ):
			replacementStringForRunningProd = token + "_runningProduct"
			tokenWithSpaces = ' ' + token + ' '
			replacementStringForRunningProd = ' ' + replacementStringForRunningProd + ' '
			expression = expression.replace(tokenWithSpaces, replacementStringForRunningProd, 1)
		elif token in verifyFuncArgs:
			replacementString = " verifyArgsDict[argSigIndexMap[\'" + token + "\']][\'" + token + "\'][bodyKey] "
			tokenWithSpaces = ' ' + token + ' '
			expression = expression.replace(tokenWithSpaces, replacementString, 1)

	expression = expression.replace(" ^ ", " ** ")	
	expression = expression.replace(" e ", " pair ")
	return expression

def writeDotProdIndicesString(indexVarsOfDotProdsInOrder):

	if (numSignaturesIndex not in indexVarsOfDotProdsInOrder):
		return ""

	if (len(indexVarsOfDotProdsInOrder) == 1) and (indexVarsOfDotProdsInOrder[0] == numSignaturesIndex):
		return "[" + numSignaturesIndex + "]"


	return "[" + numSignaturesIndex + "]"
		
	return indexString
		

def writeDotProdCalculations(batchOutputString, writeDotProdLines, computeLineInfo, listNamesToReplacementStrings, indexVar, numTabs, dotProdListName, outerDotProds, verifyFuncArgs, precomputeVarsDefinedSoFar, indexVarsOfDotProdsInOrder):

	computeVarNames = computeLineInfo[dotProdListName][computeLineVars]
	for computeVarName in computeVarNames:
		if (writeDotProdLines == False):
			continue
		if computeVarName not in precomputeVarReplacements:
			continue
		if computeVarName in precomputeVarsDefinedSoFar:
			continue
		precomputeExp = precomputeVarReplacements[computeVarName]
		precomputeDotProdCalcString = getDotProdCalcString(precomputeExp, listNamesToReplacementStrings, indexVar, verifyFuncArgs)
		precomputeVarNameSplit = computeVarName.split(sumOrDotSymbol)
		precomputeVarNameNoSubscript = precomputeVarNameSplit[0]
		for tabNumber in range(0, numTabs):
			batchOutputString += "\t"
		batchOutputString += precomputeVarNameNoSubscript + " = " + precomputeDotProdCalcString + "\n\n"
		precomputeVarsDefinedSoFar.append(computeVarName)
			

	dotProdCalcString = getDotProdCalcString(computeLineInfo[dotProdListName][computeLineExp], listNamesToReplacementStrings, indexVar, verifyFuncArgs)

	if (dotProdCalcString != ""):
		indexString = writeDotProdIndicesString(indexVarsOfDotProdsInOrder)

		if (writeDotProdLines == True): #or (dotProdListName in outerDotProds):			
			for tabNumber in range(0, numTabs):
				batchOutputString += "\t"
			batchOutputString += dotProdListName + indexString + " = " + dotProdCalcString + "\n"
		
		
		
		#if ( (dotProdListName not in outerDotProds) and (writeDotProdLines == True) ) or ( (writeDotProdLines == False) and (indexVar == numSignaturesIndex) ):
			
			
			
			
		if ( (dotProdListName not in precomputeOuterDotProds) and (writeDotProdLines == True) ) or ( (writeDotProdLines == False) and (indexVar == numSignaturesIndex) and (dotProdListName in outerDotProds) ):	
			for tabNumber in range(0, numTabs):
				batchOutputString += "\t"
			if (dotProdListName.startswith(dotProdPrefix) == True):	
				batchOutputString += dotProdListName + "_runningProduct = " + dotProdListName + "_runningProduct * " + dotProdListName + indexString + "\n"
			elif (dotProdListName.startswith(sumPrefix) == True):
				batchOutputString += dotProdListName + "_runningProduct = " + dotProdListName + "_runningProduct + " + dotProdListName + indexString + "\n"
				
		elif ( (writeDotProdLines == False) and (indexVar != numSignaturesIndex) ) or ( (writeDotProdLines == False) and (dotProdListName not in outerDotProds)    ):
			for tabNumber in range(0, numTabs):
				batchOutputString += "\t"
			if (dotProdListName.startswith(dotProdPrefix) == True):	
				batchOutputString += dotProdListName + "_runningProduct = " + dotProdListName + "_runningProduct * " + dotProdCalcString + "\n"
			elif (dotProdListName.startswith(sumPrefix) == True):
				batchOutputString += dotProdListName + "_runningProduct = " + dotProdListName + "_runningProduct + " + dotProdCalcString + "\n"



		
	batchOutputString += "\n"		
	
	return batchOutputString

def writeDotProdLinesToFile(batchOutputString, computeLineInfo, pythonCodeLines, linesForDotProds, baseNumTabs, numTabsBeforeVerify, verifyFuncArgs, declaredLists, indexVar, dotProdListName, listNamesToReplacementStrings):
	#print(declaredLists)

	numTabs = -1
	
	#listNamesToReplacementStrings = {}
	
	for lineNo in linesForDotProds:
		line = pythonCodeLines[lineNo - 1]
		if (line.lstrip().rstrip().startswith(commentChar) == True):
			continue
		if (line.lstrip().rstrip() == ""):
			continue		
		numSpacesBeforeText = determineNumSpacesBeforeText(line)
		numTabsBeforeText = determineNumTabs(numSpacesBeforeText)
		extraTabsNeeded = numTabsBeforeText - numTabsBeforeVerify - 1		
		line = ensureSpacesBtwnTokens(line)
		
		
		for arg in verifyFuncArgs:
			argWithSpaces = ' ' + arg + ' '
			numArgMatches = line.count(argWithSpaces)
			for countIndex in range(0, numArgMatches):				
				indexOfCharAfterArg = line.index(argWithSpaces) + len(argWithSpaces)
				if (indexOfCharAfterArg < len(line)):
					charAfterArg = line[indexOfCharAfterArg]
				else:
					charAfterArg = ''
				replacementString = " verifyArgsDict[argSigIndexMap[\'" + arg + "\']][\'" + arg + "\'][bodyKey]"
				if (charAfterArg == dictBeginChar):
					line = line.replace(argWithSpaces + '[', replacementString + '[', 1)
				else:
					line = line.replace(argWithSpaces, replacementString + ' ', 1)		
					
		for listName in declaredLists:
			listName = getListNameFromDeclaredLists(listName)
			#print(listName)
			listWithSpaces = ' ' + listName + ' '
			numListMatches = line.count(listWithSpaces)
			replacementString = listName + indexVar + "[" + indexVar + "] "
			#print(replacementString)
			
			listNamesToReplacementStrings[listName] = replacementString
			
			for countIndex in range(0, numListMatches):
				line = line.replace(listWithSpaces, replacementString, 1)
					
		line = line.lstrip().rstrip()
		line = removeLeftParanSpaces(line)		
		line = removeSelfDump(line)
		numTabs = baseNumTabs + extraTabsNeeded		
		for tabNumber in range(0, numTabs):
			batchOutputString += "\t"
		batchOutputString += line + "\n"

	batchOutputString += "\n"

	#if (listToReplacementCopy != None):
		#for listToRepKey in listNamesToReplacementStrings:
			#listToReplacementCopy[listToRepKey] = listNamesToReplacementStrings[listToRepKey] 

	#if (dotProdListName == None):
	batchOutputString += "\n"
		#return batchOutputString
		
	return batchOutputString

def addTabsToFile(file, numTabsToAdd):
	for tab in range(0, numTabsToAdd):
		file += "\t"
	
	return file

def setUpVerifyFuncArgs(batchOutputString, numTabs, indexVar):
	batchOutputString = addTabsToFile(batchOutputString, numTabs)
	batchOutputString += "for arg in verifyFuncArgs:\n"
	batchOutputString = addTabsToFile(batchOutputString, numTabs + 1)
	batchOutputString += "if (sigNumKey in verifyArgsDict[" + indexVar + "][arg]):\n"
	batchOutputString = addTabsToFile(batchOutputString, numTabs + 2)
	batchOutputString += "argSigIndexMap[arg] = int(verifyArgsDict[" + indexVar + "][arg][sigNumKey])\n"
	batchOutputString = addTabsToFile(batchOutputString, numTabs + 1)
	batchOutputString += "else:\n"
	batchOutputString = addTabsToFile(batchOutputString, numTabs + 2)
	batchOutputString += "argSigIndexMap[arg] = " + indexVar + "\n\n"
		
	return batchOutputString

def addResetStatementsForDotProdCalcs(batchOutputString, dotProdList, numTabs):
	#for tab in range(0, numTabs):
		#batchOutputString += "\t"

	#print(dotProdList)

	for key in dotProdList:
		for child in dotProdList[key]:
			if (type(child).__name__ != pythonDictRep) and (len(child) == 4):
				if (child.startswith(dotProdPrefix)):				
					for tab in range(0, numTabs):
						batchOutputString += "\t"
					batchOutputString += child + "_runningProduct = group.init(" + dotProdTypes[child] + ", 1)\n"
				elif (child.startswith(sumPrefix)):
					for tab in range(0, numTabs):
						batchOutputString += "\t"
					batchOutputString += child + "_runningProduct = group.init(" + dotProdTypes[child] + ", 0)\n"
	
	return batchOutputString

def writeNumSignersLoop(batchOutputString, numTabs, numTabsBeforeVerify, verifyFuncArgs, declaredLists, pythonCodeLines, listOfIndentedBlocks, indexVar, parentIndexVar, startVal, endVal, dotProdName, computeLineInfo, assignMap):
	listNamesToReplacementStrings = {}

	for tabNumber in range(0, numTabs):
		batchOutputString += "\t"
		
	batchOutputString += dotProdName + "[" + parentIndexVar + "] = {}\n"
	
	varsForDotProds = computeLineInfo[dotProdName][computeLineVarsNoSubscripts]			
	cleanVarsForDotProds(varsForDotProds)			
	linesForDotProds = getLinesForDotProds(varsForDotProds, assignMap, pythonCodeLines, listOfIndentedBlocks)
	
	listNamesToReplacementStrings = {}
	
	batchOutputString = writeDotProdLinesToFile(batchOutputString, computeLineInfo, pythonCodeLines, linesForDotProds, numTabs, numTabsBeforeVerify, verifyFuncArgs, declaredLists, parentIndexVar, None, listNamesToReplacementStrings)
	batchOutputString = writeDotProdCalculations(batchOutputString, computeLineInfo, listNamesToReplacementStrings, indexVar, numTabs, dotProdName)

	dotProdCalcString = getDotProdCalcStringForNumSigners(computeLineInfo[dotProdName][computeLineExp], listNamesToReplacementStrings, indexVar)

	for tabNumber in range(0, numTabs):
		batchOutputString += "\t"

	batchOutputString += "for " + indexVar + " in range(0, " + endVal + "):\n"

	for tabNumber in range(0, (numTabs+1)):
		batchOutputString += "\t"
			
	batchOutputString += dotProdName + "[" + parentIndexVar + "][" + indexVar + "] = " + dotProdCalcString + "\n"
		
	for tabNumber in range(0, (numTabs+1)):
		batchOutputString += "\t"

	if (dotProdName.startswith(dotProdPrefix) == True):
		batchOutputString += dotProdName + "_runningProduct = " + dotProdName + "_runningProduct * " + dotProdName + "[" + parentIndexVar + "][" + indexVar + "]\n"
	elif (dotProdName.startswith(sumPrefix) == True):
		batchOutputString += dotProdName + "_runningProduct = " + dotProdName + "_runningProduct + " + dotProdName + "[" + parentIndexVar + "][" + indexVar + "]\n"


		
	batchOutputString += "\n"		
	
	return batchOutputString

def cleanPrecomputeVars(vars):
	varsToRemove = []
	varsToAdd = []
	
	for var in vars:
		if (var.startswith(deltaString)):
			varsToRemove.append(var)
			continue
		if (var.count(sumOrDotSymbol) == 1):
			varSplit = var.split(sumOrDotSymbol)
			varsToAdd.append(varSplit[0])
			varsToRemove.append(var)
			continue
		
	for varName in varsToRemove:
		vars.remove(varName)
		
	for varName in varsToAdd:
		vars.append(varName)

def getVarsForDotProds(dotProdNames, computeLineInfo, varsForDotProds):
	#varsForDotProds = []

	#for key in dotProdNames:
		#range = key
		#break
	
	for child in dotProdNames:
		if ( (type(child).__name__ != pythonDictRep) and  (   (child.startswith(dotProdPrefix)) or (child.startswith(sumPrefix))      ) and (len(child) == 4) ):

			for varName in computeLineInfo[child][computeLineVars]:
				if varName in precomputeVarReplacements:
					precomputeExp = precomputeVarReplacements[varName]
					precomputeVars = getVarsOfLine(precomputeExp, -1)
					cleanPrecomputeVars(precomputeVars)
					for precomputeVarName in precomputeVars:
						if precomputeVarName not in varsForDotProds:
							varsForDotProds.append(precomputeVarName)

			currVars = computeLineInfo[child][computeLineVarsNoSubscripts]				
			for varName in currVars:
				if varName not in varsForDotProds:
					varsForDotProds.append(varName)
		elif (type(child).__name__ == pythonDictRep):
			for key in child:
				newListKey = key
				break
			getVarsForDotProds(child[newListKey], computeLineInfo, varsForDotProds)
			
	#cleanVarsForDotProds(varsForDotProds)
	
	#return varsForDotProds

def addDotProdLoopRecursive(batchOutputString, writeDotProdLines, computeLineInfo, dotProdList, assignMap, pythonCodeLines, listOfIndentedBlock, numTabs, numTabsBeforeVerify, verifyFuncArgs, declaredLists, parentIndexVar, listNamesToReplacementStrings, outerDotProds, topLevelDotProd, indexVarsOfDotProdsInOrder):
	for key in dotProdList:
		dotProdRange = key
		break

	batchOutputString = addResetStatementsForDotProdCalcs(batchOutputString, dotProdList, numTabs)
	
	indexVar = dotProdRange[0]
	startVal = int(dotProdRange[1])
	startVal = startVal - 1
	startVal = str(startVal)
	endVal = dotProdRange[2]

	endValInCode = endVal

	if (endVal == numSignaturesEndVal):
		endValInCode = numSignaturesEndValInCode
	elif (endVal == numSignersEndVal):
		endValInCode = numSignersEndValInCode
		#batchOutputString = writeNumSignersLoop(batchOutputString, numTabs, numTabsBeforeVerify, verifyFuncArgs, declaredLists, pythonCodeLines, listOfIndentedBlocks, indexVar, parentIndexVar, startVal, endVal, dotProdList[dotProdRange][0], computeLineInfo, assignMap)
		#return batchOutputString

	for tab in range(0, numTabs):
		batchOutputString += "\t"

	#listNamesToReplacementStrings = {}
	
	if (writeDotProdLines == True) or (indexVar != numSignaturesIndex):	
		batchOutputString += "for " + indexVar + " in range(" + startVal + ", " + endValInCode + "):\n"
	else:
		batchOutputString += "for " + indexVar + " in range(startIndex, endIndex):\n"
		#batchOutputString += "for sigIndex in range(startIndex, endIndex):\n"
	
	
	
	if (endValInCode == numSignaturesEndValInCode):
		batchOutputString = setUpVerifyFuncArgs(batchOutputString, numTabs + 1, indexVar)
		varsForDotProds = []

		if (writeDotProdLines == True):
			for topLevelKey in topLevelDotProd:
				topLevelRange = topLevelKey
				break
		
			getVarsForDotProds(topLevelDotProd[topLevelRange], computeLineInfo, varsForDotProds)
		else:
			topLevelDotProdList = []
			topLevelDotProdList.append(topLevelDotProd)
			DC_outerDotProdNoSigs = getDC_outerDotProds(topLevelDotProdList, False, computeLineInfo)
			for topLevelKey in DC_outerDotProdNoSigs[0]:
				topLevelRange = topLevelKey
				break
			getVarsForDotProds(DC_outerDotProdNoSigs[0][topLevelRange], computeLineInfo, varsForDotProds)

			
			
		cleanVarsForDotProds(varsForDotProds)
		linesForDotProds = getLinesForDotProds(varsForDotProds, assignMap, pythonCodeLines, listOfIndentedBlocks)
		#listNamesToReplacementStrings = {}
		#namesToReplacementsCopy = copy.deepcopy(listNamesToReplacementStrings)
		
		#if (writeDotProdLines == True):
		batchOutputString = writeDotProdLinesToFile(batchOutputString, computeLineInfo, pythonCodeLines, linesForDotProds, numTabs + 1, numTabsBeforeVerify, verifyFuncArgs, declaredLists, indexVar, None, listNamesToReplacementStrings)

	for child in dotProdList[dotProdRange]:
		if type(child).__name__ == pythonDictRep:
			namesToReplacementsCopy = copy.deepcopy(listNamesToReplacementStrings)
			batchOutputString = addDotProdLoopRecursive(batchOutputString, writeDotProdLines, computeLineInfo, child, assignMap, pythonCodeLines, listOfIndentedBlocks, numTabs + 1, numTabsBeforeVerify, verifyFuncArgs, declaredLists, indexVar, namesToReplacementsCopy, outerDotProds, topLevelDotProd, indexVarsOfDotProdsInOrder)

	precomputeVarsDefinedSoFar = []

	indexVarsOfDotProdsInOrder.append(indexVar)

	for child in dotProdList[dotProdRange]:
		if ( (type(child).__name__ != pythonDictRep) and ( (child.startswith(dotProdPrefix) ) or (child.startswith(sumPrefix))    ) and (len(child) == 4)):
			#indexVarsOfDotProdsInOrder.append(indexVar)
			batchOutputString = writeDotProdCalculations(batchOutputString, writeDotProdLines, computeLineInfo, listNamesToReplacementStrings, indexVar, numTabs + 1, child, outerDotProds, verifyFuncArgs, precomputeVarsDefinedSoFar, indexVarsOfDotProdsInOrder)



			#if (parentIndexVar != None):
				#parentAndChildIndices = indexVar + parentIndexVar
				#for declaredList in declaredLists:
					#if (parentAndChildIndices == getSuffixesFromDeclaredLists(declaredList) ):
						#for numTab in range(0, numTabs):
							#batchOutputString += "\t"
						#listNameFromDL = getListNameFromDeclaredLists(declaredList)
						#batchOutputString += listNameFromDL + parentAndChildIndices + "[" + parentIndexVar + "] = copy.deepcopy(" + listNameFromDL + indexVar + ")\n"
				#batchOutputString += "\n"

	return batchOutputString

def addDotProdLoops(batchOutputString, writeDotProdLines, computeLineInfo, dotProdLoopOrder, assignMap, pythonCodeLines, listOfIndentedBlocks, numTabsBeforeVerify, verifyFuncArgs, declaredLists, outerDotProds):
	#batchOutputString += "\ttest\n"
	
	#print(dotProdLoopOrder)
	
	for outerDotProd in dotProdLoopOrder:
		#print(outerDotProd)
		listNamesToReplacementStrings = {}
		indexVarsOfDotProdsInOrder = []
		batchOutputString = addDotProdLoopRecursive(batchOutputString, writeDotProdLines, computeLineInfo, outerDotProd, assignMap, pythonCodeLines, listOfIndentedBlocks, 1, numTabsBeforeVerify, verifyFuncArgs, declaredLists, None, listNamesToReplacementStrings, outerDotProds, outerDotProd, indexVarsOfDotProdsInOrder)
		batchOutputString += "\n"
	
	return batchOutputString

def getDotProdListIndex(dotProdList, range):
	childCounter = 0
	
	for child in dotProdList:
		if type(child).__name__ == pythonDictRep:
			for key in child:
				if (key == range):
					return childCounter
					
		childCounter += 1
		
	return -1
					

def dotProdLoopRecursive(computeLineInfo, outerDotProd, dotProdList):	
	range = computeLineInfo[outerDotProd][computeLineRange]
	
	#if (range not in dotProdList):

	#rangeKeyExists = False

	dotProdListIndex = getDotProdListIndex(dotProdList, range)
		
	if (dotProdListIndex == -1):
		newDictEntry = {}
		dotProdList.append(newDictEntry)
		newDictEntry[range] = []
		newDictEntry[range].append(outerDotProd)
	else:
		dotProdList[dotProdListIndex][range].append(outerDotProd)
	
	for varName in computeLineInfo[outerDotProd][computeLineVarsNoSubscripts]:
		if (  (  (varName.startswith(dotProdPrefix)) or (varName.startswith(sumPrefix))    ) and (len(varName) ==  4) ):
			#dotProdDict[outerDotProd][varName] = {}
			#dotProdLoopRecursive(computeLineInfo, varName, dotProdDict[outerDotProd])
			
			dotProdListIndex = getDotProdListIndex(dotProdList, range)
			
			dotProdLoopRecursive(computeLineInfo, varName, dotProdList[dotProdListIndex][range])

def getDotProdLoopOrder(computeLineInfo, outerDotProds, dotProdLoopOrder):
	#dotProdLoopOrder = {}

	for outerDotProd in outerDotProds:
		dotProdLoopRecursive(computeLineInfo, outerDotProd, dotProdLoopOrder)
			
	return dotProdLoopOrder

def printList(dict):
	for key in dict:
		if (type(key).__name__ == 'dict'):
			print(key)
			for child in key:
				print(key)
				print(key[child])
			print("\n")
		else:
			print(key)
		#print(key)
		#print(dict[key])
		print("\n")

def addNumSigsSignersDefs(batchOutputString, pythonCodeLines):
	foundNumSignatures = False
	foundNumSigners = False
	
	for line in pythonCodeLines:
		if (line.lstrip().startswith(numSignaturesEndValInCode + " = ") == True):
			batchOutputString += "\t" + line.lstrip().rstrip() + "\n"
			foundNumSignatures = True
		elif (line.lstrip().startswith(numSignersEndValInCode + " = ") == True):
			batchOutputString += "\t" + line.lstrip().rstrip() + "\n"
			foundNumSigners = True
			
		if ( (foundNumSignatures == True) and (foundNumSigners == True) ):
			break

	return batchOutputString

def addEqualityTestFromFinalBatchEq(verifySigsOutput, finalBatchEq, outerDotProds, varNameFuncArgs, precomputeOuterDotProds):

	outerDotProdString = ""
	
	for outerDotProd in outerDotProds:
		if outerDotProd in precomputeOuterDotProds:
			outerDotProdString += outerDotProd + ", "
		
	for varNameFuncArg in varNameFuncArgs:
		outerDotProdString += varNameFuncArg + ", "

	finalBatchEq = finalBatchEq.lstrip().rstrip()

	verifySigsOutput += "\tif " + finalBatchEq + ":\n"
	verifySigsOutput += "\t\treturn\n"
	verifySigsOutput += "\telse:\n"
	verifySigsOutput += "\t\tmidWay = int( (endIndex - startIndex) / 2)\n"
	verifySigsOutput += "\t\tif (midWay == 0):\n"
	verifySigsOutput += "\t\t\tprint(\"sig \" + str(startIndex) + \" failed\\n\")\n"
	verifySigsOutput += "\t\t\treturn\n"
	verifySigsOutput += "\t\tmidIndex = startIndex + midWay\n"
	verifySigsOutput += "\t\tverifySigsRecursive(group, deltaz, verifyFuncArgs, argSigIndexMap, verifyArgsDict, " + outerDotProdString + "startIndex, midIndex)\n"
	verifySigsOutput += "\t\tverifySigsRecursive(group, deltaz, verifyFuncArgs, argSigIndexMap, verifyArgsDict, " + outerDotProdString + "midIndex, endIndex)\n"

	#print(finalBatchEq)
	return verifySigsOutput

def convertNewSliceSymbolToUnderscore(varName):
	if (varName.count(newSliceSymbol) != 1):
		return varName
	
	varNameSplit = varName.split(newSliceSymbol)
	return varNameSplit[0] + sumOrDotSymbol + varNameSplit[1]

def getSimplifiedFinalBatchEq(batchVerifierOutput, pythonCodeNode, verifyFuncArgs, varNameFuncArgs):
	for line in batchVerifierOutput:
		if (line.startswith(finalEqLineString) == True):
			break
		
	line = line.replace(finalEqLineString, "", 1)
	line = ensureSpacesBtwnTokens(line)
	line = line.replace(" e ", " pair ")
	line = line.replace(" ^ ", " ** ")
	
	tokenSplit = line.split()
	for token in tokenSplit:
		if ( (   (token.startswith(dotProdPrefix)) or (token.startswith(sumPrefix))   ) and (len(token) == 4) ):
			replacementString = token + "_runningProduct"
			tokenWithSpaces = ' ' + token + ' '
			replacementString = ' ' + replacementString + ' '
			line = line.replace(tokenWithSpaces, replacementString, 1)
		elif ( (token.count(newSliceSymbol) > 0) and (convertNewSliceSymbolToUnderscore(token) in varNameFuncArgs) ):
			replacementString = ' ' + convertNewSliceSymbolToUnderscore(token) + ' '
			tokenWithSpaces = ' ' + token + ' '
			line = line.replace(tokenWithSpaces, replacementString, 1)
		elif (token.count(newSliceSymbol) > 0):
			replacementString = ""
			dictName = token.split(newSliceSymbol)[0]
			if dictName in verifyFuncArgs:
				replacementString += " verifyArgsDict[argSigIndexMap[\'" + dictName + "\']][\'" + dictName + "\'][bodyKey]"
			sliceIndex = int(token.split(newSliceSymbol)[1])
			getKeysVar = GetKeysOfDictAssign(dictName)
			getKeysVar.visit(pythonCodeNode)
			keysDict = getKeysVar.getKeys()
			if (keysDict[sliceIndex][typeRep] == stringRepInAST):
				if (replacementString == ""):
					replacementString += dictName + "[\'" + keysDict[sliceIndex][valueRep] + "\']"
				else:
					replacementString += "[\'" + keysDict[sliceIndex][valueRep] + "\']"
			elif (keysDict[sliceIndex][typeRep] == numRepInAST):
				if (replacementString == ""):
					replacementString += dictName + "[" + str(keysDict[sliceIndex][valueRep]) + "]"
				else:
					replacementString += "[" + str(keysDict[sliceIndex][valueRep]) + "]"
			else:
				return line
			tokenWithSpaces = ' ' + token + ' '
			replacementString = ' ' + replacementString + ' '
			line = line.replace(tokenWithSpaces, replacementString, 1)
		elif token in verifyFuncArgs:
			replacementString = "verifyArgsDict[argSigIndexMap[\'" + token + "\']][\'" + token + "\'][bodyKey]"
			tokenWithSpaces = ' ' + token + ' '
			replacementString = ' ' + replacementString + ' '
			line = line.replace(tokenWithSpaces, replacementString, 1)
		elif (token.find(sumOrDotSymbol) != -1):
			replacementString = (token.split(sumOrDotSymbol))[0]
			tokenWithSpaces = ' ' + token + ' '
			replacementString = ' ' + replacementString + ' '
			line = line.replace(tokenWithSpaces, replacementString, 1)
	
	#print(verifyFuncArgs)
	
	return line

def resetArgSigIndexDictTo1s(batchOutputString):
	batchOutputString += "\tfor arg in verifyFuncArgs:\n"
	batchOutputString += "\t\targSigIndexMap[arg] = 0\n\n"
	
	return batchOutputString

def addLinesForNonDotProdVars(batchOutputString, assignMap, pythonCodeLines, listOfIndentedBlocks, computeLineInfo, numTabsOnVerifyFuncLine, verifyFuncArgs):
	
	cleanVarNames = []
	
	for varName in finalEqLineVars:
		lenOfVarName = len(varName)
		possibleInt = varName[lenOfVarName - 1]
		if (possibleInt.isdigit() == True):
			possibleCleanName = varName[0:(lenOfVarName - 2)]
		elif (varName.find(sumOrDotSymbol) != -1):
			varNameSplit = varName.split(sumOrDotSymbol)
			possibleCleanName = varNameSplit[0]
			
		else:
			possibleCleanName = varName
		if (possibleCleanName not in cleanVarNames):
			cleanVarNames.append(possibleCleanName)
			
	lineNos = getLinesForDotProds(cleanVarNames, assignMap, pythonCodeLines, listOfIndentedBlocks)
	#print(lineNos)

	if (len(lineNos) == 0):
		return batchOutputString

	#batchOutputString = resetArgSigIndexDictTo1s(batchOutputString)

	listNamesToReplacementStrings = {}

	batchOutputString = writeDotProdLinesToFile(batchOutputString, computeLineInfo, pythonCodeLines, lineNos, 0, 0, verifyFuncArgs, [], None, None, listNamesToReplacementStrings)
	
	return batchOutputString

def addCallToVerifySigs(batchOutputString, outerDotProds, varNameFuncArgs, verifyFuncArgs, pythonCodeNode):

	for varName in finalEqLineVars:
		if (varName.find(newSliceSymbol) == -1):
			varNameFuncArgs.append(varName)
		else:
			varNameSplit = varName.split(newSliceSymbol)
			varNameFuncArgs.append(varNameSplit[0] + sumOrDotSymbol + varNameSplit[1])

	#print(varNameFuncArgs)
	
	batchOutputString += "\tverifySigsRecursive(group, deltaz, verifyFuncArgs, argSigIndexMap, verifyArgsDict, "
	for outerDotProd in outerDotProds:
		batchOutputString += outerDotProd + ", "

	for varName in varNameFuncArgs:
		if (varName.find(sumOrDotSymbol) == -1):
			batchOutputString += varName + ", "
			continue
		
		replacementString = ""
		dictName = varName.split(sumOrDotSymbol)[0]
		if dictName in verifyFuncArgs:
			replacementString += " verifyArgsDict[argSigIndexMap[\'" + dictName + "\']][\'" + dictName + "\'][bodyKey]"
		sliceIndex = int(varName.split(sumOrDotSymbol)[1])
		getKeysVar = GetKeysOfDictAssign(dictName)
		getKeysVar.visit(pythonCodeNode)
		keysDict = getKeysVar.getKeys()	
		if (keysDict[sliceIndex][typeRep] == stringRepInAST):
			if (replacementString == ""):
				replacementString += dictName + "[\'" + keysDict[sliceIndex][valueRep] + "\']"
			else:
				replacementString += "[\'" + keysDict[sliceIndex][valueRep] + "\']"
		elif (keysDict[sliceIndex][typeRep] == numRepInAST):
			if (replacementString == ""):
				replacementString += dictName + "[" + str(keysDict[sliceIndex][valueRep]) + "]"
			else:
				replacementString += "[" + str(keysDict[sliceIndex][valueRep]) + "]"
		batchOutputString += replacementString + ", "
				

	batchOutputString += "0, N)\n"
	
	return batchOutputString

def getVariableTypes(verifyNode):
	#variableTypes = {}
	varsToRemove = []

	#print(cleanBatchEqVars)
	
	for varName in cleanBatchEqVars:
		if (varName == deltaString):
			varsToRemove.append(varName)
		if (  (  (varName.startswith(dotProdPrefix)) or (varName.startswith(sumPrefix))   )    and (len(varName) == 4)   ):
			varsToRemove.append(varName)
			
	for varToRemove in varsToRemove:
		del cleanBatchEqVars[varToRemove]

	#print(cleanBatchEqVars)

	variableNames = list(copy.deepcopy(cleanBatchEqVars).keys())

	basicTypesVar = GetBasicVariableTypes(variableNames)
	basicTypesVar.visit(verifyNode)

	variableTypes = basicTypesVar.getVariableTypesDict()
	
	return variableTypes
'''

def processListLine(line):
	global listVars

	if ( (line == None) or (type(line).__name__ != con.strTypePython) or (len(line) == 0) or (line.startswith(con.listString) == False) ):
		sys.exit("AutoBatch_CodeGen->processListLine:  problem with line parameter passed to the function.")

	line = line.replace(con.listString, '', 1)
	line = line.lstrip().rstrip()
	lineSplit = line.split(con.listInString)
	varName = lineSplit[0].lstrip().rstrip()
	if (varName in listVars):
		sys.exit("AutoBatch_CodeGen->processListLine:  variable currently being processed (" + varName + ") is already included in the listVars data structure (duplicate).")

	loopTypes = lineSplit[1].lstrip().rstrip()
	#if (loopType not in con.loopTypes):
		#sys.exit("AutoBatch_CodeGen->processListLine:  one of the loop types extracted is not one of the supported loop types.")

	listVars[varName] = loopTypes

def processPrecomputeLine(line):
	global precomputeVars

	if ( (line == None) or (type(line).__name__ != con.strTypePython) or (line.startswith(con.precomputeString) == False) ):
		sys.exit("AutoBatch_CodeGen->processPrecomputeLine:  problem with line parameter passed in.")

	lenPrecomputeString = len(con.precomputeString)
	line = line[lenPrecomputeString:len(line)]
	line = line.lstrip().rstrip()
	if (line.startswith(con.deltaPrecomputeVarString) == True):
		return

	lineSplit = line.split(con.batchVerifierOutputAssignment)
	varName = lineSplit[0].lstrip().rstrip()
	expression = lineSplit[1].lstrip().rstrip()

	for precomputeVariable in precomputeVars:
		currentVariableName = precomputeVariable.getVarName().getStringVarName()
		if (varName == currentVariableName):
			sys.exit("AutoBatch_CodeGen->processPrecomputeLine:  found duplicate variable name for a precompute variable (" + varName + ").")

	varNameStringName = StringName()
	varNameStringName.setName(varName)

	nextPrecomputeVarObj = PrecomputeVariable()
	nextPrecomputeVarObj.setVarName(varNameStringName)
	nextPrecomputeVarObj.setExpression(expression)
	precomputeVars.append(copy.deepcopy(nextPrecomputeVarObj))

def processLoopLine(line):
	global loopVarGroupTypes

	if ( (line == None) or (type(line).__name__ != con.strTypePython) ):
		sys.exit("AutoBatch_CodeGen->processLoopLine:  problem with line parameter passed in.")

	lineSplit = line.split(con.batchVerifierOutputAssignment)
	varName = lineSplit[0].lstrip().rstrip()
	groupType = lineSplit[1].lstrip().rstrip()

	isVarNameALoopName = isStringALoopName(varName)
	if (isVarNameALoopName == False):
		sys.exit("AutoBatch_CodeGen->processLoopLine:  loop line passed in does not contain the name of a valid loop name.")

	if (varName in loopVarGroupTypes):
		sys.exit("AutoBatch_CodeGen->processLoopLine:  found duplicate in loop variable names.")

	if (groupType not in con.groupTypes):
		sys.exit("AutoBatch_CodeGen->processLoopLine:  group type ovar loop variable " + varName + " is not one of the supported types.")

	loopVarGroupTypes[varName] = groupType

'''
def getStandAloneVars(batchEqNotSumOrDotVars):
	standAloneVars = []

	for varName in batchEqNotSumOrDotVars:
		if (varName.find(newSliceSymbol) != -1):
			continue
		standAloneVars.append(varName)
	
	return standAloneVars

def doWeAddIt(dotProdList, computeLineInfo):

	for dotProd in dotProdList:
		if dotProd not in computeLineInfo:
			return True

		for var in computeLineInfo[dotProd][computeLineVars]:
			if (var.find(sumOrDotSymbol) == -1):
				continue
			varSplit = var.split(sumOrDotSymbol)
			if (varSplit[1].find(numSignersIndex) != -1):
				return False
	
	return True

def getSplitOrderRecursive(dotProdLoopOrder, precomputeDotProdOrder, computeLineInfo):
	if (type(dotProdLoopOrder).__name__ != pythonDictRep):
		return

	for key in dotProdLoopOrder:
		keyName = key
		break
		
	if (keyName == (numSignaturesIndex + "1" + numSignaturesEndVal) ):
		doWeAddThis = doWeAddIt(dotProdLoopOrder[keyName], computeLineInfo)
		if (doWeAddThis == True):
			precomputeDotProdOrder.append(dotProdLoopOrder)
		return
	else:
		for child in dotProdLoopOrder[keyName]:
			getSplitOrderRecursive(child, precomputeDotProdOrder, computeLineInfo)
		return

def getSplitDotProdLoopOrder(dotProdLoopOrder, computeLineInfo):
	
	precomputeDotProdOrder = []

	for dotProd in dotProdLoopOrder:
		getSplitOrderRecursive(dotProd, precomputeDotProdOrder, computeLineInfo)

	#print(dotProdLoopOrder)
	
	#print(precomputeDotProdOrder)

	#precompute

	return precomputeDotProdOrder
		
	#print(dotProdLoopOrder)
	#return precomputeDotProdOrder#, DC_dotProdOrder

def getPrecomputeOuterDotProds(precomputeDotProdLoopOrder):
	#precomputeOuterDotProds = []
	
	for listChild in precomputeDotProdLoopOrder:
		for key in listChild:
			keyName = key
			break
		
		for dictChild in listChild[keyName]:
			if (  (type(dictChild).__name__ != pythonDictRep)  and  ( (dictChild.startswith(dotProdPrefix)) or (dictChild.startswith(sumPrefix)) ) and (len(dictChild) == 4)  ):
				precomputeOuterDotProds.append(dictChild)
				
	#return precomputeOuterDotProds










def getDC_outerDotProdsRecursive_JUSTOUTER(outerDotProdOrder, DC_outerDotProds, addSignatureLoopDotProds):

	#if (type(outerDotProdOrder).__name__ != pythonDictRep):
		#DC_outerDotProds.append(outerDotProdOrder)
		#return

	for key in outerDotProdOrder:
		keyName = key
		break

	foundLastOne = False

	if (keyName == (numSignaturesIndex + "1" + numSignaturesEndVal) ):
		foundLastOne = True

	#DC_outerDotProds.append({keyName:[]})

	for dictChild in outerDotProdOrder[keyName]:
		if ( (type(dictChild).__name__ != pythonDictRep)  and       ( (dictChild.startswith(dotProdPrefix)) or (dictChild.startswith(sumPrefix)) ) and (len(dictChild) == 4)  ):
			if ( (foundLastOne == False) or (addSignatureLoopDotProds == True) ):
				DC_outerDotProds[keyName].append(dictChild)
			
	for dictChild in outerDotProdOrder[keyName]:
		if ( (type(dictChild).__name__ == pythonDictRep) and (foundLastOne == False) ):
			for childKey in dictChild:
				childKeyName = childKey
				break

			DC_outerDotProds[keyName].append({childKeyName:[]})
			lenOfCurrentDC_OuterProdList = len(DC_outerDotProds[keyName])
			getDC_outerDotProdsRecursive_JUSTOUTER(dictChild, DC_outerDotProds[keyName][lenOfCurrentDC_OuterProdList - 1], addSignatureLoopDotProds )
			


def getDC_outerDotProds_JUSTOUTER(outerDotProdOrder, addSignatureLoopDotProds):
	DC_outerDotProds = []
	
	for listChild in outerDotProdOrder:
		for key in listChild:
			keyName = key
			break
		
		if (keyName == (numSignaturesIndex + "1" + numSignaturesEndVal) ):
			continue

		DC_outerDotProds.append({keyName:[]})
		
		getDC_outerDotProdsRecursive_JUSTOUTER(listChild, DC_outerDotProds[len(DC_outerDotProds) - 1], addSignatureLoopDotProds)
	
	return DC_outerDotProds















def getDoWeAddThisOne(dotProd, computeLineInfo):

	range = computeLineInfo[dotProd][computeLineRange]
	
	if range != (numSignaturesIndex + "1" + numSignaturesEndVal):
		return True

	for var in computeLineInfo[dotProd][computeLineVars]:
		if (var.find(sumOrDotSymbol) == -1):
			continue
		varSplit = var.split(sumOrDotSymbol)
		if (varSplit[1].find(numSignersIndex) != -1):
			return True
	
	return False



def getDC_outerDotProdsRecursive(outerDotProdOrder, DC_outerDotProds, addSignatureLoopDotProds, computeLineInfo):

	#if (type(outerDotProdOrder).__name__ != pythonDictRep):
		#DC_outerDotProds.append(outerDotProdOrder)
		#return

	for key in outerDotProdOrder:
		keyName = key
		break

	#foundLastOne = False

	#if (keyName == (numSignaturesIndex + "1" + numSignaturesEndVal) ):
		#foundLastOne = True

	#DC_outerDotProds.append({keyName:[]})

	for dictChild in outerDotProdOrder[keyName]:
		if ( (type(dictChild).__name__ != pythonDictRep)  and       ( (dictChild.startswith(dotProdPrefix)) or (dictChild.startswith(sumPrefix)) ) and (len(dictChild) == 4)  ):
			#if ((addSignatureLoopDotProds == True) ):
			doWeAddThisOne = getDoWeAddThisOne(dictChild, computeLineInfo)
			if (doWeAddThisOne == True):
				DC_outerDotProds[keyName].append(dictChild)
			
	for dictChild in outerDotProdOrder[keyName]:
		if ( (type(dictChild).__name__ == pythonDictRep)):
			for childKey in dictChild:
				childKeyName = childKey
				break

			DC_outerDotProds[keyName].append({childKeyName:[]})
			lenOfCurrentDC_OuterProdList = len(DC_outerDotProds[keyName])
			getDC_outerDotProdsRecursive(dictChild, DC_outerDotProds[keyName][lenOfCurrentDC_OuterProdList - 1], addSignatureLoopDotProds, computeLineInfo )
			


def getDC_outerDotProds(outerDotProdOrder, addSignatureLoopDotProds, computeLineInfo):
	DC_outerDotProds = []
	
	for listChild in outerDotProdOrder:
		for key in listChild:
			keyName = key
			break
		
		#if (keyName == (numSignaturesIndex + "1" + numSignaturesEndVal) ):
			#continue

		DC_outerDotProds.append({keyName:[]})
		
		getDC_outerDotProdsRecursive(listChild, DC_outerDotProds[len(DC_outerDotProds) - 1], addSignatureLoopDotProds, computeLineInfo)
	
	return DC_outerDotProds

def isTopLayerLoopOverNumSignatures(dotProdLoopOrder):

	for listChild in dotProdLoopOrder:
		for key in listChild:
			keyName = key
			break

		if (keyName != (numSignaturesIndex + "1" + numSignaturesEndVal) ):
			return False
		
	return True
'''

def addImportLines():
	global batchVerFile, individualVerFile, verifySigsFile

	importLines = getImportLines(pythonCodeNode, copy.deepcopy(pythonCodeLines))
	if (importLines == None):
		return

	if ( (type(importLines).__name__ != con.listTypePython) or (len(importLines) == 0) ):
		sys.exit("AutoBatch_CodeGen->addImportLines:  problem with value returned from getImportLines.")

	for index in range(0, len(importLines)):
		batchVerFile.write(importLines[index].lstrip().rstrip() + "\n")
		individualVerFile.write(importLines[index].lstrip().rstrip() + "\n")
		verifySigsFile.write(importLines[index].lstrip().rstrip() + "\n")

	batchVerFile.write("import sys\n")
	individualVerFile.write("import sys\n")
	verifySigsFile.write("import sys\n\n")

def getGlobalVarsHeaderString():
	if (globalVars == None):
		return None

	globalsString = ""

	if ( (type(globalVars).__name__ != con.listTypePython) or (len(globalVars) == 0) ):
		sys.exit("AutoBatch_CodeGen->getGlobalVarsHeaderString:  problem with globalVars global variable.")

	for var in globalVars:
		if ( (var == None) or (type(var).__name__ != con.stringName) ):
			sys.exit("AutoBatch_CodeGen->getGlobalVarsHeaderString:  problem with one of the StringName objects in the globalVars global variable.")

		varAsString = var.getStringVarName()
		if ( (varAsString == None) or (type(varAsString).__name__ != con.strTypePython) or (len(varAsString) == 0) ):
			sys.exit("AutoBatch_CodeGen->getGlobalVarsHeaderString:  problem with string representation of one of the StringName objects in the globalVars global variable.")

		if (varAsString == con.group):
			continue

		globalsString += varAsString + ", "

	lenString = len(globalsString)

	return globalsString[0:(lenString - 2)]

def addCommonHeaderLines():
	global batchVerFile, individualVerFile, verifySigsFile

	batchOutputString = ""
	indOutputString = ""
	verifyOutputString = ""

	batchOutputString += "from toolbox.pairinggroup import *\n"
	batchOutputString += "from verifySigs import verifySigsRecursive\n\n"
	batchOutputString += con.group + " = None\n"

	indOutputString += "\n" + con.group + " = None\n"

	verifyOutputString += con.group + " = None\n"

	globalVarsString = getGlobalVarsHeaderString()
	if (globalVarsString != None):
		if ( (type(globalVarsString).__name__ != con.strTypePython) or (len(globalVarsString) == 0) ):
			sys.exit("AutoBatch_CodeGen->addCommonHeaderLines:  problem with value returned from getGlobalVarsHeaderString.")
		batchOutputString += globalVarsString + " = None\n"
		indOutputString += globalVarsString + " = None\n"
		verifyOutputString += globalVarsString + " = None\n"

	batchOutputString += "bodyKey = \'Body\'\n\n"
	batchOutputString += "def prng_bits(bits=80):\n"
	batchOutputString += "\treturn " + con.group + ".init(ZR, randomBits(bits))\n\n"

	indOutputString += "bodyKey = \'Body\'\n\n"

	verifyOutputString += "\n"

	batchVerFile.write(batchOutputString)
	individualVerFile.write(indOutputString)
	verifySigsFile.write(verifyOutputString)

def addTemplateLines():
	global batchVerFile, individualVerFile

	numSigners = getStringNameIntegerValue(varAssignments, con.numSigners, con.mainFuncName)

	batchOutputString = ""
	indOutputString = ""

	batchOutputString += "def run_Batch(verifyArgsDict, " + con.group + "ObjParam, verifyFuncArgs):\n"
	batchOutputString += "\tglobal " + con.group + "\n"

	indOutputString += "def run_Ind(verifyArgsDict, " + con.group + "ObjParam, verifyFuncArgs):\n"
	indOutputString += "\tglobal " + con.group + "\n"

	globalsString = getGlobalVarsHeaderString()
	if (globalsString != None):
		if ( (type(globalsString).__name__ != con.strTypePython) or (len(globalsString) == 0) ):
			sys.exit("AutoBatch_CodeGen->addTemplateLines:  problem with return value from getGlobalVarsHeaderString.")
		batchOutputString += "\tglobal " + globalsString + "\n"
		indOutputString += "\tglobal " + globalsString + "\n"

	batchOutputString += "\t" + con.group + " = " + con.group + "ObjParam\n\n"
	batchOutputString += "\t" + con.numSignatures + " = len(verifyArgsDict)\n"

	if (numSigners != None):
		batchOutputString += "\t" + con.numSigners + " = " + str(numSigners) + "\n"

	batchOutputString += "\t" + con.deltaDictName + " = {}\n"
	batchOutputString += "\tfor sigIndex in range(0, " + con.numSignatures + "):\n"
	batchOutputString += "\t\t" + con.deltaDictName + "[sigIndex] = prng_bits(80)\n\n"
	batchOutputString += "\tincorrectIndices = []\n"

	indOutputString += "\t" + con.group + " = " + con.group + "ObjParam\n\n"
	indOutputString += "\t" + con.numSignatures + " = len(verifyArgsDict)\n"

	if (numSigners != None):
		indOutputString += "\t" + con.numSigners + " = " + str(numSigners) + "\n"

	indOutputString += "\tincorrectIndices = []\n"

	batchVerFile.write(batchOutputString)
	individualVerFile.write(indOutputString)

def addPrerequisites():
	global batchVerFile, individualVerFile

	prereqLineNos = getLineNosOfValueType(varAssignments, con.lambdaValue)
	if (prereqLineNos == None):
		return

	if ( (type(prereqLineNos).__name__ != con.listTypePython) or (len(prereqLineNos) == 0) ):
		sys.exit("AutoBatch_CodeGen->addPrerequisites:  problem with value returned from getLineNosOfValueType.")

	prereqLines = getLinesFromSourceCode(copy.deepcopy(pythonCodeLines), prereqLineNos)
	if ( (prereqLines == None) or (type(prereqLines).__name__ != con.listTypePython) or (len(prereqLines) == 0) ):
		sys.exit("AutoBatch_CodeGen->addPrerequisites:  problem with value returned from getLinesFromSourceCode.")

	outputString = ""

	for line in prereqLines:
		if ( (line == None) or (type(line).__name__ != con.strTypePython) or (len(line) == 0) ):
			sys.exit("AutoBatch_CodeGen->addPrerequisites:  problem with one of the lines returned from getLinesFromSourceCode.")

		outputString += "\t" + line.lstrip().rstrip()
		outputString += "\n"

	batchVerFile.write(outputString)
	individualVerFile.write(outputString)

	global verifyPrereqs
	verifyPrereqs = outputString

def getInitArgString():
	if (con.initFuncName not in functionArgNames):
		sys.exit("AutoBatch_CodeGen->getInitArgString:  init function is not included in the function arguments names structure.")

	if (functionArgNames[con.initFuncName] == None):
		return ""

	initArgListAsStrings = getFunctionArgsAsStrings(functionArgNames, con.initFuncName)
	if ( (initArgListAsStrings == None) or (type(initArgListAsStrings).__name__ != con.listTypePython) or (len(initArgListAsStrings) == 0) ):
		sys.exit("AutoBatch_CodeGen->getInitArgString:  problem with value returned from getFunctionArgsAsStrings.")

	if (len(initArgListAsStrings) > 1):
		sys.exit("AutoBatch_CodeGen->getInitArgString:  number of arguments passed to __init__ function is greater than one; this is not currently supported.")

	onlyArg = initArgListAsStrings[0]

	if (onlyArg.startswith(con.group) == False):
		sys.exit("AutoBatch_CodeGen->getInitArgString:  the argument passed to the __init__ function does not start with \"" + con.group + "\"; this is not currently supported.")

	return con.group

def addCallToInit():
	if (con.initFuncName not in functionNames):
		sys.exit("AutoBatch_CodeGen->addCallToInit:  init function is not included in the function names dictionary.")

	global batchVerFile, individualVerFile

	batchOutputString = ""
	indOutputString = ""

	initArgString = getInitArgString()

	batchOutputString += "\t__init__(" + initArgString + ")\n\n"
	indOutputString += "\t__init__(" + initArgString + ")\n"

	batchVerFile.write(batchOutputString)
	individualVerFile.write(indOutputString)

def addSigLoop():
	global batchVerFile, individualVerFile

	outputString = ""
	outputString += "\n\tfor sigIndex in range(0, " + con.numSignatures + "):\n"

	batchVerFile.write(outputString)
	individualVerFile.write(outputString)

def addGroupMembershipChecks():
	global batchVerFile, individualVerFile

	outputString = ""
	outputString += "\t\tfor arg in verifyFuncArgs:\n"
	outputString += "\t\t\tif (group.ismember(verifyArgsDict[sigIndex][arg][bodyKey]) == False):\n"
	outputString += "\t\t\t\tsys.exit(\"ALERT:  Group membership check failed!!!!\\n\")\n\n"

	batchVerFile.write(outputString)
	individualVerFile.write(outputString)

def writeLinesToOutputString(lines, indentationListParam, baseNumTabs, numExtraTabs):
	if ( (lines == None) or (type(lines).__name__ != con.listTypePython) or (len(lines) == 0) ):
		sys.exit("AutoBatch_CodeGen->writeLinesToOutputString:  problem with lines parameter passed in.")

	if ( (indentationListParam == None) or (type(indentationListParam).__name__ != con.listTypePython) or (len(indentationListParam) != len(lines) ) ):
		sys.exit("AutoBatch_CodeGen->writeLinesToOutputString:  problem with indentation list parameter passed in.")

	if ( (baseNumTabs == None) or (type(baseNumTabs).__name__ != con.intTypePython) or (baseNumTabs < 0) ):
		sys.exit("AutoBatch_CodeGen->writeLinesToOutputString:  problem with base number of tabs parameter passed in.")

	if ( (numExtraTabs == None) or (type(numExtraTabs).__name__ != con.intTypePython) or (numExtraTabs < 0) ):
		sys.exit("AutoBatch_CodeGen->writeLinesToOutputString:  problem with extra number of tabs passed in.")

	outputString = ""
	lineNumber = -1

	for line in lines:
		lineNumber += 1
		if (isLineOnlyWhiteSpace(line) == True):
			continue
		line = ensureSpacesBtwnTokens_CodeGen(line)
		for arg in verifyFuncArgs:
			argWithSpaces = ' ' + arg + ' '
			numArgMatches = line.count(argWithSpaces)
			for countIndex in range(0, numArgMatches):
				indexOfCharAfterArg = line.index(argWithSpaces) + len(argWithSpaces)
				if (indexOfCharAfterArg < len(line)):
					charAfterArg = line[indexOfCharAfterArg]
				else:
					charAfterArg = ''
				replacementString = " verifyArgsDict[sigIndex][\'" + arg + "\'][bodyKey]"
				if (charAfterArg == con.dictBeginChar):
					line = line.replace(argWithSpaces + '[', replacementString + '[', 1)
				else:
					line = line.replace(argWithSpaces, replacementString + ' ', 1)
		line = line.lstrip().rstrip()
		line = removeSpaceBeforeChar(line, con.lParan)
		line = removeSpaceAfterChar(line, '-')
		line = line.replace(con.selfFuncCallString, con.space)
		numTabs = determineNumTabsFromSpaces(indentationListParam[lineNumber], numSpacesPerTab) - baseNumTabs
		numTabs += numExtraTabs
		outputString += getStringOfTabs(numTabs)
		outputString += line + "\n"

	if (len(outputString) == 0):
		sys.exit("AutoBatch_CodeGen->writeLinesToOutputString:  could not form any lines for the output string.")

	return outputString

def writeBodyOfInd():
	global individualVerFile

	individualOutputString = writeLinesToOutputString(verifyLines, indentationListVerifyLines, numTabsOnVerifyLine, 1)
	if ( (individualOutputString == None) or (type(individualOutputString).__name__ != con.strTypePython) or (len(individualOutputString) == 0) ):
		sys.exit("AutoBatch_CodeGen->writeBodyOfInd:  problem with value returned from writeLinesToOutputString.")

	individualOutputString += "\t\t\tpass\n"
	individualOutputString += "\t\telse:\n"
	individualOutputString += "\t\t\tincorrectIndices.append(sigIndex)\n\n"
	individualOutputString += "\treturn incorrectIndices\n"

	individualVerFile.write(individualOutputString)

def addFunctionsThatVerifyCalls():
	global batchVerFile, individualVerFile, verifySigsFile

	outputString = ""
	linePairsOfVerifyFuncs.sort()

	for linePair in linePairsOfVerifyFuncs:
		functionString = writeFunctionFromCodeToString(copy.deepcopy(pythonCodeLines), linePair[0], linePair[1], 0, numSpacesPerTab, True)
		if ( (functionString == None) or (type(functionString).__name__ != con.strTypePython) or (len(functionString) == 0) ):
			sys.exit("AutoBatch_CodeGen->addFunctionsThatVerifyCalls:  problem with function string returned from writeFunctionFromCodeToString.")

		outputString += functionString

	batchVerFile.write(outputString)
	individualVerFile.write(outputString)
	verifySigsFile.write(outputString)

def getLoopNamesOfFinalBatchEq():
	global loopNamesOfFinalBatchEq

	loopNamesOfFinalBatchEq = []

	batchEqWithLoopsCopy = finalBatchEqWithLoops.replace(con.finalBatchEqWithLoopsString, '', 1)

	tempList = getVarNamesAsStringNamesFromLine(batchEqWithLoopsCopy)

	for possibleLoopName in tempList:
		nameAsString = possibleLoopName.getStringVarName()
		isValidLoopName = isStringALoopName(nameAsString)
		if (isValidLoopName == False):
			continue
		loopNamesOfFinalBatchEq.append(copy.deepcopy(possibleLoopName))

	del tempList

def getLoopOrder(varListAsStrings):
	if ( (varListAsStrings == None) or (type(varListAsStrings).__name__ != con.listTypePython) or (len(varListAsStrings) == 0) ):
		sys.exit("AutoBatch_CodeGen->getLoopOrder:  problem with variable list parameter passed in.")

	loopOrder = []
	maxListSize = 0
	maxList = []

	for varName in varListAsStrings:
		if ( (varName == None) or (type(varName).__name__ != con.strTypePython) or (len(varName) == 0) ):
			sys.exit("AutoBach_CodeGen->getLoopOrder:  problem with one of the variable names within the list parameter passed in.")

		if (varName.find(con.loopIndicator) == -1):
			continue

		if (varName.count(con.loopIndicator) > 1):
			sys.exit("AutoBatch_CodeGen->getLoopOrder:  variable name contains more than one loop indicator symbol (" + con.loopIndicator + ").")

		currentList = []

		loopIndicatorIndex = varName.find(con.loopIndicator)
		subscriptIndicesStringSpaces = varName[(loopIndicatorIndex + 1):len(varName)]
		subscriptIndicesString = subscriptIndicesStringSpaces.lstrip().rstrip()
		splitString = subscriptIndicesString.split(con.loopIndicesSeparator)

		for indString in splitString:
			currentList.append(indString)

		currentSize = len(currentList)

		if (currentSize < maxListSize):
			continue

		if (currentSize == maxListSize):
			if (currentList != maxList):
				sys.exit("AutoBatch_CodeGen->getLoopOrder:  multiple lists of same size contain different loop orders.")
			else:
				continue

		maxList = copy.deepcopy(currentList)
		maxListSize = len(maxList)

	for loopNameEntry in maxList:
		loopNameEntryAsStringName = StringName()
		loopNameEntryAsStringName.setName(loopNameEntry)
		loopOrder.append(copy.deepcopy(loopNameEntryAsStringName))
		del loopNameEntryAsStringName

	return loopOrder

def distillLoopsWRTNumSignatures():
	global loopsOuterNumSignatures, loopsOuterNotNumSignatures

	for loop in loopInfo:
		loopNameToAdd = StringName()
		loopNameToAdd.setName(loop.getLoopName().getStringVarName())

		loopOrder = loop.getLoopOrder()
		outerIndexStringName = loopOrder[0]
		outerIndex = outerIndexStringName.getStringVarName()
		if (outerIndex not in con.loopIndexTypes):
			sys.exit("AutoBatch_CodeGen->distillLoopsWRTNumSignatures:  outer loop index extracted from one of the loops in loopInfo is not one of the supported loop index types.")
		if (outerIndex == con.numSignaturesIndex):
			loopsOuterNumSignatures.append(copy.deepcopy(loop))
		else:
			loopsOuterNotNumSignatures.append(copy.deepcopy(loop))

		del loopNameToAdd

def writeLinesToFile(lineNosToWriteToFile, numBaseTabs, outputFile):
	indentationListParam = []
	sourceLinesToWriteToFile = getSourceCodeLinesFromLineList(copy.deepcopy(pythonCodeLines), lineNosToWriteToFile, indentationListParam)
	batchOutputString = writeLinesToOutputString(sourceLinesToWriteToFile, indentationListParam, numTabsOnVerifyLine, numBaseTabs)
	outputFile.write(batchOutputString)

def writeOneBlockToFile(block, numBaseTabs, outputFile):
	if ( (block == None) or (type(block).__name__ != con.loopBlock) ):
		sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with block parameter passed in.")

	if ( (numBaseTabs == None) or (type(numBaseTabs).__name__ != con.intTypePython) or (numBaseTabs < 0) ):
		sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with number of base tabs parameter passed in.")

	blockStartValue = block.getStartValue().getValue()
	blockIndexVariable = block.getIndexVariable().getStringVarName()
	blockLoopOverValue = block.getLoopOverValue().getStringVarName()

	if ( (blockStartValue == None) or (type(blockStartValue).__name__ != con.intTypePython) or (blockStartValue < 0) ):
		sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with the start value of the block parameter passed in.")

	if ( (blockIndexVariable == None) or (type(blockIndexVariable).__name__ != con.strTypePython) or (blockIndexVariable not in con.loopIndexTypes) ):
		sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with the index variable of the block parameter passed in.")

	if ( (blockLoopOverValue == None) or (type(blockLoopOverValue).__name__ != con.strTypePython) or (blockLoopOverValue not in con.loopTypes) ):
		sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with the loop over value of the block parameter passed in.")

	outputString = ""
	outputString += getStringOfTabs(numBaseTabs)
	outputString += "for " + blockIndexVariable + " in range(" + str(blockStartValue) + ", " + blockLoopOverValue + "):\n"
	outputFile.write(outputString)
	outputString = ""

	childrenList = block.getChildrenList()
	if (childrenList != None):
		for childBlock in childrenList:
			if ( (childBlock == None) or (type(childBlock).__name__ != con.loopBlock) ):
				sys.exit("AutoBatch_CodeGen->writeOneBlockToFile:  problem with one of the child blocks from the block parameter passed in.")

			writeOneBlockToFile(childBlock, (numBaseTabs + 1), outputFile)

	loopsToCalculate = []

	blockLoopsWithVarsToCalc = block.getLoopsWithVarsToCalculate()
	if (blockLoopsWithVarsToCalc != None):
		blockLoopsWithVarsAsStrings = getStringNameListAsStringsNoDups(blockLoopsWithVarsToCalc)

		for blockLoopVarString in blockLoopsWithVarsAsStrings:
			loopsToCalculate.append(blockLoopVarString)

		variablesToCalculateAsStrings = getVariablesOfLoopsAsStrings(loopInfo, blockLoopsWithVarsAsStrings)
		lineNosToWriteToFile = getAllLineNosThatImpactVarList(variablesToCalculateAsStrings, con.verifyFuncName, lineNosPerVar, var_varDependencies)
		if (lineNosToWriteToFile != None):
			writeLinesToFile(lineNosToWriteToFile, numBaseTabs, outputFile)

	blockLoopsToCalc = block.getLoopsToCalculate()
	if (blockLoopsToCalc != None):
		blockLoopsAsStrings = getStringNameListAsStringsNoDups(blockLoopsToCalc)
		for blockLoopString in blockLoopsAsStrings:
			loopsToCalculate.append(blockLoopString)

	for loopToCalculate in loopsToCalculate:
		writeOneLoopCalculation(loopToCalculate, (numBaseTabs + 1), True, outputFile)

def writeOneLoopCalculation(loopName, numBaseTabs, forCachedCalcs, outputFile):
	if ( (loopName == None) or (type(loopName).__name__ != con.strTypePython) or (isStringALoopName(loopName) == False) ):
		sys.exit("AutoBatch_CodeGen->writeOneLoopCalcualtion:  problem with loop name parameter passed in.")

	if ( (numBaseTabs == None) or (type(numBaseTabs).__name__ != con.intTypePython) or (numBaseTabs < 0) ):
		sys.exit("AutoBatch_CodeGen->writeOneLoopCalculation:  problem with number of base tabs parameter passed in.")

	if ( (forCachedCalcs != True) and (forCachedCalcs != False) ):
		sys.exit("AutoBatch_CodeGen->writeOneLoopCalculation:  for cached calculations parameter is neither True nor False.")

	global cachedCalcsToPassToDC

	if loopName not in cachedCalcsToPassToDC:
		cachedCalcsToPassToDC.append(loopName)

	expression = getExpressionFromLoopInfoList(loopInfo, loopName)
	expressionCalcString = getExpressionCalcString(expression, loopName, numBaseTabs, forCachedCalcs)

	outputString = ""
	outputString += getStringOfTabs(numBaseTabs)
	outputString += expressionCalcString
	outputString += "\n"

	outputFile.write(outputString)

def getExpressionCalcString(expression, loopName, numBaseTabs, forCachedCalcs):
	outputString = ""
	outputString += loopName

	if (forCachedCalcs == True):
		outputString += "[" + con.numSignaturesIndex + "] = "

	expression = ensureSpacesBtwnTokens_CodeGen(expression)
	expression = expression.replace(' ^ ', ' ** ')

	expressionSplit = expression.split()
	for token in expressionSplit:
		if (token.count(con.loopIndicator) > 1):
			sys.exit("AutoBatch_CodeGen->getExpressionCalcString:  one of the tokens in the expression string contains more than one loop indicator symbol.  This is not currently supported.")

		if (token.count(con.loopIndicator) == 1):
			newToken = processTokenWithLoopIndicator(token)
			expression = expression.replace(token, newToken, 1)

	outputString += expression
	return outputString

def processTokenWithLoopIndicator(token):
	tokenSplit = token.split(con.loopIndicator)
	if (len(tokenSplit) != 2):
		sys.exit("AutoBatch_CodeGen->processTokenWithLoopIndicator:  token split by loop indicator symbol does not produce 2 sub-tokens.  This is not currently supported.")

	realTokenName = tokenSplit[0]

	if (realTokenName not in listVars):
		return realTokenName

	indicesString = listVars[realTokenName]

	indicesStringWithBraces = getIndicesStringWithBraces(indicesString)

	return realTokenName + indicesStringWithBraces

def getIndicesStringWithBraces(indicesString):
	if (indicesString.find(con.loopIndicesSeparator) == -1):
		return "[" + indicesString + "]"

	indicesStringSplit = indicesString.split(con.loopIndicesSeparator)

	retString = ""

	for index in indicesStringSplit:
		retString += "["
		retString += index
		retString += "]"

	return retString

def writeBodyOfNonCachedCalcsForDC():
	global verifySigsFile

	for block in loopBlocksForNonCachedCalculations:
		writeOneBlockToFile(block, 1, verifySigsFile)

def writeBodyOfCachedCalcsForBatch():
	global batchVerFile

	if ( (loopBlocksForCachedCalculations == None) or (type(loopBlocksForCachedCalculations).__name__ != con.listTypePython) or (len(loopBlocksForCachedCalculations) == 0) ):
		sys.exit("AutoBatch_CodeGen->writeBodyOfCachedCalcsForBatch:  problem with loopBlocksForCachedCalculations global parameter.")

	for block in loopBlocksForCachedCalculations:
		writeOneBlockToFile(block, 1, batchVerFile)

	batchVerFile.write("\n")

	nonLoopCachedVars = []

	global cachedCalcsToPassToDC

	for currPrecomputeVar in precomputeVars:
		currPrecomputeVarName = currPrecomputeVar.getVarName().getStringVarName()
		nonLoopCachedVars.append(currPrecomputeVarName)
		if currPrecomputeVarName not in cachedCalcsToPassToDC:
			cachedCalcsToPassToDC.append(currPrecomputeVarName)

	lineNosToWriteToFile = getAllLineNosThatImpactVarList(nonLoopCachedVars, con.verifyFuncName, lineNosPerVar, var_varDependencies)
	if ( (lineNosToWriteToFile == None) or (type(lineNosToWriteToFile).__name__ != con.listTypePython) or (len(lineNosToWriteToFile) == 0) ):
		sys.exit("AutoBatch_CodeGen->writeBodyOfCachedCalcsForBatch:  problem with value returned from getAllLineNosThatImpactVarList for non-loop cached variables.")

	writeLinesToFile(lineNosToWriteToFile, 0, batchVerFile)

	batchVerFile.write("\n")

	if (con.deltaDictName not in cachedCalcsToPassToDC):
		cachedCalcsToPassToDC.append(con.deltaDictName)

def writeDictDefsOfCachedCalcsForBatch():
	global batchVerFile

	if ( (loopBlocksForCachedCalculations == None) or (type(loopBlocksForCachedCalculations).__name__ != con.listTypePython) or (len(loopBlocksForCachedCalculations) == 0) ):
		sys.exit("AutoBatch_CodeGen->writeDictDefsOfCachedCalcsForBatch:  problem with loopBlocksForCachedCalculations global variable.")

	loopList = []

	for block in loopBlocksForCachedCalculations:
		if (block.getLoopsWithVarsToCalculate() != None):
			for loop in block.getLoopsWithVarsToCalculate():
				loopName = loop.getStringVarName()
				if (loopName not in loopList):
					loopList.append(loopName)

		if (block.getLoopsToCalculate() != None):
			for loop in block.getLoopsToCalculate():
				loopName = loop.getStringVarName()
				if (loopName not in loopList):
					loopList.append(loopName)

	batchOutputString = ""

	for loopName in loopList:
		batchOutputString += "\t" + loopName + " = {}\n"

	batchOutputString += "\n"
	batchVerFile.write(batchOutputString)

def writeCallToDCAndRetToBatch():
	global batchVerFile

	outputString = ""
	outputString += "\tverifySigsRecursive(verifyArgsDict, " + con.group + ", incorrectIndices, 0, " + con.numSignatures
	if (len(cachedCalcsToPassToDC) != 0):
		for cachedCalcName in cachedCalcsToPassToDC:
			outputString += ", "
			outputString += cachedCalcName

	outputString += ")\n\n"

	outputString += "\treturn incorrectIndices\n"

	batchVerFile.write(outputString)

def writeOpeningLinesToDCVerifySigsRecursiveFunc():
	global verifySigsFile

	verifyOutputString = ""
	verifyOutputString += "def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, EndSigNum"

	if (len(cachedCalcsToPassToDC) != 0):
		for cachedCalcName in cachedCalcsToPassToDC:
			verifyOutputString += ", "
			verifyOutputString += cachedCalcName

	verifyOutputString += "):\n"
	verifyOutputString += "\t" + con.group + " = groupObj\n\n"

	verifyOutputString += verifyPrereqs

	verifySigsFile.write(verifyOutputString)

def main():
	if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("\nUsage:  python " + sys.argv[0] + "\n \
			[input path and filename of Python code for signature scheme] \n \
			[input path and filename of output file from batcher] \n \
			[input path and filename of pickled Python dictionary with verify function arguments] \n \
			[output path and filename of individual verification Python module] \n \
			[output path and filename of batch verification Python module] \n \
			[output path and filename of divide-and-conquer Python module] \n")

	try:
		pythonCodeArg = sys.argv[1]
		batchVerifierOutputFile = sys.argv[2]
		verifyParamFilesArg = sys.argv[3]
		individualVerArg = sys.argv[4]
		batchVerArg = sys.argv[5]
		verifySigsArg = sys.argv[6]
	except:
		sys.exit("AutoBatch_CodeGen->main:  problem obtaining command-line arguments using sys.argv.")

	global pythonCodeLines, individualVerFile, batchVerFile, verifySigsFile, pythonCodeNode, varAssignments, verifyFuncNode, verifyLines 
	global verifyEqNode, functionArgMappings, callListOfVerifyFuncs, linePairsOfVerifyFuncs, verifyFuncArgs, indentationListVerifyLines
	global numTabsOnVerifyLine, batchVerifierOutput, finalBatchEq, finalBatchEqWithLoops, listVars, numSpacesPerTab, lineInfo
	global loopBlocksForCachedCalculations, loopBlocksForNonCachedCalculations, lineNosPerVar
	global lineNoOfFirstFunction, globalVars, var_varDependencies, functionArgNames, functionNames

	try:
		pythonCodeLines = open(pythonCodeArg, 'r').readlines()
		batchVerifierOutput = open(batchVerifierOutputFile, 'r').readlines()
		individualVerFile = open(individualVerArg, 'w')
		batchVerFile = open(batchVerArg, 'w')
		verifySigsFile = open(verifySigsArg, 'w')
	except:
		sys.exit("AutoBatch_CodeGen->main:  problem opening input/output files passed in as command-line arguments.")

	myASTParser = ASTParser()
	pythonCodeNode = myASTParser.getASTNodeFromFile(pythonCodeArg)
	if (pythonCodeNode == None):
		sys.exit("AutoBatch_CodeGen->main:  root node obtained from ASTParser->getASTNodeFromFile is of None type.")

	globalVars = getGlobalDeclVars(pythonCodeNode)
	if ( (globalVars != None) and (type(globalVars).__name__ != con.listTypePython) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getGlobalDeclVars.")

	functionNames = myASTParser.getFunctionNames(pythonCodeNode)
	if (functionNames == None):
		sys.exit("AutoBatch_CodeGen->main:  function names obtained from ASTParser->getFunctionNames is of None type.")

	lineNoOfFirstFunction = getLineNoOfFirstFunction(functionNames, myASTParser)
	if ( (lineNoOfFirstFunction == None) or (type(lineNoOfFirstFunction).__name__ != con.intTypePython) or (lineNoOfFirstFunction < 1) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value obtained from getLineNoOfFirstFunction.")

	(functionArgNames, lenFunctionArgDefaults) = myASTParser.getFunctionArgNamesAndDefaultLen(pythonCodeNode)
	if ( (functionArgNames == None) or (lenFunctionArgDefaults == None) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with the values returned from ASTParser->getFunctionArgNamesAndDefaultLen.")

	for funcName in con.funcNamesNotToTest:
		if (funcName in functionNames):
			del functionNames[funcName]
		if (funcName in functionArgNames):
			del functionArgNames[funcName]
		if (funcName in lenFunctionArgDefaults):
			del lenFunctionArgDefaults[funcName]

	functionArgMappings = getFunctionArgMappings(functionNames, functionArgNames, lenFunctionArgDefaults, myASTParser)
	if (functionArgMappings == None):
		sys.exit("AutoBatch_CodeGen->main:  mappings of variables passed between functions from getFunctionArgMappings is of None type.")

	varAssignments = getVarAssignments(pythonCodeNode, functionNames, myASTParser)
	if (varAssignments == None):
		sys.exit("AutoBatch_CodeGen->main:  getVarAssignments returned None when trying to get the variable assignments.")

	verifyFuncNodeList = myASTParser.getFunctionNode(pythonCodeNode, con.verifyFuncName)
	if (verifyFuncNodeList == None):
		sys.exit("AutoBatch_CodeGen->main:  could not locate a function with name " + con.verifyFuncName)
	if (len(verifyFuncNodeList) > 1):
		sys.exit("AutoBatch_CodeGen->main:  located more than one function with the name " + con.verifyFuncName)

	verifyFuncNode = verifyFuncNodeList[0]

	verifyEqNode = myASTParser.getLastEquation(verifyFuncNode)
	if (verifyEqNode == None):
		sys.exit("AutoBatch_CodeGen->main:  could not locate the verify equation within the " + con.verifyFuncName + " function.")

	verifyStartLine = myASTParser.getLineNumberOfNode(verifyFuncNode)
	if ( (verifyStartLine == None) or (type(verifyStartLine).__name__ != con.intTypePython) or (verifyStartLine < 1) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned for starting line of " + con.verifyFuncName + " function.")

	numSpacesOnVerifyFuncList = []
	getLinesFromSourceCodeWithinRange(copy.deepcopy(pythonCodeLines), verifyStartLine, (verifyStartLine + 1), numSpacesOnVerifyFuncList)
	if ( (numSpacesOnVerifyFuncList == None) or (type(numSpacesOnVerifyFuncList).__name__ != con.listTypePython) or (len(numSpacesOnVerifyFuncList) != 2) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getLinesFromSourceCodeWithinRange to determine the number of spaces on the line of the " + con.verifyfuncName + " function.")

	numSpacesOnVerifyFunc = numSpacesOnVerifyFuncList[0]
	if ( (numSpacesOnVerifyFunc == None) or (type(numSpacesOnVerifyFunc).__name__ != con.intTypePython) or (numSpacesOnVerifyFunc < 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with number of spaces extracted on the line of the " + con.verifyFuncName + " function.")

	numSpacesPerTab = numSpacesOnVerifyFuncList[1] - numSpacesOnVerifyFunc
	if ( (numSpacesPerTab == None) or (type(numSpacesPerTab).__name__ != con.intTypePython) or (numSpacesPerTab < 1) ):
		sys.exit("AutoBatch_codeGen->main:  problem with number obtained for the number of spaces per tab.")

	numTabsOnVerifyLine = determineNumTabsFromSpaces(numSpacesOnVerifyFunc, numSpacesPerTab)
	if ( (numTabsOnVerifyLine == None) or (type(numTabsOnVerifyLine).__name__ != con.intTypePython) or (numTabsOnVerifyLine < 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with number of tabs extracted on the line of the " + con.verifyFuncName + " function.")

	verifyStartLine += 1

	verifyEndLine = myASTParser.getLineNumberOfNode(verifyEqNode)
	if ( (verifyEndLine == None) or (type(verifyEndLine).__name__ != con.intTypePython) or (verifyEndLine < verifyStartLine) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned for ending line of " + con.verifyFuncName + " function.")

	indentationListVerifyLines = []
	verifyLines = getLinesFromSourceCodeWithinRange(copy.deepcopy(pythonCodeLines), verifyStartLine, verifyEndLine, indentationListVerifyLines)

	verifyFuncArgs = getFunctionArgsAsStrings(functionArgNames, con.verifyFuncName)
	if ( (verifyFuncArgs == None) or (type(verifyFuncArgs).__name__ != con.listTypePython) or (len(verifyFuncArgs) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getFunctionArgsAsStrings to get arguments of " + con.verifyFuncName + " function.")

	callListOfVerifyFuncs = []
	funcsVisitedSoFar = []
	linePairsOfVerifyFuncs = None
	buildCallListOfFunc(functionArgMappings, con.verifyFuncName, callListOfVerifyFuncs, funcsVisitedSoFar)

	if (con.initFuncName in functionNames):
		if (con.initFuncName not in callListOfVerifyFuncs):
			callListOfVerifyFuncs.append(con.initFuncName)

	callListOfInitFuncs = []
	funcsVisitedSoFar = []
	buildCallListOfFunc(functionArgMappings, con.initFuncName, callListOfInitFuncs, funcsVisitedSoFar)

	if (len(callListOfInitFuncs) > 0):
		for initCalledFunc in callListOfInitFuncs:
			if (initCalledFunc not in callListOfVerifyFuncs):
				callListOfVerifyFuncs.append(initCalledFunc)

	if (len(callListOfVerifyFuncs) > 0):
		linePairsOfVerifyFuncs = getFirstLastLineNosOfFuncList(callListOfVerifyFuncs, pythonCodeNode)
		if ( (linePairsOfVerifyFuncs == None) or (type(linePairsOfVerifyFuncs).__name__ != con.listTypePython) or (len(linePairsOfVerifyFuncs) == 0) ):
			sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getFirstLastLineNosOfFuncList.")

	addImportLines()
	addCommonHeaderLines()

	if (linePairsOfVerifyFuncs != None):
		addFunctionsThatVerifyCalls()

	addTemplateLines()
	addPrerequisites()

	if (con.initFuncName in functionNames):
		addCallToInit()

	addSigLoop()
	addGroupMembershipChecks()
	writeBodyOfInd()

	for line in batchVerifierOutput:
		if (line.startswith(con.finalBatchEqString) == True):
			if (finalBatchEq != None):
				sys.exit("AutoBatch_CodeGen->main:  more than one line starting with final batch equation string (" + con.finalBatchEqString + ") was found in the output from the batch verifier.")
			finalBatchEq = line
		if (line.startswith(con.finalBatchEqWithLoopsString) == True):
			if (finalBatchEqWithLoops != None):
				sys.exit("AutoBatch_CodeGen->main:  more than one line starting with final batch equation with loops string (" + con.finalBatchEqWithLoopsString + ") was found in the output from the batch verifier.")
			finalBatchEqWithLoops = line
		if (line.startswith(con.listString) == True):
			processListLine(line)
		if (line.startswith(con.precomputeString) == True):
			processPrecomputeLine(line)
		if (line.startswith(con.computeString) == True):
			processComputeLine(line)
		linePrefix = line[0:con.maxStrLengthForLoopNames]
		if (isStringALoopName(linePrefix) == True):
			processLoopLine(line)

	if ( (finalBatchEq == None) or (finalBatchEqWithLoops == None) ):
		sys.exit("AutoBatch_CodeGen->main:  problem locating the various forms of the final batch equation from the output of the batch verifier.")

	if (con.deltaDictName not in listVars):
		listVars[con.deltaDictName] = con.numSignaturesIndex

	cleanFinalBatchEq()
	getBatchEqVars()
	distillBatchEqVars()
	lineInfo = getLineInfoFromSourceCodeLines(copy.deepcopy(pythonCodeLines), numSpacesPerTab)
	if ( (lineInfo == None) or (type(lineInfo).__name__ != con.listTypePython) or (len(lineInfo) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  could not extract any line information from the source code Python lines of the cryptoscheme.")

	getLoopNamesOfFinalBatchEq()
	distillLoopsWRTNumSignatures()
	loopBlocksForCachedCalculations = buildLoopBlockList(loopsOuterNumSignatures)
	if ( (loopBlocksForCachedCalculations == None) or (type(loopBlocksForCachedCalculations).__name__ != con.listTypePython) or (len(loopBlocksForCachedCalculations) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem obtaining loop blocks used for cached calculations.")

	loopBlocksForNonCachedCalculations = buildLoopBlockList(loopsOuterNotNumSignatures, loopsOuterNumSignatures)
	if ( (loopBlocksForNonCachedCalculations == None) or (type(loopBlocksForNonCachedCalculations).__name__ != con.listTypePython) or (len(loopBlocksForNonCachedCalculations) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem obtaining loop blocks used for non-cached calculations.")

	lineNosPerVar = getLineNosPerVar(varAssignments)
	if ( (lineNosPerVar == None) or (type(lineNosPerVar).__name__ != con.dictTypePython) or (len(lineNosPerVar) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getLineNosPerVar.")

	var_varDependencies = getVar_VarDependencies(varAssignments, globalVars)
	if ( (var_varDependencies == None) or (type(var_varDependencies).__name__ != con.dictTypePython) or (len(var_varDependencies) == 0) ):
		sys.exit("AutoBatch_CodeGen->main:  problem with value returned from getVar_VarDependencies.")

	writeDictDefsOfCachedCalcsForBatch()
	writeBodyOfCachedCalcsForBatch()
	writeCallToDCAndRetToBatch()

	writeOpeningLinesToDCVerifySigsRecursiveFunc()
	writeBodyOfNonCachedCalcsForDC()

	try:
		batchVerFile.close()
		individualVerFile.close()
		verifySigsFile.close()
	except:
		sys.exit("AutoBatch_CodeGen->main:  problem attempting to run close() on the output files of this program.")

'''
	dotProdLoopOrder = getDotProdLoopOrder(computeLineInfo, outerDotProds, dotProdLoopOrder)	
	precomputeDotProdLoopOrder = getSplitDotProdLoopOrder(dotProdLoopOrder, computeLineInfo)
	DC_outerDotProds = getDC_outerDotProds_JUSTOUTER(dotProdLoopOrder, True)
	mydctest = getDC_outerDotProds_JUSTOUTER(dotProdLoopOrder, False)
	declaredLists = []
	batchOutputString = addListDeclarations(batchOutputString, computeLineInfo, verifyFuncArgs, declaredLists)
	batchOutputString = addDeltasAndArgSigIndexMap(batchOutputString, declaredLists)
	variableTypes = getVariableTypes(verifyFuncNode)
	verifySigsOutput = ""
	getPrecomputeOuterDotProds(precomputeDotProdLoopOrder)	
	batchOutputString = addDotProdLoops(batchOutputString, True, computeLineInfo, precomputeDotProdLoopOrder, assignMap, pythonCodeLines, listOfIndentedBlocks, numTabsOnVerifyFuncLine, verifyFuncArgs, declaredLists, outerDotProds)
	batchOutputString = addLinesForNonDotProdVars(batchOutputString, assignMap, pythonCodeLines, listOfIndentedBlocks, computeLineInfo, 1, verifyFuncArgs)	
	varNameFuncArgs = []	
	batchOutputString = addCallToVerifySigs(batchOutputString, precomputeOuterDotProds, varNameFuncArgs, verifyFuncArgs, pythonCodeNode)
	verifySigsFile = open(verifySigsFile, 'w')
	verifySigsOutput = ""
	for importFromLine in importFromLines:			
		verifySigsOutput += importFromLine + "\n"
	verifySigsOutput += "import hashlib\n"
	verifySigsOutput += "import sys, copy\n"
	verifySigsOutput += "from charm.engine.util import *\n"
	verifySigsOutput += "from toolbox.pairinggroup import *\n\n"
	verifySigsOutput += "bodyKey = \'Body\'\n\n"
	verifySigsOutput += "def verifySigsRecursive(group, deltaz, verifyFuncArgs, argSigIndexMap, verifyArgsDict, "
	for precomputeOuterDotProd in precomputeOuterDotProds:
		verifySigsOutput += precomputeOuterDotProd + ", "
	for varNameFuncArg in varNameFuncArgs:
		verifySigsOutput += varNameFuncArg + ", "
	verifySigsOutput += "startIndex, endIndex):\n\n"
	verifySigsOutput += "\t" + numSignersEndVal + " = " + actual_numSignersEndVal_value + "\n\n"
	verifySigsOutput += "\tsigNumKey = \'Signature_Number\'\n\n"
	verifySigsOutput += "\thashObj = hashlib.new('sha1')\n\n"	
	if (len(prereqAssignLineNos) > 0):
		for prereqLineNo in prereqAssignLineNos:
			prereqLine = getLinesFromSourceCode(pythonCodeLines, prereqLineNo, prereqLineNo, indentationList)
			verifySigsOutput += "\t" + str(prereqLine[0]) + "\n"
	verifySigsOutput = resetArgSigIndexDictTo1s(verifySigsOutput)
	outerDotProdsDict = {}
	outerDotProdsDict['key'] = outerDotProds
	verifySigsOutput = addResetStatementsForDotProdCalcs(verifySigsOutput, outerDotProdsDict, 1)	
	if (isTopLayerLoopOverNumSignatures(dotProdLoopOrder) == False):	
		verifySigsOutput = addDotProdLoops(verifySigsOutput, False, computeLineInfo, DC_outerDotProds, assignMap, pythonCodeLines, listOfIndentedBlocks, numTabsOnVerifyFuncLine, verifyFuncArgs, declaredLists, outerDotProds)
	verifySigsOutput += "\n"
	verifySigsOutput += "\tfor index in range(startIndex, endIndex):\n"
	for outerDotProd in outerDotProds:
		if (outerDotProd.startswith(dotProdPrefix) == True)  and (outerDotProd in precomputeOuterDotProds):
			verifySigsOutput += "\t\t" + outerDotProd + "_runningProduct = " + outerDotProd + "_runningProduct * " + outerDotProd + "[index]\n"
		elif (outerDotProd.startswith(sumPrefix) == True) and (outerDotProd in precomputeOuterDotProds):	
			verifySigsOutput += "\t\t" + outerDotProd + "_runningProduct = " + outerDotProd + "_runningProduct + " + outerDotProd + "[index]\n"
	verifySigsOutput += "\n"
	simplifiedFinalBatchEq = getSimplifiedFinalBatchEq(batchVerifierOutput, pythonCodeNode, verifyFuncArgs, varNameFuncArgs)	
	verifySigsOutput = addEqualityTestFromFinalBatchEq(verifySigsOutput, simplifiedFinalBatchEq, outerDotProds, varNameFuncArgs, precomputeOuterDotProds)

'''

if __name__ == '__main__':
	main()
