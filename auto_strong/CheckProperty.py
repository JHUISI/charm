from __future__ import print_function
from z3 import *

I = IntSort()
e = Function('E', I, I, I)
x, y, z = Ints('x y z')

my_solver = Then(With('simplify', arith_lhs=True, som=True), 'normalize-bounds', 'solve-eqs', 'smt').solver()
my_solver.add( ForAll([x, y], e(x, y) == x*y) )
my_solver.add( ForAll([x, y, z], e(x+y, z) == (x*z + y*z)) )
my_solver.add( ForAll([x, y, z], e(x, y+z) == (y*x + z*x)) )

# x := random(ZR)
# y := random(ZR)
# X := g^x
# Y := g^y
# a := random(G2)
# m := H(M, ZR)
# b := a^y
# c := a^(x + (m * x * y))
# sig := list{a, b, c}

a, b, c, d = Ints('a b c d')
g, m = Ints('g m')
#my_solver.add( And(a == 2, b == 4, c == 6, d == 3 ) )
#my_solver.add( And(x == 3, y == 4, m == 5))
#my_solver.add( And(m == 3, ))
b = y
c = (x + (m * x * y))


print(my_solver)
my_solver.check()
M = my_solver.model()
print(M, "\n")
verify1 = M.evaluate(e(a, y) == e(g, b))
verify2 = M.evaluate(((e(x, a) * (e(x, b) * m)) == e(g, c)))
#print("Evaluate: e(a+b, c) == e(a, c+b) : ", m.evaluate(e(a+b, c) == e(a, c+b)))
##print(m.evaluate(e(a, c+1)))
#print("Evaluate: e(a, c) == e(b, d) : ", m.evaluate(e(a, c) == e(b, d)))
#print("Evaluate: (e(a, c) * e(b, c) / e(a, c) ) == e(b, c) : ", m.evaluate(((e(a, c) * e(b, c)) / e(a, c)) == e(b, c)))
#print("Evaluate: ((e(a, c) * e(b, c)) == e(b, c) * e(a, c)) : ", m.evaluate(((e(a, c) * e(b, c)) == e(b, c) * e(a, c))))

print("Evaluate: e(a, Y) == e(g, b) : ", M.evaluate(e(a, y) == e(g, b)))
#print("Evaluate: e(X, a) * e(X, b)^M == e(g, c) : ", M.evaluate(((e(x, a) * (e(x, b) * m)) )))
#print("Evaluate: e(g, c) : ", M.evaluate(e(g, c)))
print("Evaluate: e(X, a) * e(X, b)^M == e(g, c) : ", M.evaluate(((e(x, a) * (e(x, b) * m)) == e(g, c))))

#result1 = solve(verify1, verify2, m > 1, g > 1, a > 1, y > 1) #, x > 1)
print("Simpify test: ", simplify(verify2))