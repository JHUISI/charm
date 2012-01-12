from charm.pairing import *
from toolbox.PKSig import PKSig
import sys, copy
from charm.engine.util import *
from toolbox.pairinggroup import *

bodyKey = 'Body'

def verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotC, startIndex, endIndex):
	for arg in verifyFuncArgs:
		argSigIndexMap[arg] = 0

	a = H( 1 , verifyArgsDict[argSigIndexMap['M']]['M'][bodyKey][ 't1' ] )
	h = H( 2 , verifyArgsDict[argSigIndexMap['M']]['M'][bodyKey][ 't2' ] )


	dotA_runningProduct = 1
	dotB_runningProduct = 1
	dotC_runningProduct = 1

	for index in range(startIndex, endIndex):
		dotA_runningProduct = dotA_runningProduct * dotA[index]
		dotB_runningProduct = dotB_runningProduct * dotB[index]
		dotC_runningProduct = dotC_runningProduct * dotC[index]

	if pair ( dotA_runningProduct ,  verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey]['g'] ) == ( pair ( a , dotB_runningProduct ) * pair ( h , dotC_runningProduct ) ):
		return
	else:
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			print("sig " + str(startIndex) + " failed\n")
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotC, startIndex, midIndex)
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotC, midIndex, endIndex)
