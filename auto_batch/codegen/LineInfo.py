import con, sys

class LineInfo:
	def __init__(self):
		self.numIndentSpaces = None
		self.numIndentTabs = None
		self.lineNo = None
		self.varNames = None

	def getNumIndentSpaces(self):
		return self.numIndentSpaces

	def getNumIndentTabs(self):
		return self.numIndentTabs

	def getLineNo(self):
		return self.lineNo

	def getVarNames(self):
		return self.varNames

	def setNumIndentSpaces(self, numIndentSpaces, numSpacesPerTab):
		if ( (numIndentSpaces == None) or (type(numIndentSpaces).__name__ != con.intTypePython) or (numIndentSpaces < 0) ):
			sys.exit("LineInfo->setNumIndentSpaces:  problem with the number of indented spaces passed in.")

		if ( (numSpacesPerTab == None) or (type(numSpacesPerTab).__name__ != con.intTypePython) or (numSpacesPerTab < 1) ):
			sys.exit("LineInfo->setNumIndentSpaces:  problem with the number of spaces per tab passed in.")

		if ( (numIndentSpaces % numSpacesPerTab) != 0):
			sys.exit("LineInfo->setNumIndentSpaces:  number of indented spaces passed in is not a multiple of the number of spaces per tab passed in.")

		self.numIndentSpaces = numIndentSpaces

		self.numIndentTabs = (int(numIndentSpaces/numSpacesPerTab))

	def setNumIndentTabs(self, numIndentTabs):
		if ( (numIndentTabs == None) or (type(numIndentTabs).__name__ != con.intTypePython) or (numIndentTabs < 0) ):
			sys.exit("LineInfo->setNumIndentTabs:  problem with number of indented tabs passed in.")

		self.numIndentTabs = numIndentTabs

	def setLineNo(self, lineNo):
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("LineInfo->setLineNo:  problem with line number passed in.")

		self.lineNo = lineNo

	def setVarNames(self, varNames):
		if ( (varNames == None) or (type(varNames).__name__ != con.listTypePython) or (len(varNames) == 0) ):
			sys.exit("LineInfo->setVarNames:  problem with variable names list passed in.")

		for varName in varNames:
			if (type(varName).__name__ != con.stringName):
				sys.exit("LineInfo->setVarNames:  one of the variable names passed in the variable names list is not of type " + con.stringName)

		self.varNames = varNames
