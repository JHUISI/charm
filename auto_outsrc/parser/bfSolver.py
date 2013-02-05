from __future__ import print_function
from z3 import *
import string

# input for our BF solver
bf_count = 5
mskVars = ['alpha', 't1', 't2', 't3', 't4']
rndVars = ['r1', 'r2']

######################################################################################
# Standard code below
keygenVars = mskVars + rndVars
alphabet = string.ascii_lowercase
factors = []

for i in range(bf_count):
    factors.append(alphabet[i])
factors.append('nil') # no blinding factor
print("selected factors :", factors)

# blinding factors
Factors, factorsList = EnumSort('Factors', factors)
#a, b, c, d, e, nil = factorsList
print("factorList :", factorsList)
nil = factorsList[-1]

# target variables
varList = []
mskList = []
nonNilList = []
rndList = []
for i in keygenVars:
    j = Const(i, Factors)
    varList.append( j )
    if i in mskVars:
       mskList.append( j )
       nonNilList.append( j != nil )
    else:
       rndList.append( j )

# extract all possible mappings for mskList
orObjs = []
for i in mskList:
    varMap = []
    for j in factorsList:
        if str(j) != str(nil):
           varMap.append( i == j )
    orObjs.append( Or(varMap) )

andObjVarMap = And(orObjs)

s = Solver()
s.set(unsat_core=True)
# add vars for possible blinding factor mappings for msk
s.add(andObjVarMap)
# R1. msk must be unique
s.add( Distinct(mskList) )
# R2. none of the msk variables can be mapped to nil or no blinding factors
s.add( And(nonNilList) )

######################################################################################

#5- r1 * t1 * t2 + r2 * t3 * t4
#4- alpha * t2 + r1 * t2
#3- alpha * t1 + r2 * t1
#2- r2 * t4
#1- r2 * t3

alpha, t1, t2, t3, t4, r1, r2 = varList

p1, p2, p3, p4, p5, p6, p7 = Bools('p1 p2 p3 p4 p5 p6 p7')

# rnd can be reused, but reused consistently
# 1
s.assert_and_track( And(r2 == nil, t3 != nil), p1 )
# 2
s.assert_and_track( And(r2 == nil, t4 != nil), p2 )
# 3 : alpha * t1 + r2 * t1
# need a way to translate the expression to the following:
#s.assert_and_track( Or(And(alpha == nil, t1 != nil), And(alpha != nil, t1 == nil)), p3 )
#s.assert_and_track( Or(And(r2 == nil, t1 != nil), And(r2 != nil, t1 == nil)), p3 )
#s.assert_and_track( And(Or(alpha == r2, alpha == t1), Or(t1 == r2, t1 == t1)), p3 )

# 4 : alpha * t2 + r1 * t2
#s.assert_and_track( Or(And(alpha == nil, t2 != nil), And(alpha != nil, t2 == nil)), p4 ) 
#s.assert_and_track( Or(And(r1 == nil, t2 != nil), And(r1 != nil, t2 == nil)), p4 )
#s.assert_and_track( And(Or(alpha == r1, alpha == t2), Or(t2 == r1, t2 == t2)), p4 )

# add rule
# 5 : r1 * t1 * t2 + r2 * t3 * t4 => {'MUL0': [ 'r1', 't1', 't2' ],  'MUL1': [ 'r2', 't3', 't4' ], 'ADD0': ['MUL0', 'MUL1'], 'root':'ADD0' }
s.assert_and_track( Or(And(r1 == nil, t1 == nil, t2 != nil), And(r1 == nil, t1 != nil, t2 != nil), And(r1 != nil, t1 == nil, t2 == nil)), p5 )
s.assert_and_track( Or(And(r2 == nil, t3 == nil, t4 != nil), And(r2 == nil, t3 != nil, t4 != nil), And(r2 != nil, t3 == nil, t4 == nil)), p6 )
s.assert_and_track( And(Or(r1 == r2, r1 == t3, r1 == t4), Or(t1 == r2, t1 == t3, t1 == t4), Or(t2 == r2, t2 == t3, t2 == t4)), p7 )

print(s)
print(s.check())
if s.check() != unsat:
  print(s.model())
else:
  print(s.unsat_core())
#  print(s.check(p1, p2, p3))
