from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy
from charm.engine.util import *
from toolbox.pairinggroup import *

bodyKey = 'Body'

def verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotB, dotC, mpk_0, mpk_1, startIndex, endIndex, group):

	#group = pairing('/Users/matt/Documents/charm/param/a.param')
	#group = PairingGroup(80)

	H1 = lambda x: group.hash(('1', str(x)), G1)
	H2 = lambda a, b, c: group.hash(('2', a, b, c), ZR)
	lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i]) # => u * (pk ** h) for all signers
	for arg in verifyFuncArgs:
		argSigIndexMap[arg] = 0

	dotB_runningProduct = group.init(G1, 1)
	dotC_runningProduct = group.init(G1, 1)

	for index in range(startIndex, endIndex):
		dotB_runningProduct = dotB_runningProduct * dotB[index]
		dotC_runningProduct = dotC_runningProduct * dotC[index]

	if pair ( dotB_runningProduct , mpk_0 ) == pair ( dotC_runningProduct , mpk_1 ):
		return
	else:
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			print("sig " + str(startIndex) + " failed\n")
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotB, dotC, mpk_0, mpk_1, startIndex, midIndex, group)
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotB, dotC, mpk_0, mpk_1, midIndex, endIndex, group)
