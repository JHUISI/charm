from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy, random
from bat_bls import runBLS_Batch

sigNumKey = 'Signature_Number'
bodyKey = 'Body'
charmPickleSuffix = '.charmPickle'
pythonPickleSuffix = '.pythonPickle'
repeatSuffix = '.repeat'
lenRepeatSuffix = len(repeatSuffix)

trials = 1
time_in_ms = 1000
SIGS_PER_CYCLE = 750
MS_PER_CYCLE = 1000
TIMER = 0
NUM_CYCLES = 100

def shuffle(oldList):
	lenList = len(oldList)
	newList = []

	for i in range(0, lenList):
		randNum = random.choice(oldList)
		newList.append(randNum)
		oldList.remove(randNum)

	return newList

def loadDictDataFromFile(verifyParamFilesDict, groupParamArg):
	verifyArgsDict = {}
	totalNumSigs = len(verifyParamFilesDict)
	verifyFuncArgs = list(verifyParamFilesDict[0].keys())

	for sigIndex in range(0, totalNumSigs):
		verifyArgsDict[sigIndex] = {}
		for arg in verifyFuncArgs:
			verifyArgsDict[sigIndex][arg] = {}
			verifyParamFile = str(verifyParamFilesDict[sigIndex][arg])
			if (verifyParamFile.endswith(charmPickleSuffix)):
				verifyParamPickle = open(verifyParamFile, 'rb').read()
				verifyArgsDict[sigIndex][arg][bodyKey] = deserializeDict( unpickleObject( verifyParamPickle ) , groupParamArg )
				#if groupParamArg.isMember( verifyArgsDict[counterFromZero][arg][bodyKey] ) == False:
					#sys.exit("The " + arg + " member of signature number " + sigIndex + " has failed the group membership check.  Exiting.\n")
			elif (verifyParamFile.endswith(pythonPickleSuffix)):
				verifyParamPickle = open(verifyParamFile, 'rb')
				verifyArgsDict[sigIndex][arg][bodyKey] = pickle.load(verifyParamPickle)
			elif (verifyParamFile.endswith(repeatSuffix)):
				verifyArgsDict[sigIndex][arg][sigNumKey] = verifyParamFile[0:(len(verifyParamFile) - lenRepeatSuffix)]
			else:
				tempFile = open(verifyParamFile, 'rb')
				tempBuf = tempFile.read()
				verifyArgsDict[sigIndex][arg][bodyKey] = tempBuf

	return verifyArgsDict

def loadDataFromDictInMemory(verifyParamFilesDict, startIndex, numSigsToProcess, verifyArgsDict, counterToStartFrom, incorrectSigIndices = []):

	totalNumSigs = len(verifyParamFilesDict)
	verifyFuncArgs = list(verifyParamFilesDict[0].keys())
	counterFromZero = counterToStartFrom

	for i in range(startIndex, (startIndex + numSigsToProcess)):
		sigIndex = i % totalNumSigs
		verifyArgsDict[counterFromZero] = verifyParamFilesDict[sigIndex]
		incorrectSigIndices.append(counterFromZero)
		counterFromZero += 1

	return (counterFromZero - 1)

def getIndexReplacement(randomizedIndices, numSigs, indexToFind):
	for sigIndex in range(0, numSigs):
		possibleIndex = randomizedIndices[sigIndex]
		if ( int(possibleIndex) == int(indexToFind) ):
			return sigIndex

	return -1

if __name__ == '__main__':
	if ( (len(sys.argv) != 6) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + sys.argv[0] + "\n\t[dictionary with valid messages/signatures]\n\t[dictionary with invalid messages/signatures]\n\t[path and filename of invalid sig distribution]\n\t[path and filename of group param file]\n\t[name of output file]\n")

	validDictArg = open(sys.argv[1], 'rb').read()
	invalidDictArg = open(sys.argv[2], 'rb').read()
	invalidSigDistro = open(sys.argv[3], 'r').readlines()


	groupParamArg = PairingGroup(int(sys.argv[4]))
	#groupParamArg = PairingGroup(80)

	outputFileName = sys.argv[5]

	testOutputFileName = open('invalidSigsGraph', 'w')

	testString = ""

	validDictFile = deserializeDict( unpickleObject(validDictArg), groupParamArg )
	invalidDictFile = deserializeDict( unpickleObject(invalidDictArg), groupParamArg )

	validDict = loadDictDataFromFile(validDictFile, groupParamArg)
	invalidDict = loadDictDataFromFile(invalidDictFile, groupParamArg)

	lastValidSigNum = 0
	lastInvalidSigNum = 0

	outputString = ""
	#outputString += "CYCLE NUM.\t\tTIMER\t\tSIGS_PER_CYCLE\t\tNum valid sigs\t\tNum invalid sigs\n\n"

	for cycle in range(0, NUM_CYCLES):

		#print(cycle)

		numInvalidSigs = int(invalidSigDistro[cycle])

		if (numInvalidSigs > SIGS_PER_CYCLE):
			numInvalidSigs = SIGS_PER_CYCLE

		numValidSigs = SIGS_PER_CYCLE - numInvalidSigs

		sigsDict = {}
		endCounter = loadDataFromDictInMemory(validDict, lastValidSigNum, numValidSigs, sigsDict, 0)

		lastValidSigNum += numValidSigs
		endCounter += 1

		realIncorrectSigIndices = []

		loadDataFromDictInMemory(invalidDict, lastInvalidSigNum, numInvalidSigs, sigsDict, endCounter, realIncorrectSigIndices)

		lastInvalidSigNum += numInvalidSigs

		preRandomizedIndices = []
		for randomIndex in range(0, (numValidSigs + numInvalidSigs)):
			preRandomizedIndices.append(randomIndex)

		randomizedIndices = shuffle(preRandomizedIndices)

		if (preRandomizedIndices != []):
			sys.exit("Problems with randomly shuffling the valid and invalid signatures.")

		verifyArgsDictRandomized = {}

		randomizedIncorrectSigIndices = []

		for sigIndex in range(0, (numValidSigs + numInvalidSigs)):
			verifyArgsDictRandomized[sigIndex] = sigsDict[randomizedIndices[sigIndex]]
			if (randomizedIndices[sigIndex] in realIncorrectSigIndices):
				randomizedIncorrectSigIndices.append(sigIndex)

		#print("total is " + str(numValidSigs + numInvalidSigs))

		verifyFuncArgs = list(verifyArgsDictRandomized[0].keys())

		bID1 = InitBenchmark()

		StartBenchmark(bID1, [RealTime])
		incorrectSigIndices = runBLS_Batch(verifyArgsDictRandomized, groupParamArg, verifyFuncArgs)
		EndBenchmark(bID1)

		result = (GetBenchmark(bID1, RealTime) / trials) * time_in_ms

		TIMER += result

		#outputString += str(cycle+1) + "\t\t\t" + str(TIMER) + "\t\t\t" + str(SIGS_PER_CYCLE) + "\t\t" + str(numValidSigs) + "\t\t\t" + str(numInvalidSigs) + "\n\n"
		outputString += str(TIMER) + " " + str(SIGS_PER_CYCLE) + "\n"
		testString += str(TIMER) + " " + str(numInvalidSigs) + "\n"
		print("outputString")
		print(str(TIMER) + " " + str(SIGS_PER_CYCLE) + "\n")
		print("test")
		print(str(TIMER) + " " + str(numInvalidSigs) + "\n")

		if ( (randomizedIncorrectSigIndices.sort()) != (incorrectSigIndices.sort()) ):
			sys.exit("Error:  batch code returned wrong results for which signatures are invalid.")

		SIGS_PER_CYCLE = int( ( float(MS_PER_CYCLE) / float(result) ) * SIGS_PER_CYCLE )
		if (SIGS_PER_CYCLE == 0):
			SIGS_PER_CYCLE = 1

		del sigsDict
		del randomizedIndices
		del verifyArgsDictRandomized
		del incorrectSigIndices
		del realIncorrectSigIndices
		del randomizedIncorrectSigIndices

	outputFile = open(outputFileName, 'w')
	outputFile.write(outputString)
	outputFile.close()
	del outputFile

	testOutputFileName.write(testString)

	testOutputFileName.close()
