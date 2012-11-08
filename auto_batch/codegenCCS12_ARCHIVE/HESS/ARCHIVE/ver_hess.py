from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import PairingGroup,G1,G2,ZR,pair
import sys

group = None
debug = None
H1 = None
H2 = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, delta, dotA, dotB, dotC):
	z = 0

	group = groupObj

	H2 = lambda x,y: group.hash((x,y), ZR)
	H1 = lambda x: group.hash(x, G1)

	__init__(group)


	dotA_loopVal = group.init(G1, 1)
	dotB_loopVal = group.init(G1, 1)
	dotC_loopVal = group.init(GT, 1)

	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]
		dotB_loopVal = dotB_loopVal * dotB[index]
		dotC_loopVal = dotC_loopVal * dotC[index]

	if (  pair( dotA_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'g2' ] )==( pair( dotB_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'P' ] ) * dotC_loopVal )   ):
		return
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, delta, dotA, dotB, dotC)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, delta, dotA, dotB, dotC)
