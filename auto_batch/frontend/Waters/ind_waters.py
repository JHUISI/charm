from charm.pairing import *
from toolbox.iterate import dotprod
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
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
	lam_func = lambda i,a,b: a[i] ** b[i]

	for sigIndex in range(0, numSigs):
		for arg in verifyFuncArgs:
			if (sigNumKey in verifyArgsDict[sigIndex][arg]):
				argSigIndexMap[arg] = int(verifyArgsDict[sigIndex][arg][sigNumKey])
			else:
				argSigIndexMap[arg] = sigIndex
		h = hashObj.copy(  )
		h.update( bytes( verifyArgsDict[argSigIndexMap['ID']]['ID'][bodyKey] , 'utf-8' )  )
		hash = Bytes( h.digest( )  )
		val = Conversion.OS2IP( hash )
		bstr = bin( val ) [ 2 :  ]
		v = [  ]
		for i in range( verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'x' ] )  :
			binsubstr = bstr [ verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'l' ] * i : verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'l' ] *( i + 1 )  ]
			intval = int( binsubstr , 2 )
			intelement = group.init( ZR , intval )
			v.append( intelement )
		k = v
		h = hashObj.copy(  )
		h.update( bytes( verifyArgsDict[argSigIndexMap['M']]['M'][bodyKey] , 'utf-8' )  )
		hash = Bytes( h.digest( )  )
		val = Conversion.OS2IP( hash )
		bstr = bin( val ) [ 2 :  ]
		v = [  ]
		for i in range( verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'x' ] )  :
			binsubstr = bstr [ verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'l' ] * i : verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'l' ] *( i + 1 )  ]
			intval = int( binsubstr , 2 )
			intelement = group.init( ZR , intval )
			v.append( intelement )
		m = v
		S1 = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'S1' ]
		S2 = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'S2' ]
		S3 = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'S3' ]
		A = verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'A' ]
		g2 = verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'g2' ]
		comp1 = dotprod( group.init( G2 ) , - 1 , verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'x' ] , lam_func , verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'ub' ] , k )
		comp2 = dotprod( group.init( G2 ) , - 1 , verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'x' ] , lam_func , verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'ub' ] , m )
		if( pair( S1 , g2 ) * pair( S2 , verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'u1b' ] * comp1 ) * pair( S3 , verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'u2b' ] * comp2 ) ) == A :
			pass
		else:
			print("Verification of signature " + str(sigIndex) + " failed.\n")
