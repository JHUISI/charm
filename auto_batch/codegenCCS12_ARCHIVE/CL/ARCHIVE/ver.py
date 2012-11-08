from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import *
import sys

group = None
debug = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, delta, dotA, dotB, dotC):
	z = 0

	group = groupObj


	__init__(group)


	dotA_loopVal = group.init(G2, 1)
	dotB_loopVal = group.init(G2, 1)
	dotC_loopVal = group.init(G2, 1)

	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]
		dotB_loopVal = dotB_loopVal * dotB[index]
		dotC_loopVal = dotC_loopVal * dotC[index]

	if ( ( pair( verifyArgsDict[z]['pk'][bodyKey] [ 'Y' ] , dotA_loopVal ) * pair( verifyArgsDict[z]['pk'][bodyKey] [ 'g' ] , dotB_loopVal ) )== pair( verifyArgsDict[z]['pk'][bodyKey] [ 'X' ] , dotC_loopVal )   ):
		return
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			if startSigNum not in incorrectIndices:
				incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, delta, dotA, dotB, dotC)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, delta, dotA, dotB, dotC)
