#TODO:  get ensurespacesbetweentokens in here, run every
#line of verify through it
#then go through and replace each variable name with the
#right variable in the verify dict

'''
Requirements:

- The definition line for the verify function in the 
Charm code for the scheme must be on one line.  For example,

def verify(pk, sig, M):

This must all be on one line.
'''

import ast, os, sys

nameOfVerifyFunc = 'verify'
argsRepInAST = 'args'
argRepInAST = 'arg'
selfRepInAST = 'self'
idRepInAST = 'id'
lambdaRepInAST = 'Lambda'
callRepInAST = 'Call'
funcRepInAST = 'func'
sigNumKey = 'Signature_Number'
bodyKey = 'Body'
individualTemplate = '/Users/matt/Documents/charm/auto_batch/frontend/IndividualVerifyTemplate.py'
batchTemplate = '/Users/matt/Documents/charm/auto_batch/frontend/BatchVerifyTemplate.py'
equalityOperator = 'Eq()'
printPrefix = 'print('
commentPrefix = '#'
dictBeginChar = '['
lParan = '('
space = ' '
numSpacesPerTab = 4
pairFuncNames = ['pairing', 'PairingGroup']
selfDump = 'self.dump('
selfDumpLen = len(selfDump)
batchVerifierPythonFile = '/Users/matt/Documents/charm/auto_batch/batchverify.py'
batchVerifierOutputFile = '/Users/matt/Documents/charm/auto_batch/frontend/batchVerifierOutput'
finalBatchEqTag = 'Final batch eq'
numBitsOfSecurity = 80
deltasGroupType = 'ZR'
batchEqRemoveVars = ['e', '(', 'j', '1', 'prod', '{', '}', 'N', ':=', '^', ',', 'on', ')', '==']
dotProdSuffix = '_j'
deltaString = 'delta'
idRepInAST = 'id'
eltsRepInAST = 'elts'
unknownType = 'Unknown'

class ImportFromVisitor(ast.NodeVisitor):
	def __init__(self):
		self.lineNos = []

	def visit_ImportFrom(self, node):
		self.lineNos.append(node.lineno)

	def getImportFromLineNos(self):
		if (len(self.lineNos) == 0):
			return 0

		return self.lineNos

class GetLastLineOfFunction(ast.NodeVisitor):
	def __init__(self):
		self.lastLine = 0

	'''
	def checkNextNode(self, node):
		print(node.lineno)
		if (node.lineno > self.lastLine):
			self.lastLine = node.lineno
	'''

	'''
	def visit_Module(self, node):
		self.checkNextNode(node)

	def visit_Interactive(self, node):
		self.checkNextNode(node)

	def visit_Expression(self, node):
		self.checkNextNode(node)

	#def visit_Assign(self, node):
		#self.checkNextNode(node)
	'''

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
			return node.id
		else:
			return unknownType

	'''
		for childNode in ast.iter_child_nodes(node):
			retVal = self.getTargetName(childNode)
			if (retVal != unknownType):
				return retVal
		
		return unknownType
	'''
		
	def buildNameDictEntry(self, node):
		targetName = self.getName(node)
		if (targetName == unknownType):
			return
		self.assignMap[targetName] = {}
		self.assignMap[targetName][node.lineno] = {}
		
	#def buildValuesDictEntries(self, node, targetName):

	def visit_Assign(self, node):
		if (eltsRepInAST in node.targets[0]._fields):
			for eltsIndex in range(0, len(node.targets[0].elts)):
				targetName = self.buildNameDictEntry(node.targets[0].elts[eltsIndex])
				if (targetName == unknownType):
					return 
				#valuesResult = self.buildValuesDictEntries(node.)
				

				
		
		
		#targetNames = []
		#targetNames = self.getTargetNames(node.targets[0], targetNames)
		#print(targetNames)

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

def getRootASTNode(lines):
	code = ""
	for line in lines:
		code += line
	return ast.parse(code)

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
	L_index = 1
	R_index = 1
	withinApostrophes = False

	while (True):
		checkForSpace = False
		if (lineOfCode[R_index] == '\''):
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
	#print(finalBatchEq)
	finalBatchEq = finalBatchEq.lstrip(finalBatchEqTag).lstrip(':').lstrip()
	
	
	finalBatchEq = ensureSpacesBtwnTokens(finalBatchEq)
	
	#finalBatchEq = finalBatchEq.rstrip()
	
	return finalBatchEq
	
	#print(finalBatchEq)

def addDeltas(batchOutputString):
	batchOutputString += "\n\tdeltas = []\n\n"
	batchOutputString += "\tfor sigIndex in range(1, (numSigs+1)):\n"
	batchOutputString += "\t\tdeltas.append(prng_bits(" + deltasGroupType + ", " + str(numBitsOfSecurity) + "))\n\n"
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
	batchEqVarsSplit = finalBatchEq.split()
	for removeVar in batchEqRemoveVars:
		while (batchEqVarsSplit.count(removeVar) > 0):
			batchEqVarsSplit.remove(removeVar)

	for varIndex in range(0, len(batchEqVarsSplit)):
		batchEqVarsSplit[varIndex] = batchEqVarsSplit[varIndex].rstrip(dotProdSuffix)
	
	for dupVar in batchEqVarsSplit:
		while (batchEqVarsSplit.count(dupVar) > 1):
			batchEqVarsSplit.remove(dupVar)
			
	if (batchEqVarsSplit.count(deltaString) == 1):
		batchEqVarsSplit.remove(deltaString)

	return batchEqVarsSplit

if __name__ == '__main__':
	if ( (len(sys.argv) != 6) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("\nUsage:  python Code_Generator.py \n [individual verification output filename] \n [batch verification output filename] \n [filename of Python code for signature scheme] \n [filename of pickled Python dictionary with verify function arguments] \n [filename of .bv file that will be input for the batch verifier] \n")

	individualVerArg = sys.argv[1]
	batchVerArg = sys.argv[2]
	pythonCodeArg = sys.argv[3]
	verifyParamFilesArg = sys.argv[4]
	batchVerifierInputFile = sys.argv[5]

	#os.system("cp " + individualTemplate + " " + individualVerArg)
	#os.system("cp " + batchTemplate + " " + batchVerArg)

	individualVerFile = open(individualVerArg, 'w')
	batchVerFile = open(batchVerArg, 'w')

	pythonCodeLines = open(pythonCodeArg, 'r').readlines()

	pythonCodeNode = getRootASTNode(pythonCodeLines)
	
	
	importFromLines = getImportFromLines(pythonCodeNode, pythonCodeLines)
	for importFromLine in importFromLines:			
		#individualOutputString += "\t" + str(importFromLine) + "\n"
		individualVerFile.write(importFromLine)
		individualVerFile.write("\n")
		batchVerFile.write(importFromLine)
		batchVerFile.write("\n")

	individualTemplateLines = open(individualTemplate, 'r').readlines()
	batchTemplateLines = open(batchTemplate, 'r').readlines()

	for line in individualTemplateLines:
		individualVerFile.write(line)
		
	for line in batchTemplateLines:
		batchVerFile.write(line)
	
	verifyFuncNode = getVerifyFuncNode(pythonCodeNode)
	verifyFuncArgs = getVerifyFuncArgs(verifyFuncNode)

	verifyEqNode = getVerifyEqNode(verifyFuncNode)
	if (verifyEqNode == 0):
		sys.exit("Could not locate the verify equation within the \"verify\" function")

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
	#print(verifyFuncLine)
	#numSpacesOnVerifyFuncLine = getNumIndentedSpaces(indentationList[0])
	#print(numSpacesOnVerifyFuncLine)
	numTabsOnVerifyFuncLine = determineNumTabs(indentationList[0])
	#print(numTabsOnVerifyFuncLine)

	#individualOutputString += "\tfrom charm.engine.util import *\n"


	prereqVisitor = PrereqAssignVisitor()
	prereqVisitor.visit(pythonCodeNode)
	prereqAssignLineNos = prereqVisitor.getPrereqAssignLineNos()

	indentationList = []

	if (len(prereqAssignLineNos) > 0):
		for prereqLineNo in prereqAssignLineNos:
			prereqLine = getLinesFromSourceCode(pythonCodeLines, prereqLineNo, prereqLineNo, indentationList)
			individualOutputString += "\t" + str(prereqLine[0]) + "\n"
			batchOutputString += "\t" + str(prereqLine[0]) + "\n"

	indentationList = []

	verifyLines = getLinesFromSourceCode(pythonCodeLines, (verifyFuncNode.lineno + 1), verifyEqNode.lineno, indentationList)

	lineNumber = -1

	individualOutputString += "\n\tfor sigIndex in range(1, (numSigs+1)):\n"
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
			break

	finalBatchEq = cleanFinalBatchEq(finalBatchEq)
	
	batchEqVars = getBatchEqVars(finalBatchEq)
	
	test = BuildAssignMap()
	test.visit(verifyFuncNode)
	
	#print(batchEqVars)
    
	#print(finalBatchEq.split())
	
	batchOutputString = addDeltas(batchOutputString)
	
	batchOutputString = addIfElse(batchOutputString, finalBatchEq)

	individualVerFile.write(individualOutputString)
	batchVerFile.write(batchOutputString)

	individualVerFile.close()
	batchVerFile.close()

	#os.system("python " + individualVerArg)
	#os.system("python " + batchVerArg)
