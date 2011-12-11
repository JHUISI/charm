import ast
from ASTParser import *

class AST_Test(ast.NodeVisitor):
	def __init__(self):
		self.my = ASTParser()

	def visit_Assign(self, node):
		print(node.value.func.value.id)
		print(node.value.func.attr)

def verify():
	x = 4
	y = 4.5
	t = "strings and strings"
	if (1 == 1):
		pass

if __name__ == '__main__':
	test = ASTParser()
	node = test.getASTNodeFromFile("new.py")
	next = AST_Test()
	next.visit(node)
