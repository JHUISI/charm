import sys, ast

class AST_Visitor(ast.NodeVisitor):
	#def generic_visit(self, node):
		#print(ast.dump(node))
		#ast.NodeVisitor.generic_visit(self, node)

	#def visit_UnaryOp(self, node):
		#print(type(node.op).__name__)

	def visit_Subscript(self, node):
		print(node.slice._fields)

f = open(sys.argv[1], 'r').readlines()
c = ""
for l in f:
	c += l

t = ast.parse(c)
print(ast.dump(t))

u = AST_Visitor()
#u.visit(t)
