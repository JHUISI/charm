from toolbox.pairinggroup import *
from charm.engine.util import *
import sys
from verifySigs import verifySigsRecursive

#Constants for loading message/signature data from disk

sigNumKey = 'Signature_Number'
bodyKey = 'Body'
charmPickleSuffix = '.charmPickle'
pythonPickleSuffix = '.pythonPickle'
repeatSuffix = '.repeat'


#For deltas

def prng_bits(group, bits=80):
	return group.init(ZR, randomBits(bits))

if __name__ == '__main__':
	if ( (len(sys.argv) != 3) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + sys.argv[0] + " [filename of pickled Python dictionary with message/signature data] [group parameter]")

	#Load data from disk

	verifyParamFilesArg = sys.argv[1]
	verifyParamFiles = open(verifyParamFilesArg, 'rb').read()
	groupParamArg = PairingGroup(int(sys.argv[2]))
	verifyParamFilesDict = deserializeDict( unpickleObject( verifyParamFiles ) , groupParamArg )
	verifyArgsDict = {}
	numSigs = len(verifyParamFilesDict)
	lenRepeatSuffix = len(repeatSuffix)
	verifyFuncArgs = list(verifyParamFilesDict[1].keys())

	for sigIndex in range(0, numSigs):
		verifyArgsDict[sigIndex] = {}
		for arg in verifyFuncArgs:
			verifyArgsDict[sigIndex][arg] = {}
			verifyParamFile = str(verifyParamFilesDict[sigIndex][arg])
			if (verifyParamFile.endswith(charmPickleSuffix)):
				verifyParamPickle = open(verifyParamFile, 'rb').read()
				verifyArgsDict[sigIndex][arg][bodyKey] = deserializeDict( unpickleObject( verifyParamPickle ) , groupParamArg )
			elif (verifyParamFile.endswith(pythonPickleSuffix)):
				verifyParamPickle = open(verifyParamFile, 'rb')
				verifyArgsDict[sigIndex][arg][bodyKey] = pickle.load(verifyParamPickle)
			elif (verifyParamFile.endswith(repeatSuffix)):
				verifyArgsDict[sigIndex][arg][sigNumKey] = verifyParamFile[0:(len(verifyParamFile) - lenRepeatSuffix)]
			else:
				tempFile = open(verifyParamFile, 'rb')
				tempBuf = tempFile.read()
				verifyArgsDict[sigIndex][arg][bodyKey] = tempBuf


	# Holds pointers to the data in the case of repeat information
	argSigIndexMap = {}

	N = numSigs

	group = groupParamArg

	deltaz = {}

	# Dot products used for optimized batching
	dotB = {}
	dotA = {}

	# Calculate deltas
	for sigIndex in range(0, numSigs):
		deltaz[sigIndex] = prng_bits(group, 80)

	# Initialize dot products
	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G1, 1)

	# Precompute dot products that can be cached between runs of divide-and-conquer
	for z in range(0, N):

		#print(verifyArgsDict)

		# Load references so we can get to the data if there are pointers
		for arg in verifyFuncArgs:
			if (sigNumKey in verifyArgsDict[z][arg]):
				argSigIndexMap[arg] = int(verifyArgsDict[z][arg][sigNumKey])
			else:
				argSigIndexMap[arg] = z



		# Group membership checks
		if (type( verifyArgsDict[argSigIndexMap['message']]['message'][bodyKey] ) != str):
			sys.exit("Group membership check failed")

		if (group.ismember( verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey] ) == False):
			sys.exit("Group membership check failed")

		if (group.ismember( verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey]['g^x'] ) == False):
			sys.exit("Group membership check failed")

		if (group.ismember( verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey]['g'] ) == False):
			sys.exit("Group membership check failed")
		


		# Begin scheme-specific code used for precomputed dot products
		h = group.hash( verifyArgsDict[argSigIndexMap['message']]['message'][bodyKey] , G1 )
		dotA[z] =  h ** deltaz[z] 
		dotB[z] =  verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey] ** deltaz[z] 


	#Recursive algorithm that handles divide-and-conquer
	verifySigsRecursive(group, verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB,  verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey]['g^x'],  verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey]['g'], 0, N)

	print("here")
