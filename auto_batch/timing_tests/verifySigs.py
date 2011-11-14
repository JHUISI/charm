from toolbox.pairinggroup import *
from charm.engine.util import *

bodyKey = 'Body'

def verifySigsRecursive(verifyFuncArgs, verifyArgsDict, dotA, dotB, pk_0, pk_1, startIndex, endIndex, group, incorrectSigIndices):

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
			incorrectSigIndices.append(startIndex)
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(verifyFuncArgs, verifyArgsDict, dotA, dotB, pk_0, pk_1, startIndex, midIndex, group, incorrectSigIndices)
		verifySigsRecursive(verifyFuncArgs, verifyArgsDict, dotA, dotB, pk_0, pk_1, midIndex, endIndex, group, incorrectSigIndices)
