import con, sys
from Value import Value

class InitValue:
	def __init__(self):
		self.value = None
		self.groupType = None
		self.lineNo = None

	def getType(self):
		return con.initType

	def getValue(self):
		return self.value

	def getGroupType(self):
		return self.groupType

	def getLineNo(self):
		return self.lineNo

	def getStringVarName(self):
		if (self.groupType == None):
			return None

		stringVarName = ""
		stringVarName += con.group
		stringVarName += "."
		stringVarName += con.initType
		stringVarName += "("

		groupTypeStringVarName = self.groupType.getStringVarName()
		if ( (groupTypeStringVarName == None) or (type(groupTypeStringVarName).__name__ != con.strTypePython) or (len(groupTypeStringVarName) == 0) ):
			return None

		if (groupTypeStringVarName not in con.groupTypes):
			sys.exit("InitValue->getStringVarName:  group type string extracted from self.groupType is not one of the supported group types.")

		stringVarName += groupTypeStringVarName

		if (self.value != None):
			valueStringVarName = self.value.getStringVarName()
			if ( (valueStringVarName == None) or (type(valueStringVarName).__name__ != con.strTypePython) or (len(valueStringVarName) == 0) ):
				return None

			stringVarName += ", "
			stringVarName += valueStringVarName

		stringVarName += ")"

		return stringVarName

	def setValue(self, value):
		if (value == None):
			sys.exit("InitValue->setValue:  value passed in is of None type.")

		self.value = value

	def setGroupType(self, groupType):
		if (groupType not in con.groupTypes):
			sys.exit("InitValue->setGroupType:  value passed in is not one of the supported group types.")

		self.groupType = groupType

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("InitValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("InitValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Value.register(InitValue)
