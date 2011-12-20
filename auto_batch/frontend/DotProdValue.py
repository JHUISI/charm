import con, sys
from Value import Value

class DotProdValue:
	def __init__(self):
		self.initialValue = None
		self.skipValue = None
		self.numProds = None
		self.funcName = None
		self.argList = None
		self.lineNo = None

	def getInitialValue(self):
		return self.initialValue

	def getSkipValue(self):
		return self.skipValue

	def getNumProds(self):
		return self.numProds

	def getFuncName(self):
		return self.funcName

	def getArgList(self):
		return self.argList

	def getType(self):
		return con.dotProdType

	def getLineNo(self):
		return self.lineNo

	def setInitialValue(self, initialValue):
		if (initialValue == None):
			sys.exit("DotProdValue->setInitialValue:  initial value passed in is of None type.")

		self.initialValue = initialValue

	def setSkipValue(self, skipValue):
		if (skipValue == None):
			sys.exit("DotProdValue->setSkipValue:  skip value passed in is of None type.")

		self.skipValue = skipValue

	def setNumProds(self, numProds):
		if (numProds == None):
			sys.exit("DotProdValue->setNumProds:  number of products passed in is of None type.")

		self.numProds = numProds

	def setFuncName(self, funcName):
		if (funcName == None):
			sys.exit("DotProdValue->setFuncName:  function name passed in is of None type.")

		self.funcName = funcName

	def setArgList(self, argList):
		if ( (argList == None) or (type(argList) is not list) or (len(argList) == 0) ):
			sys.exit("DotProdValue->setArgList:  problem with arguments list passed in.")

		self.argList = argList

	def setLineNo(self, lineNo):
		if (type(lineNo) is not int):
			sys.exit("DotProdValue->setLineNo:  line number passed in is not of type " + con.intTypePython)

		if (lineNo < 1):
			sys.exit("DotProdValue->setLineNo:  line number passed in is less than one.")

		self.lineNo = lineNo

Value.register(DotProdValue)
