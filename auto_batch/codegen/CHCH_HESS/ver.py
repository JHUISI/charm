from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
from schemes.pksig_hess import Hess
from schemes.pksig_chch import CHCH
import sys

group = None
H2 = None
debug = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global H2 , group , debug 
	group= groupObj 
	debug= False 
	H2= lambda x , y : group.hash(( x , y ) , ZR ) 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, delta, dotA, dotB, dotC):
	z = 0

	group = groupObj

	H2 = lambda x,y: group.hash((x,y), ZR)

	__init__(group)


	dotA_loopVal = group.init(G1, 1)
	dotB_loopVal = group.init(GT, 1)
	dotC_loopVal = group.init(G1, 1)

	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]
		dotB_loopVal = dotB_loopVal * dotB[index]
		dotC_loopVal = dotC_loopVal * dotC[index]

	if ( ( pair( dotA_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'P' ] ) *( dotB_loopVal * pair( dotC_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'g2' ] ) ) )== group.init(GT, 1)   ):
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
