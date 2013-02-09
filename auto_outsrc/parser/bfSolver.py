from __future__ import print_function
from z3 import *
import string

# input for our BF solver
#bfCount = 5
#mskVars = ['alpha', 't1', 't2', 't3', 't4']
#rndVars = ['r1', 'r2']
#
## 4 : alpha * t2 + r1 * t2
##d4 = {'MUL0':['alpha', 't2'], 'MUL1':['r1', 't2'], 'ADD0': ['MUL0', 'MUL1'], 'root':'ADD0' }
## 5 : r1 * t1 * t2 + r2 * t3 * t4 => 
##d5 = {'MUL0': [ 'r1', 't1', 't2' ],  'MUL1': [ 'r2', 't3', 't4' ], 'ADD0': ['MUL0', 'MUL1'], 'root':'ADD0' }
#
##keywords: info, skVars, rndVars, mskVars and bfCount
#info = {'d3': {'root': ['ADD0'], 'ADD0': ['t4', '-r2', 'hID#y']}, 'sk': {}, 'd4': {'root': ['ADD0'], 'ADD0': ['t3', '-r2', 'hID#y']}, 'd2': {'root': ['ADD0'], 'ADD0': ['t1', '-alpha', 't1', '-r1', 'hID#y']}, 'id': {}, 'd0': {'ADD0': ['MUL0', 'MUL2'], 'MUL2': ['r2', 'MUL3'], 'MUL3': ['t3', 't4'], 'MUL0': ['r1', 'MUL1'], 'MUL1': ['t1', 't2'], 'root': ['ADD0']}, 'd1': {'root': ['ADD0'], 'ADD0': ['t2', '-alpha', 't2', '-r1', 'hID#y']}}
#skVars = ['d0', 'd1', 'd2', 'd3', 'd4']

bfCount = 2
mskVars = ['alpha']
rndVars = ['t', 'beta', 's'] # try to capture ordering of instances of random vars.

info = {'sk': ['K', 'L', 'Kl'], 'K': {'root': ['ADD0'], 'ADD0': ['MUL0','MUL1'], 'MUL0':['alpha', 'beta'], 'MUL1':['s', 't']}, 'L': {'root':['LEAF0'], 'LEAF0':['t']}, 'Kl': {'root':['LEAF0'], 'LEAF0':['t']}}

#rndVars = ['t', 'beta']
#info = {'sk': ['K', 'L', 'Kl'], 'K': {'root': ['ADD0'], 'ADD0': ['t','MUL0'], 'MUL0':['alpha', 'beta']}, 'L': {'root':['LEAF0'], 'LEAF0':['t']}, 'Kl': {'root':['LEAF0'], 'LEAF0':['t']}}
#info = {'sk': ['K', 'L', 'Kl'], 'K': {'root': ['ADD0'], 'ADD0': ['alpha','t']}, 'L': {'root':['LEAF0'], 'LEAF0':['t']}, 'Kl': {'root':['LEAF0'], 'LEAF0':['t']}}
skVars = 'sk'

######################################################################################
root = 'root'
def clean(v):
    removeSymbols = ['-', '#', '?']
    for i in removeSymbols:
        if v.find(i) != -1:
            v.strip(i)
    return v

# Standard code below
keygenVars = mskVars + rndVars
alphabet = string.ascii_lowercase
factors = []

for i in range(bfCount):
    factors.append(alphabet[i])
factors.append('nil') # no blinding factor
print("selected factors :", factors)

# blinding factors
Factors, factorsList = EnumSort('Factors', factors)
#a, b, c, d, e, nil = factorsList
print("factorList :", factorsList)
nil = factorsList[-1]

# target variables
theVarMap = {}
varList = []
mskList = []
nonNilList = []
rndList = []
for i in keygenVars:
    i = clean(i)
    j = Const(i, Factors)
    varList.append( j )
    theVarMap[ i ] = j
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
ADD,MUL,LEAF='ADD','MUL','LEAF'

class ConstructRule:
    def __init__(self, theVarMap):
        self.varMap = theVarMap
        self.varMapKeys = list(self.varMap.keys())
    
    def baseCase(self, dataList):
        """ returns True iff all elements in the list are in varMap which means they are attributes"""
        for i in dataList:
            if i not in self.varMapKeys:
                return False
        return True
    
    def getFirstNonAttr(self, data):
        assert type(data) == list, "invalid type to getFirstNonAttr"
        newData = []
        attrList = []
        for i in data:
            if ADD in i or MUL in i:
                newData.append(i)
            elif i in self.varMapKeys:
                attrList.append(i)
        return newData, attrList
    
    def rule(self, ruleType, data, retList=False, excludeList=[]):
        finalConstraints = []
        for i in ruleType:
            if ADD in i:
                if self.baseCase(data[i]):
                    if retList: finalConstraints += (self.__addRule(data[i], excludeList), data[i])
                    finalConstraints += self.__addRule(data[i], excludeList)
                else:
                    newRuleList, attrList = self.getFirstNonAttr(data[i])
                    print("newDataList=", newRuleList)
                    print("attrList=", attrList)
                    if len(attrList) > 0:
                        res = self.rule(newRuleList, data, True, excludeList)
#                        print("RESULT0: ", res[0])
#                        print("RESULT1: ", res[1] + attrList)
                        data[ i ] = res[1] + attrList # updating current ADD* key/value
                        excludeList += list(res[1])
                        res2 = self.rule([ i ], data, excludeList)
#                        print("RESULT2: ", res[0], res2[0])
                        finalConstraints += res[0] + res2[0]
                    else:
                        finalConstraints += self.rule(newRuleList, data, retList, excludeList)
#                    sys.exit(0)
            elif MUL in i:
                if self.baseCase(data[i]):
                    if retList: finalConstraints += (self.__mulRule(data[i], excludeList), data[i])
                    finalConstraints += self.__mulRule(data[i], excludeList)
                else:
                    print("dealing with mix modes!!!")                    
            elif LEAF in i:
                finalConstraints += self.__attrRule(data[i]) # base case
        return finalConstraints
    
    def __attrRule(self, data):
        orObjects = []
        print("ATTR Rule: ", data)
        for i in data:
            orObjects.append(self.varMap.get(i) != nil)
#            orObjects.append(self.varMap.get(i) == nil)
        print("Result:", Or(orObjects))
        return [ Or(orObjects) ]

    def __mulRule(self, data, excludeList):
        """base rule: a * b ==> Or(And(a != nil, b == nil), And(a == nil, b != nil))"""
        print("MUL Rule: ", data)
        index = 0
        orObjects = []
        for x in range(len(data)):
            objects = []
            for i,j in enumerate(data):
                jj = self.varMap.get(j)
                if index == i:
                    objects.append(jj != nil)
                    #print(j, "!= nil", end=" ")
                else:
                    objects.append(jj == nil)
                    #print(j, "== nil", end=" ")
#            print("")
            orObjects.append( And(objects) )
            index += 1
        print("MUL Result: ", Or(orObjects))
        return [ Or(orObjects) ]
    
    def __addRule(self, data, excludeList):
        """base rule: a + b ==> And(a == b), a + b + c ==> And(a == b, a == c, b == c), etc"""        
        print("ADD Rule: ", data)
        varCheck = {}
        objects = []
        for i in data:
            for j in data:
                if i in excludeList and j in excludeList: continue
                ii = self.varMap.get(i)
                jj = self.varMap.get(j)
                if i != j and (j != varCheck.get(i) and i != varCheck.get(j)):
                    varCheck[ i ] = j
                    varCheck[ j ] = i
                    objects.append(ii == jj)
                        
        print("ADD Result: ", Or(objects))
        return [ Or(objects) ]
    
# read the 'info' dict
construct = ConstructRule(theVarMap)
skList = info.get(skVars)
index = 0
for i in skList:
    print("key=", i, ", dict=", info[i])
    constraints = construct.rule(info[i][root], info[i])
    print("DEBUG: constraints=", constraints)
    for j in range(len(constraints)):
        s.assert_and_track(constraints[j], 'p' + str(index))
        index += 1
    print("\n")

# TODO: map the sk vars to constraints to assert that each group element is blinded.

#0- r1 * t1 * t2 + r2 * t3 * t4
#1- alpha * t2 + r1 * t2
#2- alpha * t1 + r2 * t1
#3- r2 * t4
#4- r2 * t3

# s2 = Solver() # copy the assertions in 's' so far and add then constraints. Note that we can return to this
# point if any of the constraints fail. We use the boolean variables from p1 -> pX to determine
# WHAT constraint failed and why. Then, we can repeat the check for a satisfiable solution w/o 
# the identified failure and mark that we have to go nuclear for that particular constraint.

#alpha, t1, t2, t3, t4, r1, r2 = varList

#p1, p2, p3, p4, p5, p6, p7 = Bools('p1 p2 p3 p4 p5 p6 p7')

# rnd can be reused, but reused consistently
# 1
#s.assert_and_track( And(r2 == nil, t3 != nil), 'p1' )
# 2
#s.assert_and_track( And(r2 == nil, t4 != nil), 'p2' )
# 3 : alpha * t1 + r2 * t1
# need a way to translate the expression to the following:
#s.assert_and_track( Or(And(alpha == nil, t1 != nil), And(alpha != nil, t1 == nil)), 'p3' )
#s.assert_and_track( Or(And(r2 == nil, t1 != nil), And(r2 != nil, t1 == nil)), 'p3' )
#s.assert_and_track( And(Or(alpha == r2, alpha == t1), Or(t1 == r2, t1 == t1)), 'p3' )

# 4 : alpha * t2 + r1 * t2
#s.assert_and_track( Or(And(alpha == nil, t2 != nil), And(alpha != nil, t2 == nil)), 'p4' ) 
#s.assert_and_track( Or(And(r1 == nil, t2 != nil), And(r1 != nil, t2 == nil)), 'p4' )
#s.assert_and_track( And(Or(alpha == r1, alpha == t2), Or(t2 == r1, t2 == t2)), 'p4' )

# add rule
# 5 : r1 * t1 * t2 + r2 * t3 * t4 => {'MUL0': [ 'r1', 't1', 't2' ],  'MUL1': [ 'r2', 't3', 't4' ], 'ADD0': ['MUL0', 'MUL1'], 'root':'ADD0' }


#s.assert_and_track( Or(And(r1 == nil, t1 == nil, t2 != nil), And(r1 == nil, t1 != nil, t2 != nil), And(r1 != nil, t1 == nil, t2 == nil)), 'p5' )
#s.assert_and_track( Or(And(r2 == nil, t3 == nil, t4 != nil), And(r2 == nil, t3 != nil, t4 != nil), And(r2 != nil, t3 == nil, t4 == nil)), 'p6' )
#s.assert_and_track( And(Or(r1 == r2, r1 == t3, r1 == t4), Or(t1 == r2, t1 == t3, t1 == t4), Or(t2 == r2, t2 == t3, t2 == t4)), 'p7' )

print(s, "\n")
print(s.check())
if s.check() != unsat:
  print(s.model())
else:
  print(s.unsat_core())
