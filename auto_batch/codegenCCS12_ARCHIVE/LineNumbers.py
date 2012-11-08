import con, sys

class LineNumbers:
	def __init__(self):
		self.varName = None
		self.lineNosList = None

	def getVarName(self):
		return self.varName

	def getLineNosList(self):
		return self.lineNosList

	def setVarName(self, varName):
		if (varName == None):
			sys.exit("LineNumbers->setVarName:  variable name passed in is of None type.")

		if ( (type(varName).__name__ != con.stringName) and (type(varName).__name__ != con.subscriptName) ):
			sys.exit("LineNumbers->setVarName:  problem with type of variable name parameter passed in.")

		varNameAsString = varName.getStringVarName()
		if ( (varNameAsString == None) or (type(varNameAsString).__name__ != con.strTypePython) or (len(varNameAsString) == 0) ):
			sys.exit("LineNumbers->setVarName:  problem with string representation of variable name parameter passed in.")

		self.varName = varName

	def setLineNosList(self, lineNosList):
		if ( (lineNosList == None) or (type(lineNosList).__name__ != con.listTypePython) or (len(lineNosList) == 0) ):
			sys.exit("LineNumbers->setLineNosList:  problem with line numbers list parameter passed in.")

		for lineNoAsInt in lineNosList:
			if ( (lineNoAsInt == None) or (type(lineNoAsInt).__name__ != con.intTypePython) or (lineNoAsInt < 1) ):
				sys.exit("LineNumbers->setLineNosList:  problem with one of the list members of the line numbers list parameter passed in.")

		self.lineNosList = lineNosList
