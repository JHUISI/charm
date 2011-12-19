import con, sys
from Name import Name

class SubscriptName:
	def __init__(self):
		self.lineNo = None
		self.value = None
		self.slice = None

	def getValue(self):
		return self.value

	def getSlice(self):
		return self.slice

	def getType(self):
		return con.subscriptTypeAST

	def getLineNo(self):
		return self.lineNo

	def getStringVarName(self):
		return str(self.value.getStringVarName()) + "[" + str(self.slice.getStringVarName()) + "]"

	def setValue(self, value):
		if (value == None):
			sys.exit("SubscriptName->setValue:  value passed in is of None type.")

		if (type(value).__name__ != con.stringName):
			sys.exit("SubscriptName->setValue:  value passed in is not of type " + con.stringName)

		self.value = value

	def setSlice(self, slice):
		if (slice == None):
			sys.exit("SubscriptName->setSlice:  slice passed in is of None type.")

		#sliceType = type(slice).__name__

		#if ( (sliceType != con.stringName) and (sliceType != con.stringValue) and (sliceType != con.integerValue) and (sliceType != con.floatValue) ):
			#sys.exit("SubscriptName->setSlice:  slice passed in is not one of the supported types (" + con.stringName + ", " + con.stringValue + ", " + con.integerValue + ", or " + con.floatValue + ").")

		self.slice = slice

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("SubscriptName->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("SubscriptName->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Name.register(SubscriptName)
