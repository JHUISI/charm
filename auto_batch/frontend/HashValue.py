import con, sys
from Value import Value

class HashValue:
	def __init__(self):
		self.argsList = None
		self.groupType = None

	def getArgsList(self):
		return self.argsList

	def getEntryAtIndex(self, index):
		if (type(index) is not int):
			sys.exit("HashValue->getEntryAtIndex:  index passed in is not of type int.")

		if (index < 0):
			sys.exit("HashValue->getEntryAtIndex:  index passed in is less than zero.")

		if ( index >= len(self.argsList) ):
			sys.exit("HashValue->getEntryAtIndex:  index passed in is greater than or equal to the length of the argument list.")

		return self.argsList[index]

	def getGroupType(self):
		return self.groupType

	def getType(self):
		return con.hashType

	def setArgsList(self, argsList):
		if (type(argsList) is not list):
			sys.exit("HashValue->setArgsList:  value passed in is not of type list.")

		if (len(argsList) == 0):
			self.argsList = None
		else:
			self.argsList = argsList

	def appendEntryToArgsList(self, entry):
		if (entry == None):
			sys.exit("HashValue->addEntryToArgsList:  entry passed in is of None type.")

		self.argsList.append(entry)

	def prependEntryToArgsList(self, entry):
		if (entry == None):
			sys.exit("HashValue->prependEntryToArgsList:  entry passed in is of None type.")

		self.argsList.insert(0, entry)

	def insertEntryAtIndex(self, index, entry):
		if (entry == None):
			sys.exit("HashValue->insertEntryAtIndex:  entry passed in is of None type.")

		if (type(index) is not int):
			sys.exit("HashValue->insertEntryAtIndex:  index passed in is not of type int.")

		if (index < 0):
			sys.exit("HashValue->insertEntryAtIndex:  index passed in is less than zero.")

		if ( index >= len(self.argsList) ):
			sys.exit("HashValue->insertEntryAtIndex:  index passed in is greater than or equal to the length of the arguments list.")

		self.argsList.insert(index, entry)

	def removeEntryWithValue(self, value):
		if (value == None):
			sys.exit("HashValue->removeEntryWithValue:  value passed in is of None type.")

		try:
			self.argsList.remove(value)
		except:
			sys.exit("HashValue->removeEntryWithValue:  value passed in does not exist in the arguments list.")

	def findEntryWithValue(self, value):
		if (value == None):
			sys.exit("HashValue->findEntryWithValue:  value passed in is of None type.")

		index = None

		try:
			index = self.argsList.index(value)
		except:
			return None

		return index

	def setGroupType(self, groupType):
		if (groupType not in con.groupTypes):
			sys.exit("HashValue->setGroupType:  group type passed in is not one of the supported group types.")

		self.groupType = groupType

Value.register(HashValue)
