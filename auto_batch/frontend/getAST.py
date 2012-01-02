import sys, ast

class AST_Visitor(ast.NodeVisitor):
	def visit_For(self, node):
		#print(type(node).__name__)
		#print(node.target.id)
		print(node._fields)

f = open(sys.argv[1], 'r').readlines()
c = ""
for l in f:
	c += l

t = ast.parse(c)
print(ast.dump(t))

u = AST_Visitor()
u.visit(t)
