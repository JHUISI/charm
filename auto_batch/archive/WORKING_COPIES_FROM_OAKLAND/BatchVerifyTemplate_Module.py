from toolbox.pairinggroup import *
from verifySigs import verifySigsRecursive

bodyKey = 'Body'

def prng_bits(group, bits=80):
	return group.init(ZR, randomBits(bits))

def runBLS_Batch(verifyArgsDict, group, verifyFuncArgs):

	numSigs = len(verifyArgsDict)
	N = len(verifyArgsDict)
	verifyFuncArgs = list(verifyArgsDict[0].keys())
	incorrectSigIndices = []

	#MUST INSERT GROUP CHECKS
	#MUST ADD GROUP AND INCORRECT SIGINDICES TO CALL


	incorrectSigIndices = []


