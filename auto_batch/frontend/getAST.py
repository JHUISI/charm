import sys, ast

class AST_Visitor(ast.NodeVisitor):
	def visit_FunctionDef(self, node):
		print(node.args.args[1].arg)

f = open(sys.argv[1], 'r').readlines()
c = ""
for l in f:
	c += l

t = ast.parse(c)
print(ast.dump(t))

#u = AST_Visitor()
#u.visit(t)
