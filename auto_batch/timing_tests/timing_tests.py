from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy, random
from bat_bls import runBLS_Batch

sigNumKey = 'Signature_Number'
bodyKey = 'Body'
charmPickleSuffix = '.charmPickle'
pythonPickleSuffix = '.pythonPickle'
repeatSuffix = '.repeat'

trials = 1
time_in_ms = 1000
SIGS_PER_CYCLE = 100
MS_PER_CYCLE = 1000
TIMER = 0
NUM_CYCLES = 20

def getNumInvalidSigs()
	return 10

def loadDataFromDict(verifyParamFilesDict, startIndex, numSigsToProcess, dictToAddTo, counterToStartFrom):

	verifyArgsDict = dictToAddTo
	totalNumSigs = len(verifyParamFilesDict)
	lenRepeatSuffix = len(repeatSuffix)
	verifyFuncArgs = list(verifyParamFilesDict[0].keys())
	counterFromZero = counterToStartFrom

	for i in range(startIndex, (startIndex + numSigsToProcess)):
		sigIndex = i % totalNumSigs
		verifyArgsDict[counterFromZero] = {}
		for arg in verifyFuncArgs:
			verifyArgsDict[counterFromZero][arg] = {}
			verifyParamFile = str(verifyParamFilesDict[sigIndex][arg])
			if (verifyParamFile.endswith(charmPickleSuffix)):
				verifyParamPickle = open(verifyParamFile, 'rb').read()
				verifyArgsDict[counterFromZero][arg][bodyKey] = deserializeDict( unpickleObject( verifyParamPickle ) , groupParamArg )
				#if groupParamArg.isMember( verifyArgsDict[counterFromZero][arg][bodyKey] ) == False:
					#sys.exit("The " + arg + " member of signature number " + sigIndex + " has failed the group membership check.  Exiting.\n")
			elif (verifyParamFile.endswith(pythonPickleSuffix)):
				verifyParamPickle = open(verifyParamFile, 'rb')
				verifyArgsDict[counterFromZero][arg][bodyKey] = pickle.load(verifyParamPickle)
			elif (verifyParamFile.endswith(repeatSuffix)):
				verifyArgsDict[counterFromZero][arg][sigNumKey] = verifyParamFile[0:(len(verifyParamFile) - lenRepeatSuffix)]
			else:
				tempFile = open(verifyParamFile, 'rb')
				tempBuf = tempFile.read()
				verifyArgsDict[counterFromZero][arg][bodyKey] = tempBuf
		counterFromZero += 1

	return (counterFromZero - 1)

def getIndexReplacement(randomizedIndices, numSigs, indexToFind):
	for sigIndex in range(0, numSigs):
		possibleIndex = randomizedIndices[sigIndex]
		if ( int(possibleIndex) == int(indexToFind) ):
			return sigIndex

	return -1

if __name__ == '__main__':
	if ( (len(sys.argv) != 5) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + sys.argv[0] + " [dictionary with valid messages/signatures] [dictionary with invalid messages/signatures] [path and filename of group param file] [name of output file]")

	validDictFile = open(sys.argv[1], 'rb').read()
	invalidDictFile = open(sys.argv[2], 'rb').read()
	groupParamArg = PairingGroup(sys.argv[3])
	outputFileName = sys.argv[4]

	validDict = deserializeDict( unpickleObject(validDictFile), groupParamArg )
	invalidDict = deserializeDict( unpickleObject(invalidDictFile), groupParamArg )
	lastSigNum = 0
	endCounter = 0

	outputString = ""
	outputString += "CYCLE NUM.\tTIMER\tSIGS_PER_CYCLE\tNum valid sigs\tNum invalid sigs\n\n"

	for cycle in range(0, NUM_CYCLES):
		numInvalidSigs = getNumInvalidSigs()

		if (numInvalidSigs > SIGS_PER_CYCLE):
			numInvalidSigs = SIGS_PER_CYCLE

		numValidSigs = SIGS_PER_CYCLE - numInvalidSigs

		sigsDict = {}
		endCounter = loadDataFromDict(validDict, lastSigNum, numValidSigs, sigsDict, endCounter)
		lastSigNum += numValidSigs
		endCounter += 1
		endCounter = loadDataFromDict(invalidDict, lastSigNum, numInvalidSigs, sigsDict, endCounter)
		lastSigNum += numInvalidSigs
		endCounter += 1

		randomizedIndices = []
		for randomIndex in range(0, (numValidSigs + numInvalidSigs)):
			randomizedIndices.append(randomIndex)

		random.shuffle(randomizedIndices)

		verifyArgsDictRandomized = {}

		for sigIndex in range(0, (numValidSigs + numInvalidSigs)):
			verifyArgsDictRandomized[sigIndex] = sigsDict[randomizedIndices[sigIndex]]

		bID1 = InitBenchmark()
		StartBenchmark(bID1, [RealTime])
		runBLS_Batch(verifyArgsDictRandomized, groupParamArg, verifyFuncArgs)
		EndBenchmark(bID1)
		result = (GetBenchmark(bID1, RealTime) / trials) * time_in_ms

		TIMER += result

		outputString += str(cycle+1) + "\t" + str(TIMER) + "\t" + str(SIGS_PER_CYCLE) + "\t" + numValidSigs + "\t" + numInvalidSigs + "\n\n"

		del sigsDict
		del randomizedIndices
		del verifyArgsDictRandomized

	outputFile = open(outputFileName, 'w')
	outputFile.write(outputString)
	outputFile.close()
	del outputFile
