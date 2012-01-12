import con, sys
from Value import Value

class VariableNamesValue:
	def __init__(self):
		self.varNamesList = None
		self.lineNo = None

	def getVarNamesList(self):
		return self.varNamesList

	def getType(self):
		return con.variableNamesValue

	def getLineNo(self):
		return self.lineNo

	def getStringVarName(self):
		if (self.varNamesList == None):
			return None

		retString = ""

		for varName in self.varNamesList:
			if ( (varName == None) or (type(varName).__name__ != con.stringName) ):
				sys.exit("VariableNamesValue->getStringVarName:  problem with one of the StringName values in self.varNamesList.")

			varNameAsString = varName.getStringVarName()
			if ( (varNameAsString == None) or (type(varNameAsString).__name__ != con.strTypePython) or (len(varNameAsString) == 0) ):
				sys.exit("VariableNamesValue->getStringVarName:  problem with string representation of one of the variable names in self.varNamesList.")

			retString += varNameAsString + ", "

		lenRetString = len(retString)
		retString = retString[0:(lenRetString - 2)]
		return retString

	def setVarNamesList(self, varNamesList):
		if ( (varNamesList == None) or (type(varNamesList).__name__ != con.listTypePython) or (len(varNamesList) == 0) ):
			sys.exit("VariableNamesValue->setVarNamesList:  problem with variable names list parameter passed in.")

		for varName in varNamesList:
			if ( (varName == None) or (type(varName).__name__ != con.stringName) ):
				sys.exit("VariableNamesValue->setVarNamesList:  problem with one of the variable names in the variable name list passed in.")

		self.varNamesList = varNamesList

	def setLineNo(self, lineNo):
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("VariableNamesValue->setLineNo:  problem with line number passed in.")

		self.lineNo = lineNo

Value.register(VariableNamesValue)
