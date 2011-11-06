from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
import sys
from charm.engine.util import *
from toolbox.pairinggroup import *

sigNumKey = 'Signature_Number'
bodyKey = 'Body'
charmPickleSuffix = '.charmPickle'
pythonPickleSuffix = '.pythonPickle'
repeatSuffix = '.repeat'

if __name__ == '__main__':
	if ( (len(sys.argv) != 3) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("\nUsage:  python IndividualVerifyTemplate.py [filename of pickled Python dictionary with verify function arguments] [path and filename of group param file]\n")
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

	for sigIndex in range(1, (numSigs+1)):
		for arg in verifyFuncArgs:
			if (sigNumKey in verifyArgsDict[sigIndex][arg]):
				argSigIndexMap[arg] = int(verifyArgsDict[sigIndex][arg][sigNumKey])
			else:
				argSigIndexMap[arg] = sigIndex
		u = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'u' ]
		S = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'S' ]
		Lt = self.concat( verifyArgsDict[argSigIndexMap['L']]['L'][bodyKey] )
		num_signers = len( verifyArgsDict[argSigIndexMap['L']]['L'][bodyKey] )
		h = [ group.init( ZR , 1 ) for i in range( num_signers )  ]
		for i in range( num_signers ) :
			h [ i ] = H2( verifyArgsDict[argSigIndexMap['M']]['M'][bodyKey] , Lt , u [ i ]  )
		pk = [ H1( i ) for i in verifyArgsDict[argSigIndexMap['L']]['L'][bodyKey] ] # get all signers pub keys
		result = dotprod( group.init( G1 ) , - 1 , num_signers , lam_func , u , pk , h )
		if pair( result , verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'Pub' ] ) == pair( S , verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'g' ] ) :
			pass
		else:
			print("Verification of signature " + str(sigIndex) + " failed.\n")
