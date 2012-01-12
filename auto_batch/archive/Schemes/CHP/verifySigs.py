from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy
from charm.engine.util import *
from toolbox.pairinggroup import *

bodyKey = 'Body'

def verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotC, mpk_0, a, h, startIndex, endIndex):
	group = pairing('/Users/matt/Documents/charm/param/a.param')
	H = lambda prefix,x: group.H((str(prefix), str(x)), G1)
	H3 = lambda a,b: group.H(('3', str(a), str(b)), ZR)
	for arg in verifyFuncArgs:
		argSigIndexMap[arg] = 0

	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G2, 1)
	dotC_runningProduct = group.init(G2, 1)

	for index in range(startIndex, endIndex):
		dotA_runningProduct = dotA_runningProduct * dotA[index]
		dotB_runningProduct = dotB_runningProduct * dotB[index]
		dotC_runningProduct = dotC_runningProduct * dotC[index]

	if pair ( dotA_runningProduct , mpk_0 ) == ( pair ( a , dotB_runningProduct ) * pair ( h , dotC_runningProduct ) ):
		return
	else:
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			print("sig " + str(startIndex) + " failed\n")
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotC, mpk_0, a, h, startIndex, midIndex)
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotC, mpk_0, a, h, midIndex, endIndex)
