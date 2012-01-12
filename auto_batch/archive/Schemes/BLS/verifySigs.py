from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy

bodyKey = 'Body'

#Recursive algorithm that handles divide-and-conquer
def verifySigsRecursive(group, verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, pk_0, pk_1, startIndex, endIndex):

	#Initialize dot products for this round of divide-and-conquer
	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G1, 1)

	#Calculate dot products
	for index in range(startIndex, endIndex):
		dotA_runningProduct = dotA_runningProduct * dotA[index]
		dotB_runningProduct = dotB_runningProduct * dotB[index]

	#Optimized batch verification equation
	if pair ( dotA_runningProduct , pk_0 ) == pair ( dotB_runningProduct , pk_1 ):
		return
	else:
		#Next round of divide-and-conquer
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			print("sig " + str(startIndex) + " failed\n")
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(group, verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, pk_0, pk_1, startIndex, midIndex)
		verifySigsRecursive(group, verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, pk_0, pk_1, midIndex, endIndex)
