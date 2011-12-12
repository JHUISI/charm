import con, sys
from Value import Value

class LambdaValue:
	def __init__(self):
		self.lineNo = None

	def getType(self):
		return con.lambdaType

	def getLineNo(self):
		return self.lineNo

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("LambdaValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("LambdaValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Value.register(LambdaValue)
