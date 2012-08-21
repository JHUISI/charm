import con, sys
from Name import Name

class SubscriptName:
	def __init__(self):
		self.lineNo = None
		self.value = None
		self.slice = None
		self.groupType = None

	def getValue(self):
		return self.value

	def getSlice(self):
		return self.slice

	def getType(self):
		return con.subscriptName

	def getLineNo(self):
		return self.lineNo

	def getGroupType(self):
		return self.groupType

	def getStringVarName(self):
		if ( (self.value == None) or (self.slice == None) ):
			return None

		valueStringVarName = self.value.getStringVarName()
		if ( (valueStringVarName == None) or (type(valueStringVarName).__name__ != con.strTypePython) or (len(valueStringVarName) == 0) ):
			return None

		sliceStringVarName = self.slice.getStringVarName()
		if ( (sliceStringVarName == None) or (type(sliceStringVarName).__name__ != con.strTypePython) or (len(sliceStringVarName) == 0) ):
			return None

		return valueStringVarName + "[" + sliceStringVarName + "]"

	def equals(self, otherSubscriptNameObject):
		if ( (otherSubscriptNameObject == None) or (type(otherSubscriptNameObject).__name__ != con.subscriptName) ):
			sys.exit("SubscriptName->equals:  problem with input parameter passed in.")

		if ( self.getStringVarName() == otherSubscriptNameObject.getStringVarName() ):
			return True

		return False

	def setValue(self, value):
		if (value == None):
			sys.exit("SubscriptName->setValue:  value passed in is of None type.")

		#if ( (type(value).__name__ != con.stringName) and (type(value).__name__ != con.callValue) ):
			#sys.exit("SubscriptName->setValue:  value passed in is not of type " + con.stringName + " or type " + con.callValue + ".")

		self.value = value

	def setSlice(self, slice):
		if ( (slice == None) or (type(slice).__name__ != con.sliceValue) ):
			sys.exit("SubscriptName->setSlice:  problem with slice parameter passed in.")

		self.slice = slice

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("SubscriptName->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("SubscriptName->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

	def setGroupType(self, groupType):
		if ( (groupType == None) or (type(groupType).__name__ != con.stringName) or (groupType.getStringVarName() not in con.groupTypes) ):
			sys.exit("SubscriptName->setGroupType:  problem with groupType input parameter.")

		self.groupType = groupType

Name.register(SubscriptName)
