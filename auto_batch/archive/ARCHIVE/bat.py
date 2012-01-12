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

	argSigIndexMap = {}

	group = pairing('/Users/matt/Documents/charm/param/a.param')
	H1 = lambda x: group.H(('1', str(x)), G1)
	H2 = lambda a, b, c: group.H(('2', a, b, c), ZR)
	lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i]) # => u * (pk ** h) for all signers
	N = 3
	l = 5

	deltaz = {}
	dotC = {}
	dotB = {}
	dotA = {}

	for sigIndex in range(0, numSigs):
		deltaz[sigIndex] = prng_bits(group, 80)

	dotB_runningProduct = group.init(G1, 1)
	dotC_runningProduct = group.init(G1, 1)
	for z in range(0, N):
		for arg in verifyFuncArgs:
			if (sigNumKey in verifyArgsDict[z][arg]):
				argSigIndexMap[arg] = int(verifyArgsDict[z][arg][sigNumKey])
			else:
				argSigIndexMap[arg] = z

		u = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'u' ]
		S = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'S' ]
		Lt = ""
		for i in verifyArgsDict[argSigIndexMap['L']]['L'][bodyKey] :
			Lt = Lt + ":" + i
		num_signers = len( verifyArgsDict[argSigIndexMap['L']]['L'][bodyKey] )
		h = [ group.init( ZR , 1 ) for i in range( num_signers ) ]
		for i in range( num_signers ) :
			h [ i ] = H2( verifyArgsDict[argSigIndexMap['M']]['M'][bodyKey] , Lt , u [ i ] )
		pk = [ H1( i ) for i in verifyArgsDict[argSigIndexMap['L']]['L'][bodyKey] ] # get all signers pub keys


		dotA_runningProduct = group.init(G1, 1)
		for y in range(0, l):
			dotA[y] =   ( u[a] * pk[a] ** h[a] )  
			dotA_runningProduct = dotA_runningProduct * dotA[y]

		dotB[z] =   dotA_runningProduct ** deltaz[z]  

		dotC[z] =   S ** deltaz[z]  


	verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotB, dotC, 0, N)
