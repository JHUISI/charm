from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy, random
from bat_BLS import run_Batch
from ind_BLS import run_Ind

sigNumKey = 'Signature_Number'
bodyKey = 'Body'
charmPickleSuffix = '.charmPickle'
pythonPickleSuffix = '.pythonPickle'
repeatSuffix = '.repeat'
lenRepeatSuffix = len(repeatSuffix)

trials = 1
time_in_ms = 1000
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
				verifyArgsDict[sigIndex][arg][bodyKey] = bytesToObject(verifyParamPickle, groupParamArg)
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
	if ( (len(sys.argv) != 5) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + sys.argv[0] + "\n\t[dictionary with valid messages/signatures]\n\t[path and filename of group param file]\n\t[name of output file for individual]\n\t[name of output file for batch]\n")

	validDictArg = open(sys.argv[1], 'rb').read()
	groupParamArg = PairingGroup(int(sys.argv[2]))
	indOutputFileName = sys.argv[3]
	batOutputFileName = sys.argv[4]

	validDictFile = bytesToObject(validDictArg, groupParamArg)
	validDict = loadDictDataFromFile(validDictFile, groupParamArg)

	indOutputString = ""
	batOutputString = ""

	for numValidSigs in range(1, (NUM_CYCLES + 1)):
		sigsDict = {}
		loadDataFromDictInMemory(validDict, 0, numValidSigs, sigsDict, 0)

		verifyArgsDictRandomized = sigsDict

		verifyFuncArgs = list(verifyArgsDictRandomized[0].keys())

		bID1 = InitBenchmark()

		StartBenchmark(bID1, [RealTime])
		incorrectSigIndices = run_Ind(verifyArgsDictRandomized, groupParamArg, verifyFuncArgs)
		EndBenchmark(bID1)

		if (incorrectSigIndices != []):
			sys.exit("Individual failed.")

		result = (GetBenchmark(bID1, RealTime) / trials) * time_in_ms



here
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
