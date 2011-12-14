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

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("LambdaValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("LambdaValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

	def setArgList(self, argList):
		if (argList == None):
			sys.exit("LambdaValue->setArgList:  list passed in is of None type.")

		if (len(argList) == 0):
			sys.exit("LambdaValue->setArgList:  list passed in is of zero length.")

		for arg in argList:
			if (type(arg) is not str):
				sys.exit("LambdaValue->setArgList:  one of the arguments passed in the argument list is not of string type.")

		self.argList = argList

	def setExpression(self, expression):
		if (expression == None):
			sys.exit("LambdaValue->setExpression:  expression passed in is of None type.")

		if (len(expression) == 0):
			sys.exit("LambdaValue->setExpression:  expression is of length zero.")

		self.expression = expression

Value.register(LambdaValue)
