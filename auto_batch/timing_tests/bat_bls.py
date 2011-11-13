from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy
from charm.engine.util import *
from toolbox.pairinggroup import *
from verifySigs import verifySigsRecursive

sigNumKey = 'Signature_Number'
bodyKey = 'Body'
charmPickleSuffix = '.charmPickle'
pythonPickleSuffix = '.pythonPickle'
repeatSuffix = '.repeat'

def prng_bits(group, bits=80):
	return group.init(ZR, randomBits(bits))

def runBLS_Batch(verifyArgsDict, group, verifyFuncArgs):
	argSigIndexMap = {}
	N = 3
	deltaz = {}
	dotB = {}
	dotA = {}

	for sigIndex in range(0, N):
		deltaz[sigIndex] = prng_bits(group, 80)

	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G1, 1)
	for z in range(0, N):
		for arg in verifyFuncArgs:
			if (sigNumKey in verifyArgsDict[z][arg]):
				argSigIndexMap[arg] = int(verifyArgsDict[z][arg][sigNumKey])
			else:
				argSigIndexMap[arg] = z

		h = group.hash( verifyArgsDict[argSigIndexMap['message']]['message'][bodyKey] , G1 )


		dotA[z] =  h ** deltaz[z] 

		dotB[z] =  verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey] ** deltaz[z] 


	verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB,  verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey]['g^x'],  verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey]['g'], 0, N, group)
