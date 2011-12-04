from charm.pairing import *
from toolbox.PKSig import PKSig
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

if __name__ == '__main__':
	if ( (len(sys.argv) != 3) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("\nUsage:  python BatchVerifyTemplate.py [filename of pickled Python dictionary with verify function arguments] [path and filename of group param file]\n")
	verifyParamFilesArg = sys.argv[1]
	verifyParamFiles = open(verifyParamFilesArg, 'rb').read()
	groupParamArg = PairingGroup(sys.argv[2])
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
				if groupParamArg.isMember( verifyArgsDict[sigIndex][arg][bodyKey] ) == False:
					sys.exit("The " + arg + " member of signature number " + sigIndex + " has failed the group membership check.  Exiting.\n")
			elif (verifyParamFile.endswith(pythonPickleSuffix)):
				verifyParamPickle = open(verifyParamFile, 'rb')
				verifyArgsDict[sigIndex][arg][bodyKey] = pickle.load(verifyParamPickle)
			elif (verifyParamFile.endswith(repeatSuffix)):
				verifyArgsDict[sigIndex][arg][sigNumKey] = verifyParamFile[0:(len(verifyParamFile) - lenRepeatSuffix)]
			else:
				tempFile = open(verifyParamFile, 'rb')
				tempBuf = tempFile.read()
				verifyArgsDict[sigIndex][arg][bodyKey] = tempBuf

	argSigIndexMap = {}

	group = pairing(80)
	H = lambda a: group.H(('1', str(a)), ZR)
	N = 1
	l = 3

	deltaz = {}
	dotC = {}
	dotB = {}
	dotA = {}
	sumE = {}
	dotD = {}

	for sigIndex in range(0, numSigs):
		deltaz[sigIndex] = prng_bits(group, 80)

	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G1, 1)
	dotC_runningProduct = group.init(G1, 1)
	for z in range(0, N):
		for arg in verifyFuncArgs:
			if (sigNumKey in verifyArgsDict[z][arg]):
				argSigIndexMap[arg] = int(verifyArgsDict[z][arg][sigNumKey])
			else:
				argSigIndexMap[arg] = z

		S = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'S' ]
		t = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 't' ]


		preA =  S[y] ** deltaz[z] 

		dotA[z] =  preA 

		dotB[z] =  preA ** verifyArgsDict[argSigIndexMap['M']]['M'][bodyKey] 

		dotC[z] =  preA ** t 


	sumE_runningProduct = group.init(ZR, 0)
	for z in range(0, N):
		for arg in verifyFuncArgs:
			if (sigNumKey in verifyArgsDict[z][arg]):
				argSigIndexMap[arg] = int(verifyArgsDict[z][arg][sigNumKey])
			else:
				argSigIndexMap[arg] = z



		sumE[z] =  deltaz[z] 


	D = pair( verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'g1' ] , verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'g2' ]  )


	verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotC, sumE, D, 0, N)
