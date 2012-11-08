from toolbox.PKSig import PKSig
from math import *
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import *
import sys

group = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group 
	group= groupObj 

def ceilog( value ) : 
	return group.init( ZR , ceil( log( value , 2 ) ) ) 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, n, S, delta, dotA, dotB, dotC, dotD, dotE):
	z = 0

	group = groupObj

	__init__(group)


	r , s= verifyArgsDict[z]['sig'][bodyKey][ 'r' ] , verifyArgsDict[z]['sig'][bodyKey][ 'i' ]
	n= ceilog( s )


	dotA_loopVal = group.init(G1, 1)
	dotB_loopVal = group.init(GT, 1)
	dotC_loopVal = group.init(GT, 1)
	dotD_loopVal = group.init(GT, 1)
	dotE_loopVal = group.init(G1, 1)



	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]
		dotB_loopVal = dotB_loopVal * dotB[index]
		dotC_loopVal = dotC_loopVal * dotC[index]
		dotD_loopVal = dotD_loopVal * dotD[index]
		dotE_loopVal = dotE_loopVal * dotE[index]


	if (  pair( dotA_loopVal , verifyArgsDict[z]['pk'][bodyKey] [ 'g2' ] )==( dotB_loopVal *( dotC_loopVal *( dotD_loopVal * pair( dotE_loopVal ,( verifyArgsDict[z]['pk'][bodyKey] [ 'w2' ] ** n *( verifyArgsDict[z]['pk'][bodyKey] [ 'z2' ] ** S * verifyArgsDict[z]['pk'][bodyKey] [ 'h2' ] ) ) ) ) ) )  ):
		pass
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			if startSigNum not in incorrectIndices:
				incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, n, S, delta, dotA, dotB, dotC, dotD, dotE)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, n, S, delta, dotA, dotB, dotC, dotD, dotE)
		return

