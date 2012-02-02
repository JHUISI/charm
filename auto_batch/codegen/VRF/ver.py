from toolbox.pairinggroup import *
from toolbox.iterate import dotprod
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
import sys

group = None
lam_func = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group , lam_func 
	group= groupObj 
	lam_func= lambda i , a , b : a [ i ] ** b [ i ] 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG):
	z = 0

	group = groupObj

	lam_func = lambda i,a,b: a[i] ** b[i]

	__init__(group)


	dotA_loopVal = group.init(G1, 1)
	dotB_loopVal = group.init(G1, 1)
	dotC_loopVal = group.init(G1, 1)
	dotD_loopVal = group.init(G1, 1)
	dotE_loopVal = group.init(GT, 1)

	dotF_loopVal = {}
	dotG_loopVal = {}

	for t in range(1, n):
		dotF_loopVal[t] = group.init(G1, 1)
		dotG_loopVal[t] = group.init(G1, 1)

	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]
		dotB_loopVal = dotB_loopVal * dotB[index]
		dotC_loopVal = dotC_loopVal * dotC[index]
		dotD_loopVal = dotD_loopVal * dotD[index]
		dotE_loopVal = dotE_loopVal * dotE[index]

	for t in range(1, n):
		for index in range(startSigNum, endSigNum):
			dotF_loopVal[t] = dotF_loopVal[t] * dotF[index][t]
			dotG_loopVal[t] = dotG_loopVal[t] * dotG[index][t]

	if ( ( pair( dotA_loopVal , verifyArgsDict[z]['pk'][bodyKey] [ 'U_t' ] ) * pair( dotB_loopVal , verifyArgsDict[z]['pk'][bodyKey] [ 'g2' ] ) )== 1  ):
		pass
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			if startSigNum not in incorrectIndices:
				incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG)

	if ( ( pair( dotC_loopVal , verifyArgsDict[z]['pk'][bodyKey] [ 'U2' ] [ 0 ] ) * pair( dotD_loopVal ,( verifyArgsDict[z]['pk'][bodyKey] [ 'g2' ] * verifyArgsDict[z]['pk'][bodyKey] [ 'h' ] ** -1 ) ) )== dotE_loopVal  ):
		pass
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			if startSigNum not in incorrectIndices:
				incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG)

	for t in range(1, n):
		if (  pair( dotF_loopVal [ t ] , verifyArgsDict[z]['pk'][bodyKey] [ 'g2' ] )== pair( dotG_loopVal [ t ] , verifyArgsDict[z]['pk'][bodyKey] [ 'U2' ] [ t ] )  ):
			pass
		else:
			midWay = int( (endSigNum - startSigNum) / 2)
			if (midWay == 0):
				if startSigNum not in incorrectIndices:
					incorrectIndices.append(startSigNum)
				return
			midSigNum = startSigNum + midWay
			verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG)
			verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG)

