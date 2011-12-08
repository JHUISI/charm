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

	group = PairingGroup('/Users/matt/Documents/charm/param/d224.param')

	for sigIndex in range(0, numSigs):
		for arg in verifyFuncArgs:
			if (sigNumKey in verifyArgsDict[sigIndex][arg]):
				argSigIndexMap[arg] = int(verifyArgsDict[sigIndex][arg][sigNumKey])
			else:
				argSigIndexMap[arg] = sigIndex
		A , B = verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey] , verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey]
		h = group.hash( verifyArgsDict[argSigIndexMap['message']]['message'][bodyKey] , G1 )
		if pair( verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey] , verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ 'g' ] ) == pair( h , verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ 'g^x' ] )  :
			pass
		else:
			print("Verification of signature " + str(sigIndex) + " failed.\n")
