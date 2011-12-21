import con, sys
from Value import Value

class IntegerValue:
	def __init__(self):
		self.value = None
		self.lineNo = None

	def getValue(self):
		return self.value

	def getType(self):
		return int

	def getLineNo(self):
		return self.lineNo

	def getStringVarName(self):
		return str(self.value)

	def setValue(self, value):
		if (type(value) is not int):
			sys.exit("Value passed to IntegerValue class is not of type " + con.intTypePython)

		self.value = value

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("IntegerValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("IntegerValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Value.register(IntegerValue)
