import con, sys
from Value import Value

class SliceValue:
	def __init__(self):
		self.sliceType = None
		self.value = None
		self.lower = None
		self.upper = None
		self.step = None
		self.lineNo = None
		self.groupType = None

	def getSliceType(self):
		return self.sliceType

	def getValue(self):
		return self.value

	def getType(self):
		return con.sliceValue

	def getLower(self):
		return self.lower

	def getUpper(self):
		return self.upper

	def getStep(self):
		return self.step

	def getLineNo(self):
		return self.lineNo

	def getGroupType(self):
		return self.groupType

	def getStringVarName(self):
		if (self.sliceType == None):
			return None

		if (type(self.sliceType).__name__ != con.stringName):
			sys.exit("SliceValue->getStringVarName:  self.sliceType is not of type " + con.stringName + ".")

		sliceTypeAsString = self.sliceType.getStringVarName()
		if ( (sliceTypeAsString == None) or (type(sliceTypeAsString).__name__ != con.strTypePython) or (sliceTypeAsString not in con.sliceTypes) ):
			sys.exit("SliceValue->getStringVarName:  problem with self.sliceType.getStringVarName().")

		retString = ""

		if (sliceTypeAsString == con.sliceType_Value):
			if (self.value == None):
				sys.exit("SliceValue->getStringVarName:  self.value is set to None, but it shouldn't be because self.sliceType is set to value.")

			retString = self.value.getStringVarName()
			if (retString == None):
				return None
			if ( (type(retString).__name__ != con.strTypePython) or (len(retString) == 0) ):
				sys.exit("SliceValue->getStringVarName:  problem with value returned from getStringVarName() called on self.value.")
			return retString
		if (sliceTypeAsString == con.sliceType_LowerUpperStep):
			if ( (self.lower == None) and (self.upper == None) and (self.step == None) ):
				sys.exit("SliceValue->getStringVarName:  self.lower, self.upper, and self.step are all set to None, but at least one should not be set to None because self.sliceType is set to lower/upper/step.")

			if (self.lower != None):
				lowerString = self.lower.getStringVarName()
				if ( (lowerString == None) or (type(lowerString).__name__ != con.strTypePython) or (len(lowerString) == 0) ):
					sys.exit("SliceValue->getStringVarName:  problem with self.lower.getStringVarName()")

				retString += lowerString

			if (self.upper != None):
				upperString = self.upper.getStringVarName()
				if ( (upperString == None) or (type(upperString).__name__ != con.strTypePython) or (len(upperString) == 0) ):
					sys.exit("SliceValue->getStringVarName:  problem with self.upper.getStringVarName().")

				retString += ":" + upperString

			if (self.step != None):
				stepString = self.step.getStringVarName()
				if ( (stepString == None) or (type(stepString).__name__ != con.strTypePython) or (len(stepString) == 0) ):
					sys.exit("SliceValue->getStringVarName:  problem with self.step.getStringVarName().")

				retString += ":" + stepString

			return retString

		sys.exit("SliceValue->getStringVarName:  current type of self.sliceType is not supported.")

	def setSliceType(self, sliceType):
		if ( (sliceType == None) or (type(sliceType).__name__ != con.stringName) ):
			sys.exit("SliceValue->setSliceType:  problem with slice type parameter passed in.")

		sliceTypeAsString = sliceType.getStringVarName()
		if ( (sliceTypeAsString == None) or (type(sliceTypeAsString).__name__ != con.strTypePython) or (sliceTypeAsString not in con.sliceTypes) ):
			sys.exit("SliceValue->setSliceType:  problem with string representation of slice type passed in.")

		self.sliceType = sliceType

	def setValue(self, value):
		if (value == None):
			sys.exit("SliceValue->setValue:  value node passed in is of None type.")

		self.value = value

	def setLower(self, lower):
		if (lower == None):
			sys.exit("SliceValue->setLower:  lower node passed in is of None type.")

		self.lower = lower

	def setUpper(self, upper):
		if (upper == None):
			sys.exit("SliceValue->setUpper:  upper node passed in is of None type.")

		self.upper = upper

	def setStep(self, step):
		if (step == None):
			sys.exit("SliceValue->setStep:  step node passed in is of None type.")

		self.step = step

	def setLineNo(self, lineNo):
		if ( (lineNo == None) or (type(lineNo).__name__ != con.intTypePython) or (lineNo < 1) ):
			sys.exit("SliceValue->setLineNo:  problem with line number parameter passed in.")

		self.lineNo = lineNo

	def setGroupType(self, groupType):
		if ( (groupType == None) or (type(groupType).__name__ != con.stringName) or (groupType.getStringVarName() not in con.groupTypes) ):
			sys.exit("SliceValue->setGroupType:  problem with groupType parameter passed in.")

		self.groupType = groupType

Value.register(SliceValue)
