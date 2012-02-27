from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from charm.engine.util import *
import sys, random, string
#from toolbox.IBEnc import *
import sys

group = None
util = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	#IBEnc.__init__( self ) 
	global group , util 
	group= groupObj 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, A, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG, dotH, sumI):
	z = 0

	group = groupObj

	__init__(group)




	dotA_loopVal = group.init(G2, 1)
	dotB_loopVal = group.init(G2, 1)
	dotC_loopVal = group.init(G2, 1)
	dotD_loopVal = group.init(G2, 1)
	dotE_loopVal = group.init(G2, 1)
	dotF_loopVal = group.init(GT, 1)
	dotG_loopVal = group.init(GT, 1)
	dotH_loopVal = group.init(G2, 1)
	sumI_loopVal = group.init(ZR, 0)



	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]
		dotB_loopVal = dotB_loopVal * dotB[index]
		dotC_loopVal = dotC_loopVal * dotC[index]
		dotD_loopVal = dotD_loopVal * dotD[index]
		dotE_loopVal = dotE_loopVal * dotE[index]
		dotF_loopVal = dotF_loopVal * dotF[index]
		dotG_loopVal = dotG_loopVal * dotG[index]
		dotH_loopVal = dotH_loopVal * dotH[index]
		sumI_loopVal = sumI_loopVal + sumI[index]


	if ( ( pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g1^b' ] , dotA_loopVal ) *( pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g^ba1' ] , dotB_loopVal ) *( pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g^a1' ] , dotC_loopVal ) *( pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g^ba2' ] , dotD_loopVal ) * pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g^a2' ] , dotE_loopVal ) ) ) ) )== (  dotF_loopVal * dotG_loopVal ) * ( pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g1' ] , dotH_loopVal ) * A ** sumI_loopVal )  ):
		pass
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			if startSigNum not in incorrectIndices:
				incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, A, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG, dotH, sumI)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, A, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG, dotH, sumI)
		return

