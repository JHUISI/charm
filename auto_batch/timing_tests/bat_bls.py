from toolbox.pairinggroup import *
from verifySigs import verifySigsRecursive

message = 1337

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

		if (type(verifyArgsDict[z][message][bodyKey]) != str):
			sys.exit("The message member of signature number " + z + " has failed the group membership check.  Exiting.\n")

		h = group.hash( verifyArgsDict[z][message][bodyKey] , G1 )
		dotA[z] =  h ** deltaz[z]

		if group.ismember(verifyArgsDict[z]['sig'][bodyKey]) == False:
			sys.exit("The sig member of signature number " + z + " has failed the group membership check.  Exiting.\n") 

		dotB[z] =  verifyArgsDict[z]['sig'][bodyKey] ** deltaz[z] 


	incorrectSigIndices = []

	if group.ismember( verifyArgsDict[0]['pk'][bodyKey]['g^x'] ) == False:
		sys.exit("The g^x member of signature number 0 has failed the group membership check.  Exiting.\n")



	if group.ismember( verifyArgsDict[0]['pk'][bodyKey]['g'] ) == False:
		sys.exit("The g member of signature number 0 has failed the group membership check.  Exiting.\n")

	verifySigsRecursive(verifyFuncArgs, verifyArgsDict, dotA, dotB,  verifyArgsDict[0]['pk'][bodyKey]['g^x'],  verifyArgsDict[0]['pk'][bodyKey]['g'], 0, N, group, incorrectSigIndices)

	return incorrectSigIndices
