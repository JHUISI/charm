from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import PairingGroup,G1,G2,GT,ZR,pair
import sys

group = None
H = None
debug = None
H = None
H3 = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group , H , debug 
	group= groupObj 
	debug= False 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, a, h, delta, dotA, dotB, dotC):
	z = 0

	group = groupObj

	H3 = lambda a,b: group.hash(('3', str(a), str(b)), ZR)
	H = lambda prefix,x: group.hash((str(prefix), str(x)), G1)

	__init__(group)


	dotA_loopVal = group.init(G1, 1)
	dotB_loopVal = group.init(G2, 1)
	dotC_loopVal = group.init(G2, 1)

	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]
		dotB_loopVal = dotB_loopVal * dotB[index]
		dotC_loopVal = dotC_loopVal * dotC[index]

	if (  pair( dotA_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'g' ] )==( pair( a , dotB_loopVal ) * pair( h , dotC_loopVal ) )   ):
		return
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			if startSigNum not in incorrectIndices:
				incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, a, h, delta, dotA, dotB, dotC)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, a, h, delta, dotA, dotB, dotC)
