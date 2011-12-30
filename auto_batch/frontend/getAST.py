import sys, ast

class AST_Visitor(ast.NodeVisitor):
	#def generic_visit(self, node):
		#print(ast.dump(node))
		#ast.NodeVisitor.generic_visit(self, node)

	def visit_Call(self, node):
		print(node.args[1]._fields)

f = open(sys.argv[1], 'r').readlines()
c = ""
for l in f:
	c += l

t = ast.parse(c)
#print(ast.dump(t))

u = AST_Visitor()
u.visit(t)
