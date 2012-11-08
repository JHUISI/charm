import con, sys
from Value import Value

class DictValue:
	def __init__(self):
		self.keys = None
		self.values = None
		self.lineNo = None

	def getKeys(self):
		return self.keys

	def getValues(self):
		return self.values

	def getType(self):
		return con.dictTypePython

	def getLineNo(self):
		return self.lineNo

	def getStringVarName(self):
		if ( (self.keys == None) or (self.values == None) ):
			return None

		keysStringNameList = []
		valuesStringNameList = []

		for key in self.keys:
			keyStringName = key.getStringVarName()
			if ( (keyStringName == None) or (type(keyStringName).__name__ != con.strTypePython) or (len(keyStringName) == 0) ):
				return None

			keysStringNameList.append(keyStringName)

		for value in self.values:
			valueStringName = value.getStringVarName()
			if ( (valueStringName == None) or (type(valueStringName).__name__ != con.strTypePython) or (len(valueStringName) == 0) ):
				return None

			valuesStringNameList.append(valueStringName)

		if ( len(keysStringNameList) != len(valuesStringNameList) ):
			sys.exit("DictValue->getStringVarName:  lists of string names for keys and values are of unequal size.")

		dictStringVarName = "{"
		lenDict = len(keysStringNameList)

		for index in range(0, lenDict):
			dictStringVarName += keysStringNameList[index] + ":" + valuesStringNameList[index] + ", "

		dictStringVarName = dictStringVarName[0:(len(dictStringVarName) - 2)]
		dictStringVarName += "}"

		return dictStringVarName

	def getListOfKeyNames(self):
		if (self.keys == None):
			return None

		retList = []

		for key in self.keys:
			retList.append(key.getStringVarName())

		return retList

	def setKeys(self, keys):
		if ( (keys == None) or (type(keys).__name__ != con.listTypePython) ):
			sys.exit("DictValue->setKeys:  problem with input passed in to the function.")

		self.keys = keys

	def setValues(self, values):
		if ( (values == None) or (type(values).__name__ != con.listTypePython) ):
			sys.exit("DictValue->setValues:  problem with input passed in to the function.")

		self.values = values

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("DictValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("DictValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Value.register(DictValue)
