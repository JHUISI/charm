import con, sys

class PrecomputeVariable:
	def __init__(self):
		self.varName = None
		self.expression = None
		self.codeGenSegmentNo = None

	def getVarName(self):
		return self.varName

	def getExpression(self):
		return self.expression

	def getCodeGenSegmentNo(self):
		return self.codeGenSegmentNo

	def setVarName(self, varName):
		if ( (varName == None) or (type(varName).__name__ != con.stringName) ):
			sys.exit("PrecomputeVariable->setVarName:  problem with variable name parameter passed in.")

		varNameAsString = varName.getStringVarName()
		if ( (varNameAsString == None) or (type(varNameAsString).__name__ != con.strTypePython) or (len(varNameAsString) == 0) ):
			sys.exit("PrecomputeVariable->setVarName:  problem with string obtained by calling getStringVarName on variable name object passed in.")

		self.varName = varName

	def setExpression(self, expression):
		if ( (expression == None) or (type(expression).__name__ != con.strTypePython) or (len(expression) == 0) ):
			sys.exit("PrecomputeVariable->setExpression:  problem with expression parameter passed in.")

		self.expression = expression

	def setCodeGenSegmentNo(self, codeGenSegmentNo):
		self.codeGenSegmentNo = codeGenSegmentNo
