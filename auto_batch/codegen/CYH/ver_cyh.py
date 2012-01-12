from toolbox.pairinggroup import PairingGroup,G1,G2,GT,ZR,pair
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, random, string
import sys

group = None
debug = None
H1 = None
H2 = None
lam_func = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def concat( L_id ) : 
	result= "" 
	for i in L_id : 
		pass
		result += ":" + i 
	return result 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, delta, dotC, dotB):
	z = 0

	group = groupObj

	l= len( verifyArgsDict[z]['L'][bodyKey] )
	lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i]) # => u * (pk ** h) for all signers
	H1 = lambda x: group.hash(('1', str(x)), G1)
	H2 = lambda a, b, c: group.hash(('2', a, b, c), ZR)

	__init__(group)


	dotC_loopVal = group.init(G1, 1)
	dotB_loopVal = group.init(G1, 1)

	for index in range(startSigNum, endSigNum):
		dotC_loopVal = dotC_loopVal * dotC[index]
		dotB_loopVal = dotB_loopVal * dotB[index]

	if (  pair( dotB_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'Pub' ] )== pair( dotC_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'g' ] )   ):
		return
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, delta, dotC, dotB)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, delta, dotC, dotB)
