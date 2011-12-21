import con, sys
from Value import Value

class RandomValue:
	def __init__(self):
		self.seed = None
		self.groupType = None
		self.lineNo = None

	def getType(self):
		return con.randomType

	def getSeed(self):
		return self.seed

	def getGroupType(self):
		return self.groupType

	def getLineNo(self):
		return self.lineNo

	def getStringVarName(self):
		if (self.groupType == None):
			return None

		groupTypeStringVarName = self.groupType.getStringVarName()
		if ( (groupTypeStringVarName == None) or (type(groupTypeStringVarName).__name__ != con.strTypePython) or (len(groupTypeStringVarName) == 0) ):
			return None

		if (groupTypeStringVarName not in con.groupTypes):
			sys.exit("RandomValue->getStringVarName:  group type extracted from self.groupType is not one of the supported types.")

		stringVarName = ""
		stringVarName += con.group
		stringVarName += "."
		stringVarName += con.randomType
		stringVarName += "("
		stringVarName += groupTypeStringVarName

		if (self.seed != None):
			seedStringVarName = self.seed.getStringVarName()
			if ( (seedStringVarName == None) or (type(seedStringVarname).__name__ != con.strTypePython) or (len(seedStringVarName) == 0) ):
				return None

			stringVarName += ", "
			stringVarName += seedStringVarName

		stringVarName += ")"

		return stringVarName

	def setSeed(self, seed):
		if (seed == None):
			sys.exit("RandomValue->setSeed:  value passed in is of None type.")

		self.seed = seed

	def setGroupType(self, groupType):
		groupTypeStringVarName = groupType.getStringVarName()
		if ( (groupTypeStringVarName == None) or (type(groupTypeStringVarName).__name__ != con.strTypePython) or (len(groupTypeStringVarName) == 0) ):
			sys.exit("RandomValue->setGroupType:  could not properly extract group type string variable name from group type parameter passed in.")

		if (groupTypeStringVarName not in con.groupTypes):
			sys.exit("RandomValue->setGroupType:  value passed in is not one of the supported group types.")

		self.groupType = groupType

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("RandomValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("RandomValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Value.register(RandomValue)
