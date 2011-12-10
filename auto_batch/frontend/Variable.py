class Variable():
	def __init__(self):
		self.name = None
		self.value = None

	def getName(self):
		return self.name

	def getValue(self):
		return self.value

	def setName(self, name):
		self.name = name

	def setValue(self, value):
		self.value = value
