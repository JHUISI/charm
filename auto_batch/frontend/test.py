import ast
from ASTParser import *

class AST_Test(ast.NodeVisitor):
	def __init__(self):
		self.my = ASTParser()

	def visit_Call(self, node):
		print(node.args)

def verify():
	x = group.hash("M", str(x), G1)
	if (x == 1):
		pass

def main():
	test = ASTParser()
	node = test.getASTNodeFromFile("new.py")
	next = AST_Test()
	next.visit(node)
	N = 4

if __name__ == '__main__':
	main()
