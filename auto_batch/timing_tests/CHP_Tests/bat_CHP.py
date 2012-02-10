from toolbox.pairinggroup import *
from verifySigs import verifySigsRecursive

bodyKey = 'Body'

def prng_bits(group, bits=80):
	return group.init(ZR, randomBits(bits))

def runCHP_Batch(verifyArgsDict, group, verifyFuncArgs):
	N = len(verifyArgsDict)

	H = lambda prefix,x: group.H((str(prefix), str(x)), G1)
	H3 = lambda a,b: group.H(('3', str(a), str(b)), ZR)

	deltaz = {}
	dotC = {}
	dotB = {}
	dotA = {}

	for sigIndex in range(0, N):
		deltaz[sigIndex] = prng_bits(group, 80)

	incorrectIndices = []

	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G2, 1)
	dotC_runningProduct = group.init(G2, 1)
	for z in range(0, N):
		if (type(verifyArgsDict[z]['message'][bodyKey][ 'str' ]) != str):
			sys.exit("member check failed")

		if (type(verifyArgsDict[z]['message'][bodyKey][ 't3' ]) != str):
			sys.exit("member check failed")

		if (group.ismember(verifyArgsDict[z]['sig'][bodyKey]) == False):
			sys.exit("member check failed")

		if (group.ismember(verifyArgsDict[z]['pk'][bodyKey]) == False):
			sys.exit("member check failed")

		if (type(verifyArgsDict[z]['message'][bodyKey][ 't1' ]) != str):
			sys.exit("member check failed")

		if (type(verifyArgsDict[z]['message'][bodyKey][ 't2' ]) != str):
			sys.exit("member check failed")

		if (group.ismember(verifyArgsDict[z]['mpk'][bodyKey]['g']) == False):
			sys.exit("member check failed")


		b = H3( verifyArgsDict[z]['message'][bodyKey][ 'str' ] , verifyArgsDict[z]['message'][bodyKey][ 't3' ]  )


		dotA[z] =  verifyArgsDict[z]['sig'][bodyKey] ** deltaz[z] 

		preA =  verifyArgsDict[z]['pk'][bodyKey] ** deltaz[z] 

		dotB[z] =  preA 

		dotC[z] =  preA ** b 


	a = H( 1 , verifyArgsDict[z]['message'][bodyKey][ 't1' ]  )
	h = H( 2 , verifyArgsDict[z]['message'][bodyKey][ 't2' ]  )


	verifySigsRecursive(verifyFuncArgs, verifyArgsDict, dotA, dotB, dotC,  verifyArgsDict[z]['mpk'][bodyKey]['g'], a, h, 0, N, group, incorrectIndices)

	return incorrectIndices
