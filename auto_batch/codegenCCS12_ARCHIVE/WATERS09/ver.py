#NB:  I had to change the imports shown below from the original files that we used for the AutoBatch
#paper.  This is because the Charm namespace has changed.  However, this should not affectt the
#behavior of this file at all.

from charm.toolbox.pairinggroup import *
from charm.toolbox.IBEnc import *
from charm.toolbox.PKSig import PKSig
from charm.toolbox.iterate import dotprod
from charm.core.engine.util import *
import sys, random, string
import sys

group = None
util = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	#IBEnc.__init__(self) 
	global group , util 
	group= groupObj 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, A, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG, dotH, dotI, dotJ, dotK, dotL, dotM, sumN):
	z = 0

	group = groupObj

	__init__(group)




	dotA_loopVal = group.init(G2, 1)
	dotB_loopVal = group.init(G2, 1)
	dotC_loopVal = group.init(G2, 1)
	dotD_loopVal = group.init(G2, 1)
	dotE_loopVal = group.init(G2, 1)
	dotF_loopVal = group.init(G1, 1)
	dotG_loopVal = group.init(G1, 1)
	dotH_loopVal = group.init(G1, 1)
	dotI_loopVal = group.init(G1, 1)
	dotJ_loopVal = group.init(G1, 1)
	dotK_loopVal = group.init(G1, 1)
	dotL_loopVal = group.init(G1, 1)
	dotM_loopVal = group.init(G2, 1)
	sumN_loopVal = group.init(ZR, 0)



	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]
		dotB_loopVal = dotB_loopVal * dotB[index]
		dotC_loopVal = dotC_loopVal * dotC[index]
		dotD_loopVal = dotD_loopVal * dotD[index]
		dotE_loopVal = dotE_loopVal * dotE[index]
		dotF_loopVal = dotF_loopVal * dotF[index]
		dotG_loopVal = dotG_loopVal * dotG[index]
		dotH_loopVal = dotH_loopVal * dotH[index]
		dotI_loopVal = dotI_loopVal * dotI[index]
		dotJ_loopVal = dotJ_loopVal * dotJ[index]
		dotK_loopVal = dotK_loopVal * dotK[index]
		dotL_loopVal = dotL_loopVal * dotL[index]
		dotM_loopVal = dotM_loopVal * dotM[index]
		sumN_loopVal = sumN_loopVal + sumN[index]


	if ( ( pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g1^b' ] , dotA_loopVal ) *( pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g^ba1' ] , dotB_loopVal ) *( pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g^a1' ] , dotC_loopVal ) *( pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g^ba2' ] , dotD_loopVal ) * pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g^a2' ] , dotE_loopVal ) ) ) ) )==( pair( dotF_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'tau1' ] ) *( pair( dotG_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'tau2' ] ) *( pair( dotH_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'tau1^b' ] ) *( pair( dotI_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'tau2^b' ] ) *( pair( dotJ_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'w2' ] ) *( pair( dotK_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'u2' ] ) *( pair( dotL_loopVal , verifyArgsDict[z]['mpk'][bodyKey] [ 'h2' ] ) *( pair( verifyArgsDict[z]['mpk'][bodyKey] [ 'g1' ] , dotM_loopVal ) * A ** sumN_loopVal ) ) ) ) ) ) ) )  ):
		pass
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			if startSigNum not in incorrectIndices:
				incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, A, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG, dotH, dotI, dotJ, dotK, dotL, dotM, sumN)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, A, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG, dotH, dotI, dotJ, dotK, dotL, dotM, sumN)
		return

