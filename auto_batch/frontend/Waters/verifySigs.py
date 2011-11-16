from charm.pairing import *
from toolbox.iterate import dotprod
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy
from charm.engine.util import *
from toolbox.pairinggroup import *

bodyKey = 'Body'

def verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotD, sumF, mpk_1, u1b, u2b, A, startIndex, endIndex):
	group = pairing(80)
	lam_func = lambda i,a,b: a[i] ** b[i]
	for arg in verifyFuncArgs:
		argSigIndexMap[arg] = 0

	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G1, 1)
	dotE_runningProduct = group.init(GT, 1)
	dotD_runningProduct = group.init(G1, 1)
	sumF_runningProduct = group.init(ZR, 0)
	dotE_runningProduct = group.init(GT, 1)
	for y in range(0, l):
		dotE_runningProduct = dotE_runningProduct *  pair ( ( prod{ 



	for index in range(startIndex, endIndex):
		dotA_runningProduct = dotA_runningProduct * dotA[index]
		dotB_runningProduct = dotB_runningProduct * dotB[index]
		dotD_runningProduct = dotD_runningProduct * dotD[index]
		sumF_runningProduct = sumF_runningProduct + sumF[index]

	if ( pair ( dotA_runningProduct , mpk_1 ) * ( ( pair ( dotB_runningProduct , u1b ) * dotE_runningProduct ) * pair ( dotD_runningProduct , u2b ) ) ) == A ** sumF_runningProduct:
		return
	else:
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			print("sig " + str(startIndex) + " failed\n")
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotE, dotD, sumF, mpk_1, u1b, u2b, A, startIndex, midIndex)
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotE, dotD, sumF, mpk_1, u1b, u2b, A, midIndex, endIndex)
