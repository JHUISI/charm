from abc import ABCMeta, abstractmethod

class Name(metaclass=ABCMeta):
	@abstractmethod
	def getType(self):
		return
