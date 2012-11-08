import con, sys

class VariableDependencies:
	def __init__(self):
		self.name = None
		self.dependenciesList = None

	def getName(self):
		return self.name

	def getDependenciesList(self):
		return self.dependenciesList

	def setName(self, name):
		if ( (name == None) or (type(name).__name__ != con.stringName) ):
			sys.exit("VariableDependencies->setName:  problem with name parameter passed in.")

		nameAsString = name.getStringVarName()
		if ( (nameAsString == None) or (type(nameAsString).__name__ != con.strTypePython) or (len(nameAsString) == 0) ):
			sys.exit("VariableDependencies->setName:  problem with string representation of name parameter passed in.")

		self.name = name

	def setDependenciesList(self, listParam):
		if ( (listParam == None) or (type(listParam).__name__ != con.listTypePython) or (len(listParam) == 0) ):
			sys.exit("VariableDependencies->setDependenciesList:  problem with listParam parameter passed in.")

		for listEntry in listParam:
			if ( (listEntry == None) or (type(listEntry).__name__ != con.stringName) ):
				sys.exit("VariableDependencies->setDependenciesList:  problem with one of the entries in the listParam parameter passed in.")

			listEntryAsString = listEntry.getStringVarName()
			if ( (listEntryAsString == None) or (type(listEntryAsString).__name__ != con.strTypePython) or (len(listEntryAsString) == 0) ):
				sys.exit("VariableDependencies->setDependenciesList:  problem with string representation of one of the entries in the listParam parameter passed in.")

		self.dependenciesList = listParam
