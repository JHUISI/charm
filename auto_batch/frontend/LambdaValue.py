import con, sys
from Value import Value

class LambdaValue:
	def __init__(self):

	def getType(self):
		return con.lambdaType

Value.register(LambdaValue)
