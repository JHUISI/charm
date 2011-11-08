from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy
from charm.engine.util import *
from toolbox.pairinggroup import *

bodyKey = 'Body'

def verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotB, dotC, startIndex, endIndex):
	for arg in verifyFuncArgs:
		argSigIndexMap[arg] = 0

	dotB_runningProduct = 1
	dotC_runningProduct = 1

	for index in range(startIndex, endIndex):
		dotB_runningProduct = dotB_runningProduct * dotB[index]
		dotC_runningProduct = dotC_runningProduct * dotC[index]

	if pair ( dotB_runningProduct ,  verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey]['Pub'] ) == pair ( dotC_runningProduct ,  verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey]['g'] ):
		return
	else:
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			print("sig " + str(startIndex) + " failed\n")
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotB, dotC, startIndex, midIndex)
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotB, dotC, midIndex, endIndex)
