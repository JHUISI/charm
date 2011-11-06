import sys, ast

class AST_Visitor(ast.NodeVisitor):
	def visit_Assign(self, node):
		if (type(node.value).__name__ == "Dict"):
			print(node.value.keys[1]._fields)
		#print("\n")

	'''
	def visit_Target(self, node):
		print(ast.dump(node))
	'''

f = open(sys.argv[1], 'r').readlines()
c = ""
for l in f:
	c += l

t = ast.parse(c)
#print(ast.dump(t))

u = AST_Visitor()
u.visit(t)
