import con, sys
from Value import Value

class LambdaValue:
	def __init__(self):
		self.lineNo = None
		self.argList = None
		self.expression = None

	def getType(self):
		return con.lambdaType

	def getLineNo(self):
		return self.lineNo

	def getArgList(self):
		return self.argList

	def getExpression(self):
		return self.expression

	def getStringVarName(self):
		if ( (self.argList == None) or (self.expression == None) ):
			return None

		stringVarName = ""
		stringVarName += con.lambdaTypeCharm
		stringVarName += " "

		for arg in self.argList:
			if ( (arg == None) or (type(arg).__name__ != con.stringName) ):
				sys.exit("LambdaValue->getStringVarName:  problem with one of the arguments in self.argList.")

			argStringVarName = arg.getStringVarName()
			if ( (argStringVarName == None) or (type(argStringVarName).__name__ != con.strTypePython) or (len(argStringVarName) == 0) ):
				return None

			stringVarName += argStringVarName
			stringVarName += ", "

		stringVarName = stringVarName[0:(len(stringVarName) - 2)]
		stringVarName += ": "

		if (type(self.expression).__name__ != con.stringValue):
			sys.exit("LambdaValue->getStringVarName:  self.expression is not of type " + con.stringValue)

		expressionStringVarName = self.expression.getStringVarName()
		if ( (expressionStringVarName == None) or (type(expressionStringVarName).__name__ != con.strTypePython) or (len(expressionStringVarName) == 0) ):
			return None

		stringVarName += expressionStringVarName

		return stringVarName

	def setArgList(self, argList):
		if (argList == None):
			sys.exit("LambdaValue->setArgList:  list passed in is of None type.")

		if (len(argList) == 0):
			sys.exit("LambdaValue->setArgList:  list passed in is of zero length.")

		for arg in argList:
			if ( (arg == None) or (type(arg).__name__ != con.stringName) ):
				sys.exit("LambdaValue->setArgList:  problem with one of the arguments passed in the argument list.")

		self.argList = copy.deepcopy(argList)

	def setExpression(self, expression):
		if (expression == None):
			sys.exit("LambdaValue->setExpression:  expression passed in is of None type.")

		if (type(expression).__name__ != con.stringValue):
			sys.exit("LambdaValue->setExpression:  expression passed in is not of type " + con.stringValue)

		self.expression = copy.deepcopy(expression)

	def setLineNo(self, lineNo):
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("LambdaValue->setLineNo:  problem with the line number passed in.")

		self.lineNo = lineNo

Value.register(LambdaValue)
