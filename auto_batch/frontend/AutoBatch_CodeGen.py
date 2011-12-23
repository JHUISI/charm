import copy, os, sys
from ASTParser import *
from Parser_CodeGen_Toolbox import *

batchVerFile = None
individualVerFile = None
pythonCodeLines = None
pythonCodeNode = None
verifySigsFile = None

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

class GetLastLineOfFunction(ast.NodeVisitor):
	def __init__(self):
		self.lastLine = 0

	def generic_visit(self, node):
		#print(node._fields)
		try:
			if (node.lineno > self.lastLine):
				self.lastLine = node.lineno
		except:
			pass
		ast.NodeVisitor.generic_visit(self, node)

	def getLastLine(self):
		return self.lastLine

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

def isPreviousCharAlpha(line, currIndex):
	if (currIndex == 0):
		return False
	
	if (line[currIndex - 1].isalpha() == True):
		return True
	
	return False


def isNextCharAlpha(line, currIndex):
	lastCharIndex = len(line) - 1
	if (currIndex == lastCharIndex):
		return False
	
	if (line[currIndex + 1].isalpha() == True):
		return True
	
	return False


def isLineOnlyWhiteSpace(line):
	line = line.lstrip().rstrip()
	if (line == ""):
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

def getNumIndentedSpaces(line):
	lenOfLine = len(line)
	for index in range(0, lenOfLine):
		if (line[index] != space):
			break

	#print(line)

	#if (index == 0):
		#sys.exit("Error:  one of the lines in the verify() function is not preceded by a space.")

	return index

def getLinesFromSourceCode(lines, startLine, endLine, indentationList):
	retLines = []
	lineCounter = 1

	for line in lines:
		if (lineCounter > endLine):
			return retLines
		if (lineCounter >= startLine):
			numIndentedSpaces = getNumIndentedSpaces(line)
			tempLine = line.lstrip().rstrip()
			if ( (not tempLine.startswith(printPrefix)) and (not tempLine.startswith(commentPrefix)) ):
				#print(tempLine)
				retLines.append(tempLine)
				indentationList.append(numIndentedSpaces)
		lineCounter += 1

def ensureSpacesBtwnTokens(lineOfCode):
	if (lineOfCode == '\n'):
		return lineOfCode

	lenOfLine = len(lineOfCode)
	if (lineOfCode[lenOfLine - 1] == '\n'):
		lineOfCode = lineOfCode[0:(lenOfLine-1)]

	
	L_index = 1
	R_index = 1
	withinApostrophes = False

	while (True):
		checkForSpace = False
		if ( (lineOfCode[R_index] == '\'') or (lineOfCode[R_index] == '\"') ):
			if (withinApostrophes == True):
				withinApostrophes = False
			else:
				withinApostrophes = True
		if (withinApostrophes == True):
			pass
		elif (lineOfCode[R_index] in ['^', '+', '(', ')', '{', '}', '-', ',', '[', ']']):
			currChars = lineOfCode[R_index]
			L_index = R_index
			checkForSpace = True
			
			
		elif ( (lineOfCode[R_index] == 'e') and (isPreviousCharAlpha(lineOfCode, R_index) == False) ):
			currChars = lineOfCode[R_index]
			L_index = R_index
			checkForSpace = True
			
			
				
		#elif ( (lineOfCode[R_index] == '[') and (isPreviousCharAlpha(lineOfCode, R_index) == False) ):
			#currChars = lineOfCode[R_index]
			#L_index = R_index
			#checkForSpace = True

		elif (lineOfCode[R_index] in ['>', '<', ':', '!', '=']):
			if (lineOfCode[R_index+1] == '='):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '&'):
			if (lineOfCode[R_index+1] == '&'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '/'):
			if (lineOfCode[R_index+1] == '/'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '|'):
			if (lineOfCode[R_index+1] == '|'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == '*'):
			if (lineOfCode[R_index+1] == '*'):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				currChars = lineOfCode[R_index]
				L_index = R_index
				checkForSpace = True
		elif (lineOfCode[R_index] == 'H'):
			if (lineOfCode[R_index+1] == '('):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				checkForSpace = False
		elif (lineOfCode[R_index] == 'e'):
			if ( (lineOfCode[R_index+1] == '(') and (isPreviousCharAlpha(lineOfCode, R_index) == False) ):
				L_index = R_index
				R_index += 1
				currChars = lineOfCode[L_index:(R_index+1)]
				checkForSpace = True
			else:
				checkForSpace = False
		if (checkForSpace == True):
			if ( (lineOfCode[L_index-1] != ' ') and (lineOfCode[R_index+1] != ' ') ):
				lenOfLine = len(lineOfCode)
				if ( (R_index + 1) == (lenOfLine - 1) ):
					lineOfCode = lineOfCode[0:L_index] + ' ' + currChars + ' ' + lineOfCode[R_index+1]
				else:
					lineOfCode = lineOfCode[0:L_index] + ' ' + currChars + ' ' + lineOfCode[(R_index+1):lenOfLine]
				R_index += 3
			elif ( (lineOfCode[L_index-1] != ' ') and (lineOfCode[R_index+1] == ' ') ):
				lenOfLine = len(lineOfCode)
				if (L_index == (lenOfLine - 1) ):
					lineOfCode = lineOfCode[0:L_index] + ' ' + lineOfCode[L_index]
				else:
					lineOfCode = lineOfCode[0:L_index] + ' ' + lineOfCode[L_index:lenOfLine]
				R_index += 2
			elif ( (lineOfCode[L_index-1] == ' ') and (lineOfCode[R_index+1] != ' ') ):
				lenOfLine = len(lineOfCode)
				if ( (R_index + 1) == (lenOfLine - 1) ):
					lineOfCode = lineOfCode[0:(R_index+1)] + ' ' + lineOfCode[R_index+1]
				else:
					lineOfCode = lineOfCode[0:(R_index+1)] + ' ' + lineOfCode[(R_index+1):lenOfLine]
				R_index += 2
			elif ( (lineOfCode[L_index-1] == ' ') and (lineOfCode[R_index+1] == ' ') ):
				R_index += 2
		else:
			R_index += 1

		lenOfLine = len(lineOfCode)

		#CHEAP HACK!!!!  THIS MUST BE FIXED
		if (R_index == (lenOfLine - 1)):
			if (lineOfCode[R_index] == ']'):
				lineOfCode = lineOfCode[0:R_index] + ' ]'
				break
			elif (lineOfCode[R_index] == ')'):
				lineOfCode = lineOfCode[0:R_index] + ' )'
				break			
			elif (lineOfCode[R_index] == ':'):
				lineOfCode = lineOfCode[0:R_index] + ' :'
				break
			
			
			
		
		if (R_index >= (lenOfLine - 1)):
			break

	lenOfLine = len(lineOfCode)
	if ( (lineOfCode[0] == '(' ) and (lineOfCode[1] != ' ') ):
		lineOfCode = '( ' + lineOfCode[1:lenOfLine]
	if ( (lineOfCode[lenOfLine-1] == ')' ) and (lineOfCode[lenOfLine-2] != ' ') ):
		lineOfCode = lineOfCode[0:(lenOfLine-1)] + ' )'

	lineOfCode = ' ' + lineOfCode + ' '

	return lineOfCode

def removeLeftParanSpaces(line):
	nextLParanIndex = line.find(lParan)

	while (nextLParanIndex != -1):
		if ( (nextLParanIndex > 0) and (line[nextLParanIndex - 1] == space) ):
			lenOfLine = len(line)
			line = line[0:(nextLParanIndex - 1)] + line[nextLParanIndex:lenOfLine]
			nextLParanIndex = line.find(lParan, nextLParanIndex)
		else:
			nextLParanIndex = line.find(lParan, (nextLParanIndex + 1))

	return line

def determineNumTabs(numSpaces):
	if ( (numSpaces % numSpacesPerTab) != 0):
		sys.exit("Error:  Python cryptosystem did not use proper number of spaces per tab.")

	return (int(numSpaces / numSpacesPerTab))

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

def cleanFinalBatchEq(finalBatchEq):
	
	finalBatchEq = finalBatchEq.replace(finalBatchEqTag, '', 1)
	finalBatchEq = finalBatchEq.replace(':', '', 1)
	finalBatchEq = finalBatchEq.lstrip()
	
	#finalBatchEq = finalBatchEq.lstrip(finalBatchEqTag).lstrip(':').lstrip()
	
	
	finalBatchEq = ensureSpacesBtwnTokens(finalBatchEq)
	
	#finalBatchEq = finalBatchEq.rstrip()
	
	#print(finalBatchEq)
	
	return finalBatchEq
	
	#print(finalBatchEq)

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

def getBatchEqVars(finalBatchEq):
	batchEqVars = finalBatchEq.split()
	for removeVar in batchEqRemoveVars:
		while (batchEqVars.count(removeVar) > 0):
			batchEqVars.remove(removeVar)
	
	for dupVar in batchEqVars:
		while (batchEqVars.count(dupVar) > 1):
			batchEqVars.remove(dupVar)

	#print(batchEqVars)
			
	if (batchEqVars.count(deltaString) == 1):
		batchEqVars.remove(deltaString)
	
	if (batchEqVars.count(deltaDotProdString) == 1):
		batchEqVars.remove(deltaDotProdString)

	return batchEqVars

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

def getVarsThatAreLists(line):
	line = line.replace("List := ", '', 1)
	line = line.rstrip()
	#line = line.lstrip("List : = ").rstrip()
	lineSplit = line.split(' in ')
	
	varName = lineSplit[0].lstrip().rstrip()
	endVal = lineSplit[1].lstrip().rstrip()

	if (endVal == 'N'):
		varsThatAreLists[varName] = numSignaturesIndex
	elif (endVal == 'l'):
		varsThatAreLists[varName] = numSignersIndex

def getPrecomputeVarReplacements(batchVerifierOutput):
	for line in batchVerifierOutput:
		if (line.startswith("Precompute: ")):			
			line = line[len("Precompute: "):len(line)]
			line = line.lstrip().rstrip()
			if (line.startswith("delta := ")):
				continue
			#line = line.lstrip("Precompute: ").rstrip()
			
			if ( (line.startswith("pre")) == False  ):
				continue
			
			lineSplit = line.split(" := ")
			key = lineSplit[0].lstrip().rstrip()
			val = lineSplit[1].lstrip().rstrip()
			precomputeVarReplacements[key] = val
			
			#print(lineSplit[0])
			#print(lineSplit[1])
			#print(line)

def getDotProdTypes(batchVerifierOutput):
	for line in batchVerifierOutput:
		if ( (line.startswith("dot")) or (line.startswith("sum"))):
			line = line.split(" := ")
			dotProdName = line[0].lstrip().rstrip()
			dotProdType = line[1].lstrip().rstrip().rstrip("\n")
			dotProdTypes[dotProdName] = dotProdType

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
	importLines = getImportLines(pythonCodeNode, pythonCodeLines)
	if (importLines == None):
		return

	if ( (type(importLines).__name__ != con.listTypePython) or (len(importLines) == 0) ):
		sys.exit("AutoBatch_CodeGen->addImportLines:  problem with value returned from getImportLines.")

	for index in range(0, len(importLines)):
		batchVerFile.write(importLines[index])
		individualVerFile.write(importLines[index])
		verifySigsFile.write(importLines[index])

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

	try:

		pythonCodeLines = open(pythonCodeArg, 'r').readlines()
		individualVerFile = open(individualVerArg, 'w')
		batchVerFile = open(batchVerArg, 'w')
		verifySigsFile = open(verifySigsArg, 'w')
	except:
		sys.exit("AutoBatch_CodeGen->main:  problem opening input/output files passed in as command-line arguments.")

	myASTParser = ASTParser()
	pythonCodeNode = myASTParser.getASTNodeFromFile(pythonCodeArg)
	if (pythonCodeNode == None):
		sys.exit("AutoBatch_CodeGen->main:  root node obtained from ASTParser->getASTNodeFromFile is of None type.")

	addImportLines()

	try:
		batchVerFile.close()
		individualVerFile.close()
		verifySigsFile.close()
	except:
		sys.exit("AutoBatch_CodeGen->main:  problem attempting to run close() on the output files of this program.")
'''


	individualTemplateLines = open(individualTemplate, 'r').readlines()
	batchTemplateLines = open(batchTemplate, 'r').readlines()

	for line in individualTemplateLines:
		individualVerFile.write(line)
		
	for line in batchTemplateLines:
		batchVerFile.write(line)
	
	verifyFuncNode = getVerifyFuncNode(pythonCodeNode)
	verifyFuncArgs = getVerifyFuncArgs(verifyFuncNode)
	#print(verifyFuncArgs)

	verifyEqNode = getVerifyEqNode(verifyFuncNode)
	if (verifyEqNode == 0):
		sys.exit("Could not locate the verify equation within the \"verify\" function")

	#buildMapOfControlFlow(pythonCodeLines, verifyFuncNode.lineno, (verifyEqNode.lineno - 1))

	lastLineVisitor = GetLastLineOfFunction()
	lastLineVisitor.visit(verifyFuncNode)
	lastLineOfVerifyFunc = lastLineVisitor.getLastLine()
	#print(lastLineOfVerifyFunc)

	individualOutputString = ""
	batchOutputString = ""

	individualOutputString += "\n"
	batchOutputString += "\n"

	indentationList = []

	verifyFuncLine = getLinesFromSourceCode(pythonCodeLines, verifyFuncNode.lineno, verifyFuncNode.lineno, indentationList)	
	numTabsOnVerifyFuncLine = determineNumTabs(indentationList[0])

	prereqVisitor = PrereqAssignVisitor()
	prereqVisitor.visit(pythonCodeNode)
	prereqAssignLineNos = prereqVisitor.getPrereqAssignLineNos()

	indentationList = []

	if (len(prereqAssignLineNos) > 0):
		for prereqLineNo in prereqAssignLineNos:
			prereqLine = getLinesFromSourceCode(pythonCodeLines, prereqLineNo, prereqLineNo, indentationList)
			individualOutputString += "\t" + str(prereqLine[0]) + "\n"
			batchOutputString += "\t" + str(prereqLine[0]) + "\n"

	batchOutputString = addNumSigsSignersDefs(batchOutputString, pythonCodeLines)

	indentationList = []

	verifyLines = getLinesFromSourceCode(pythonCodeLines, (verifyFuncNode.lineno + 1), verifyEqNode.lineno, indentationList)

	lineNumber = -1

	individualOutputString += "\n\tfor sigIndex in range(0, numSigs):\n"
	individualOutputString += "\t\tfor arg in verifyFuncArgs:\n"
	individualOutputString += "\t\t\tif (sigNumKey in verifyArgsDict[sigIndex][arg]):\n"
	individualOutputString += "\t\t\t\targSigIndexMap[arg] = int(verifyArgsDict[sigIndex][arg][sigNumKey])\n"
	individualOutputString += "\t\t\telse:\n"
	individualOutputString += "\t\t\t\targSigIndexMap[arg] = sigIndex\n"

	for line in verifyLines:
		lineNumber += 1
		if (isLineOnlyWhiteSpace(line) == True):
			continue
		line = ensureSpacesBtwnTokens(line)
		#print(line)
		for arg in verifyFuncArgs:
			argWithSpaces = ' ' + arg + ' '
			numArgMatches = line.count(argWithSpaces)
			for countIndex in range(0, numArgMatches):
				#print(argWithSpaces)
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
				#print(line)
				#print("\n\n")
		#print(line)
		line = line.lstrip().rstrip()
		#print(line)
		line = removeLeftParanSpaces(line)
		#print(line)
		#print("\n\n")
		line = removeSelfDump(line)
		numTabs = determineNumTabs(indentationList[lineNumber]) - numTabsOnVerifyFuncLine
		numTabs += 1
		for tabNumber in range(0, numTabs):
			individualOutputString += "\t"
		individualOutputString += line + "\n"

	individualOutputString += "\t\t\tpass\n"
	individualOutputString += "\t\telse:\n"
	individualOutputString += "\t\t\tprint(\"Verification of signature \" + str(sigIndex) + \" failed.\\n\")\n"

	#os.system("python " + batchVerifierPythonFile + " " + batchVerifierInputFile + " > " + batchVerifierOutputFile)
	batchVerifierOutput = open(batchVerifierOutputFile, 'r').readlines()
	for line in batchVerifierOutput:
		if (line.startswith(finalBatchEqTag) == True):
			finalBatchEq = line
		elif (line.startswith('List := ') == True):
			getVarsThatAreLists(line)
			
			
			
	for line in pythonCodeLines:		
		if (line.startswith(numSignersEndVal + ' = ')):
			actual_numSignersEndVal_value = (line[4])

	getPrecomputeVarReplacements(batchVerifierOutput)
	getDotProdTypes(batchVerifierOutput)
	finalBatchEq = cleanFinalBatchEq(finalBatchEq)
	
	batchEqVars = getBatchEqVars(finalBatchEq)
	batchEqDotProdVars = [] #not used
	batchEqSumVars = [] #not used
	batchEqNotSumOrDotVars = []
	
	distillBatchEqVars(batchEqVars, batchEqNotSumOrDotVars)
	assignMapVar = BuildAssignMap()
	assignMapVar.visit(verifyFuncNode)
	assignMap = assignMapVar.getAssignMap()
	listOfIndentedBlocks = buildMapOfControlFlow(pythonCodeLines, verifyFuncNode.lineno, (verifyEqNode.lineno - 1))
	computeLineInfo = getComputeLineInfo(batchVerifierOutput)	
	outerDotProds = getOuterDotProds(batchVerifierOutput)
	dotProdLoopOrder = []	
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
	
	
	
	#precomputeOuterDotProds = getPrecomputeOuterDotProds(precomputeDotProdLoopOrder)
	
	
	
	
		
	#getPrecomputeOuterDotProds(precomputeDotProdLoopOrder)	
	
	
	
	
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
	
	
	#assignMapFor_l = BuildAssignMap()
	#assignMapFor_l.visit(pythonCodeNode)
	#assignMapFor_l_map = assignMapFor_l.getAssignMap()
	
	
	
	
	
	#print(assignMapFor_l_map[numSignersEndVal])
	
	
	if (len(prereqAssignLineNos) > 0):
		for prereqLineNo in prereqAssignLineNos:
			prereqLine = getLinesFromSourceCode(pythonCodeLines, prereqLineNo, prereqLineNo, indentationList)
			verifySigsOutput += "\t" + str(prereqLine[0]) + "\n"
			#batchOutputString += "\t" + str(prereqLine[0]) + "\n"
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

	individualVerFile.write(individualOutputString)
	batchVerFile.write(batchOutputString)
	individualVerFile.close()
	batchVerFile.close()

	verifySigsFile.write(verifySigsOutput)
	verifySigsFile.close()

	#os.system("python " + individualVerArg)
	#os.system("python " + batchVerArg)
'''

if __name__ == '__main__':
	main()
