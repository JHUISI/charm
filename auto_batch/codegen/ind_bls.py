from toolbox.pairinggroup import *
from charm.engine.util import *
import sys

# Constants used to load message/signature data from disk

#sigNumKey = 'Signature_Number'
#bodyKey = 'Body'
#charmPickleSuffix = '.charmPickle'
#pythonPickleSuffix = '.pythonPickle'
#repeatSuffix = '.repeat'

N = 200
l = 1

global group
group = PairingGroup(80)

def keygen(self, secparam=None):
	g = group.random(G2)
	x = group.random(ZR)
	g_x = g ** x
	pk = { 'g^x':g_x, 'g':g, 'identity':str(g_x), 'secparam':secparam }
	sk = { 'x':x }
	return (pk, sk)

def sign(x, message):
	sig = group.hash(message, G1) ** x
	return sig

def verify():
	"""
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
	"""
	group = groupParamArg
	N = numSigs

	for sigIndex in range(0, numSigs):

		# Load references so we can get to the data if there are pointers
		for arg in verifyFuncArgs:
			if (sigNumKey in verifyArgsDict[sigIndex][arg]):
				argSigIndexMap[arg] = int(verifyArgsDict[sigIndex][arg][sigNumKey])
			else:
				argSigIndexMap[arg] = sigIndex


		# Group membership checks
		if (type( verifyArgsDict[argSigIndexMap['message']]['message'][bodyKey] ) != str):
			sys.exit("Group membership check failed")

		if (group.ismember( verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey] ) == False):
			sys.exit("Group membership check failed")

		if (group.ismember( verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey]['g^x'] ) == False):
			sys.exit("Group membership check failed")

		if (group.ismember( verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey]['g'] ) == False):
			sys.exit("Group membership check failed")


		# Scheme-specific code to test the signature
		h = group.hash( message , G1 )
		if pair( verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey] , verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ 'g' ] ) == pair( h , verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ 'g^x' ] )  :
			pass
		else:
			print("Verification of signature " + str(sigIndex) + " failed.\n")
