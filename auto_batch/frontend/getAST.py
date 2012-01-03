import sys, ast

class AST_Visitor(ast.NodeVisitor):
	def visit_Assign(self, node):
		print("!!!!!!!!!!!!!!!!\n\n\n")

	def visit_For(self, node):
		ast.NodeVisitor.generic_visit(self, node)

f = open(sys.argv[1], 'r').readlines()
c = ""
for l in f:
	c += l

t = ast.parse(c)
#print(ast.dump(t))

u = AST_Visitor()
u.visit(t)
