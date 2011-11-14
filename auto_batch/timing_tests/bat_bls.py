from toolbox.pairinggroup import *
from charm.engine.util import *
from verifySigs import verifySigsRecursive

bodyKey = 'Body'

def prng_bits(group, bits=80):
	return group.init(ZR, randomBits(bits))

def runBLS_Batch(verifyArgsDict, group, verifyFuncArgs):
	N = len(verifyArgsDict)

	deltaz = {}
	dotB = {}
	dotA = {}

	for sigIndex in range(0, N):
		deltaz[sigIndex] = prng_bits(group, 80)

	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G1, 1)
	for z in range(0, N):
		h = group.hash( verifyArgsDict[z]['message'][bodyKey] , G1 )
		dotA[z] =  h ** deltaz[z] 
		dotB[z] =  verifyArgsDict[z]['sig'][bodyKey] ** deltaz[z] 

	incorrectSigIndices = []

	verifySigsRecursive(verifyFuncArgs, verifyArgsDict, dotA, dotB,  verifyArgsDict[0]['pk'][bodyKey]['g^x'],  verifyArgsDict[0]['pk'][bodyKey]['g'], 0, N, group, incorrectSigIndices)

	return incorrectSigIndices
