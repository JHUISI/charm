import con, sys
from Value import Value

class StringValue:
	def __init__(self):
		self.value = None
		self.lineNo = None
		self.inQuotes = False
		self.groupType = None

	def getValue(self):
		return self.value

	def getType(self):
		return str

	def getLineNo(self):
		return self.lineNo

	def getGroupType(self):
		return self.groupType

	def getStringVarName(self):
		'''
		if (self.inQuotes == True):
			return "'" + str(self.value) + "'"
		else:
			return str(self.value)
		'''

		return "'" + str(self.value) + "'"

	def setValue(self, value):
		if (type(value) is not str):
			sys.exit("Value passed to StringValue class is not of type " + con.strTypePython)

		#if (len(value) == 0):
			#sys.exit("Value passed to StringValue class is of length zero.")

		self.value = value

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("StringValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("StringValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

	def setInQuotes(self, inQuotes):
		self.inQuotes = inQuotes

	def setGroupType(self, groupType):
		if ( (groupType == None) or (type(groupType).__name__ != con.stringName) or (groupType.getStringVarName() not in con.groupTypes) ):
			sys.exit("StringValue->setGroupType:  problem with groupType input parameter passed in.")

		self.groupType = groupType

Value.register(StringValue)
