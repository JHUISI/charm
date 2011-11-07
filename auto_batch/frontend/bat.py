from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
import sys, copy
from charm.engine.util import *
from toolbox.pairinggroup import *

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

	for sigIndex in range(1, (numSigs+1)):
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

	group = pairing('../param/a.param')
	H1 = lambda x: group.H(('1', str(x)), G1)
	H2 = lambda a, b, c: group.H(('2', a, b, c), ZR)
	lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i]) # => u * (pk ** h) for all signers
	N = 100
	numSigners = 5

	Sb = {}
	deltab = {}
	ua = {}
	uab = {}
	pka = {}
	pkab = {}
	ha = {}
	hab = {}
	dotC = {}
	dotB = {}
	dotA = {}

	for sigIndex in range(1, (numSigs+1)):
		deltab.append(prng_bits(ZR, 80))

	dotB_runningProduct = 1
	dotC_runningProduct = 1
	for b in range(0, N):
		for arg in verifyFuncArgs:
			if (sigNumKey in verifyArgsDict[sigIndex][arg]):
				argSigIndexMap[arg] = int(verifyArgsDict[sigIndex][arg][sigNumKey])
			else:
				argSigIndexMap[arg] = sigIndex

		dotA_runningProduct = 1
		for a in range(0, numSigners):
			ua[a] = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'u' ]
			Lt = ""
			for i in verifyArgsDict[argSigIndexMap['L']]['L'][bodyKey] :
				Lt = Lt + ":" + i
			num_signers = len( verifyArgsDict[argSigIndexMap['L']]['L'][bodyKey] )
			ha[a] = [ group.init( ZR , 1 ) for i in range( num_signers ) ]
			for i in range( num_signers ) :
				ha[a] [ i ] = H2( verifyArgsDict[argSigIndexMap['M']]['M'][bodyKey] , Lt ,ua[a] [ i ] )
			pka[a] = [ H1( i ) for i in verifyArgsDict[argSigIndexMap['L']]['L'][bodyKey] ] # get all signers pub keys

			dotA[a] =  ( ua[a]  * pka[a]  ** ha[a]  ) 
			dotA_runningProduct = dotA_runningProduct * dotA[a]

		uab[b] = copy.deepcopy(ua)
		pkab[b] = copy.deepcopy(pka)
		hab[b] = copy.deepcopy(ha)


		dotB[b] =  dotA_runningProduct ** deltab[b]  
		dotB_runningProduct = dotB_runningProduct * dotB[b]

		Sb[b] = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'S' ]

		dotC[b] =  Sb[b]  ** deltab[b]  
		dotC_runningProduct = dotC_runningProduct * dotC[b]


	for arg in verifyFuncArgs:
		argSigIndexMap[arg] = 1

	if pair ( dotB_runningProduct ,  verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey]['Pub'] ) == pair ( dotC_runningProduct ,  verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey]['g'] ):
		pass
	else:
		print("Batch verification has failed.\n")