from abc import ABCMeta, abstractmethod

class Name(metaclass=ABCMeta):
	@abstractmethod
	def getType(self):
		return

	@abstractmethod
	def getLineNo(self):
		return

	@abstractmethod
	def setLineNo(self, lineNo):
		return
