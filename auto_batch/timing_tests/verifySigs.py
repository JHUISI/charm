from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy
from charm.engine.util import *
from toolbox.pairinggroup import *

bodyKey = 'Body'

def verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, pk_0, pk_1, startIndex, endIndex, group):
	for arg in verifyFuncArgs:
		argSigIndexMap[arg] = 0

	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G1, 1)

	for index in range(startIndex, endIndex):
		dotA_runningProduct = dotA_runningProduct * dotA[index]
		dotB_runningProduct = dotB_runningProduct * dotB[index]

	if pair ( dotA_runningProduct , pk_0 ) == pair ( dotB_runningProduct , pk_1 ):
		return
	else:
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			print("sig " + str(startIndex) + " failed\n")
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, pk_0, pk_1, startIndex, midIndex, group)
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, pk_0, pk_1, midIndex, endIndex, group)
