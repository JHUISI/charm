import con, sys
from ASTParser import *

def getLinesFromSourceCode(sourceCodeLines, lineNos):
	if ( (sourceCodeLines == None) or (type(sourceCodeLines).__name__ != con.listTypePython) or (len(sourceCodeLines) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getLinesFromSourceCode:  problem with source code lines passed in.")

	if ( (lineNos == None) or (type(lineNos).__name__ != con.listTypePython) or (len(lineNos) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getLinesFromSourceCode:  problem with line numbers passed in.")

	matchingLines = []

	lineNos = list(set(lineNos))
	lenLineNos = len(lineNos)
	lastLineNo = lineNos[lenLineNos - 1]

	lastSourceCodeLineNo = len(sourceCodeLines)

	if (lastLineNo > lastSourceCodeLineNo):
		sys.exit("Parser_CodeGen_Toolbox->getLinesFromSourceCode:  one of the line numbers passed in exceeds the number of lines in the source code passed in.")

	for index in range(0, lenLineNos):
		nextMatchingLineNo = lineNos[index]
		nextMatchingLine = sourceCodeLines[nextMatchingLineNo - 1]
		matchingLines.append(nextMatchingLine)

	if (len(matchingLines) == 0):
		return None

	return matchingLines

def getImportLines(rootNode, sourceCodeLines):
	if ( (rootNode == None) or (sourceCodeLines == None) or (type(sourceCodeLines).__name__ != con.listTypePython) or (len(sourceCodeLines) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getImportLines:  problem with one of the parameters passed in.")

	myASTParser = ASTParser()
	importLineNos = myASTParser.getImportLineNos(rootNode)
	if (importLineNos == None):
		return None

	if ( (type(importLineNos).__name__ != con.listTypePython) or (len(importLineNos) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getImportLines:  problem with import line numbers returned from ASTParser->getImportLineNos.")

	importLines = getLinesFromSourceCode(sourceCodeLines, importLineNos)
	if ( (importLines == None) or (type(importLines).__name__ != con.listTypePython) or (len(importLines) == 0) ):
		sys.exit("Parser_CodeGen_Toolbox->getImportLines:  problem with import lines returned from getLinesFromSourceCode.")

	return importLines
