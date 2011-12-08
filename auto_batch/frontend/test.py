import ast
from ASTParser import *

class AST_Test(ast.NodeVisitor):
	def __init__(self):
		self.my = ASTParser()

	def visit_FunctionDef(self, node):
		print(node.name)

def verify():
	if (1 == 1):
		pass

def testme(a, b):
	pass

if __name__ == '__main__':
	test = ASTParser()
	node = test.getASTNodeFromFile("new.py")
	next = AST_Test()
	next.visit(node)
