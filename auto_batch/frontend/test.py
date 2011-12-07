import ast
from ASTParser import *

class AST_Test(ast.NodeVisitor):
	def __init__(self):
		self.my = ASTParser()

	def visit_Assign(self, node):
		left = self.my.getAssignRightSideNode(node)
		#print(ast.dump(left))
		isIt = self.my.getTupleNodes(left)
		print(isIt)

test = ASTParser()
node = test.getASTNodeFromFile("new.py")
next = AST_Test()
next.visit(node)
