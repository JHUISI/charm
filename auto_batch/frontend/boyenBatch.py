from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
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
	verifyFuncArgs = list(verifyParamFilesDict[0].keys())

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

	argSigIndexMap = {}

	group = pairing('/Users/matt/Documents/charm/param/d224.param')
	H = lambda a: group.H(('1', str(a)), ZR)


	N = 1
	l = 3

	deltaj = {}

	for sigIndex in range(0, N):
		deltaj[sigIndex] = prng_bits(group, 80)


	dotE = group.init(GT, 1)

	At_pk = {}
	Bt_pk = {}
	Ct_pk = {}
	At_pk[ 0 ] = verifyArgsDict[0]['mpk'][bodyKey][ 'At' ]
	Bt_pk[ 0 ] = verifyArgsDict[0]['mpk'][bodyKey][ 'Bt' ]
	Ct_pk[ 0 ] = verifyArgsDict[0]['mpk'][bodyKey][ 'Ct' ]

	
	for a in range(0, l):
		
		dotA = group.init(G1, 1)
		dotB = group.init(G1, 1)
		dotC = group.init(G1, 1)
		
		for b in range(0, N):
			for arg in verifyFuncArgs:
				if (sigNumKey in verifyArgsDict[b][arg]):
					argSigIndexMap[arg] = int(verifyArgsDict[b][arg][sigNumKey])
				else:
					argSigIndexMap[arg] = b

			for i in verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey].keys():
				At_pk[ i ] = verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ i ][ 'At' ]
				Bt_pk[ i ] = verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ i ][ 'Bt' ]
				Ct_pk[ i ] = verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ i ][ 'Ct' ]        
			l = len(At_pk.keys())
			D = pair(verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey]['g1'], verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey]['g2'])
			S = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey]['S'] 
			t = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey]['t']
			m = H(verifyArgsDict[argSigIndexMap['M']]['M'][bodyKey])
			dotA = dotA * (S[a] ** deltaj[b])

			dotB = dotB * (dotA ** m)

			dotC = dotC * (dotA ** t[a])

		dotE = dotE * (pair(dotA, At_pk[a]) * pair(dotB, Bt_pk[a]) * pair(dotC, Ct_pk[a]))

	sum = group.init(ZR, 0)

	for b in range(0, N):
		sum = deltaj[b] + sum

	if (dotE) == (D ** sum):
		print("success")
	else:
		print("failure")
