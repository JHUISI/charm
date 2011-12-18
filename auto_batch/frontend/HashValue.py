import con, sys
from Value import Value

class HashValue:
	def __init__(self):
		self.argList = None
		self.groupType = None
		self.lineNo = None

	def getArgList(self):
		return self.argList

	def getEntryAtIndex(self, index):
		if (type(index) is not int):
			sys.exit("HashValue->getEntryAtIndex:  index passed in is not of type int.")

		if (index < 0):
			sys.exit("HashValue->getEntryAtIndex:  index passed in is less than zero.")

		if ( index >= len(self.argList) ):
			sys.exit("HashValue->getEntryAtIndex:  index passed in is greater than or equal to the length of the argument list.")

		return self.argList[index]

	def getGroupType(self):
		return self.groupType

	def getType(self):
		return con.hashType

	def getLineNo(self):
		return self.lineNo

	def setArgList(self, argList):
		if (type(argList) is not list):
			sys.exit("HashValue->setArgList:  value passed in is not of type list.")

		if (len(argList) == 0):
			self.argList = None
		else:
			self.argList = argList

	def appendEntryToArgList(self, entry):
		if (entry == None):
			sys.exit("HashValue->addEntryToArgList:  entry passed in is of None type.")

		self.argList.append(entry)

	def prependEntryToArgList(self, entry):
		if (entry == None):
			sys.exit("HashValue->prependEntryToArgList:  entry passed in is of None type.")

		self.argList.insert(0, entry)

	def insertEntryAtIndex(self, index, entry):
		if (entry == None):
			sys.exit("HashValue->insertEntryAtIndex:  entry passed in is of None type.")

		if (type(index) is not int):
			sys.exit("HashValue->insertEntryAtIndex:  index passed in is not of type int.")

		if (index < 0):
			sys.exit("HashValue->insertEntryAtIndex:  index passed in is less than zero.")

		if ( index >= len(self.argList) ):
			sys.exit("HashValue->insertEntryAtIndex:  index passed in is greater than or equal to the length of the arguments list.")

		self.argList.insert(index, entry)

	def removeEntryWithValue(self, value):
		if (value == None):
			sys.exit("HashValue->removeEntryWithValue:  value passed in is of None type.")

		try:
			self.argList.remove(value)
		except:
			sys.exit("HashValue->removeEntryWithValue:  value passed in does not exist in the arguments list.")

	def findEntryWithValue(self, value):
		if (value == None):
			sys.exit("HashValue->findEntryWithValue:  value passed in is of None type.")

		index = None

		try:
			index = self.argList.index(value)
		except:
			return None

		return index

	def setGroupType(self, groupType):
		if (groupType not in con.groupTypes):
			sys.exit("HashValue->setGroupType:  group type passed in is not one of the supported group types.")

		self.groupType = groupType

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("HashValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("HashValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Value.register(HashValue)
