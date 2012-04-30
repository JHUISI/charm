from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy, random, time
from bat import run_Batch
from ind import run_Ind

sigNumKey = 'Signature_Number'
bodyKey = 'Body'
charmPickleSuffix = '.charmPickle'
pythonPickleSuffix = '.pythonPickle'
repeatSuffix = '.repeat'
lenRepeatSuffix = len(repeatSuffix)

trials = 1
time_in_ms = 1000
NUM_PROGRAM_ITERATIONS = 30
NUM_CYCLES = 100

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

def getResults(resultsDict):
	resultsString = ""

	for cycle in range(0, NUM_CYCLES):
		value = 0.0

		for programIteration in range(0, NUM_PROGRAM_ITERATIONS):
			value += resultsDict[programIteration][cycle]

		value = float(value) / float(NUM_PROGRAM_ITERATIONS)

		resultsString += str(cycle+1) + " " + str(value) + "\n"

	return resultsString

if __name__ == '__main__':
	if ( (len(sys.argv) != 5) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + sys.argv[0] + "\n\t[dictionary with valid messages/signatures]\n\t[group param int]\n\t[name of output file for batch results]\n\t[name of output file for ind. results]")

	validDictArg = open(sys.argv[1], 'rb').read()
	groupParamArg = PairingGroup(MNT160)
	batchResultsFile = sys.argv[3]
	indResultsFile = sys.argv[4]

	validDictFile = bytesToObject(validDictArg, groupParamArg)
	validDict = loadDictDataFromFile(validDictFile, groupParamArg)

	batchResultsTimes = {}
	indResultsTimes = {}

	for initIndex in range(0, NUM_PROGRAM_ITERATIONS):
		batchResultsTimes[initIndex] = {}
		indResultsTimes[initIndex] = {}

	batchOutputFile = open(batchResultsFile, 'w')
	indOutputFile = open(indResultsFile, 'w')

	for programIteration in range(0, NUM_PROGRAM_ITERATIONS):

		#print("program iteration ", programIteration)

		for cycle in range(0, NUM_CYCLES):

			#print("\tcycle number ", cycle)

			sigsDict = {}
			loadDataFromDictInMemory(validDict, 0, (cycle+1), sigsDict, 0)
			verifyFuncArgs = list(sigsDict[0].keys())

			startTime = time.clock()
			incorrectSigIndices = run_Batch(sigsDict, groupParamArg, verifyFuncArgs)
			endTime = time.clock()

			result = (endTime - startTime) * time_in_ms

			if (incorrectSigIndices != []):
				print(incorrectSigIndices)
				sys.exit("Batch verification returned invalid signatures.")

			batchResultsTimes = ( float(result) / float(cycle+1) )
			currentBatchOutputString = str(batchResultsTimes) + ","
			batchOutputFile.write(currentBatchOutputString)

			startTime = time.clock()
			incorrectSigIndices = run_Ind(sigsDict, groupParamArg, verifyFuncArgs)
			endTime = time.clock()

			result = (endTime - startTime) * time_in_ms

			if (incorrectSigIndices != []):
				sys.exit("Ind. verification returned invalid signatures.")

			indResultsTimes = ( float(result) / float(cycle+1) )
			currentIndOutputString = str(indResultsTimes) + ","
			indOutputFile.write(currentIndOutputString)

		batchOutputFile.write("\n")
		indOutputFile.write("\n")

	batchOutputFile.close()
	indOutputFile.close()
