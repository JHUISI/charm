from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
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

	for sigIndex in range(0, numSigs):
		for arg in verifyFuncArgs:
			if (sigNumKey in verifyArgsDict[sigIndex][arg]):
				argSigIndexMap[arg] = int(verifyArgsDict[sigIndex][arg][sigNumKey])
			else:
				argSigIndexMap[arg] = sigIndex
		Atpk = { }
		Btpk = { }
		Ctpk = { }
		Atpk [ 0 ] = verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'At'  ]
		Btpk [ 0 ] = verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'Bt'  ]
		Ctpk [ 0 ] = verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'Ct'  ]
		for i in pk.keys( )  :
			Atpk [ i ] = verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ i ] [ 'At'  ]
			Btpk [ i ] = verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ i ] [ 'Bt'  ]
			Ctpk [ i ] = verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ i ] [ 'Ct'  ]
		l = len( Atpk.keys( )  )
		D = pair( verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'g1' ] , verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'g2' ]  )
		S = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'S' ]
		t = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 't' ]
		m = H( verifyArgsDict[argSigIndexMap['M']]['M'][bodyKey] )
		prod_result = group.init( GT , 1 )
		for i in range( l )  :
			prod_result * = pair( S [ i ] , Atpk [ i ] *( Btpk [ i ] ** m ) *( Ctpk [ i ] ** t [ i ] )  )
		if prod_result == D :
			pass
		else:
			print("Verification of signature " + str(sigIndex) + " failed.\n")
