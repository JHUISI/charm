from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy
from charm.engine.util import *
from toolbox.pairinggroup import *

bodyKey = 'Body'

def verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, startIndex, endIndex):
	group = PairingGroup('../../param/d224.param')
	for arg in verifyFuncArgs:
		argSigIndexMap[arg] = 0

	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G1, 1)

	for index in range(startIndex, endIndex):
		dotA_runningProduct = dotA_runningProduct * dotA[index]
		dotB_runningProduct = dotB_runningProduct * dotB[index]

	if pair ( dotA_runningProduct ,  verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey]['g^x'] ) == pair ( dotB_runningProduct ,  verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey]['g'] ):
		return
	else:
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			print("sig " + str(startIndex) + " failed\n")
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, startIndex, midIndex)
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, midIndex, endIndex)
