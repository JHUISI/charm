import con, sys
from Name import Name

class StringName:
	def __init__(self):
		self.name = None
		self.lineNo = None
		self.defaultValue = None

	def getName(self):
		return self.name

	def getType(self):
		return con.stringName

	def getLineNo(self):
		return self.lineNo

	def getDefaultValue(self):
		return self.defaultValue

	def getStringVarName(self):
		if (self.name == None):
			return None

		return str(self.name)

	def equals(self, otherStringNameObject):
		if ( (otherStringNameObject == None) or (type(otherStringNameObject).__name__ != con.stringName) ):
			sys.exit("StringName->equals:  problem with input parameter passed in.")

		if ( self.getStringVarName() == otherStringNameObject.getStringVarName() ):
			return True

		return False

	def setName(self, name):
		if (type(name) is not str):
			sys.exit("Name passed to StringName class is not of type " + con.strTypePython)

		if (len(name) == 0):
			sys.exit("Name passed to StringName class is of length zero.")

		self.name = name

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("StringName->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("StringName->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

	def setDefaultValue(self, defaultValue):
		if (defaultValue == None):
			sys.exit("StringName->setDefaultValue:  default value passed in is of None type.")

		self.defaultValue = defaultValue

Name.register(StringName)
