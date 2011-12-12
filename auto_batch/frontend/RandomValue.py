import con, sys
from Value import Value

class RandomValue:
	def __init__(self):
		self.value = None
		self.groupType = None
		self.lineNo = None

	def getValue(self):
		return self.value

	def getType(self):
		return con.randomType

	def getGroupType(self):
		return self.groupType

	def getLineNo(self):
		return self.lineNo

	def setValue(self, value):
		if (value == None):
			sys.exit("RandomValue->setValue:  value passed in is of None type.")

		self.value = value

	def setGroupType(self, groupType):
		if (groupType not in con.groupTypes):
			sys.exit("RandomValue->setGroupType:  value passed in is not one of the supported group types.")

		self.groupType = groupType

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("RandomValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("RandomValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Value.register(RandomValue)
