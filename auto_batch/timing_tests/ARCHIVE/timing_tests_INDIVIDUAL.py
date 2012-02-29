from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy, random
from bat_bls import runBLS_Batch
from ind_bls import runBLS_Ind

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
NUM_CYCLES = 20
MS_PER_BUCKET = 100
NUM_PROGRAM_ITERATIONS = 5
numBuckets = (NUM_CYCLES * MS_PER_CYCLE) / MS_PER_BUCKET

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


				#print(verifyParamFile)
				#print(verifyArgsDict[sigIndex][arg][bodyKey])
				#print("\n")




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

def updateBucketList(bucketList, startTime, duration, value):

	#print("Start time:  ", startTime)
	#print("Duration:  ", duration)
	#print("Value:  ", value)

	endTime = startTime + duration

	for bucketIndex in range(0, int(numBuckets)):
		bucketStartTime = float(bucketIndex) * float(MS_PER_BUCKET)
		bucketEndTime = float(bucketStartTime) + float(MS_PER_BUCKET)

		#print(startTime)
		#print(endTime)
		#print(bucketStartTime)
		#print(bucketEndTime)

		if (endTime <= bucketStartTime):
			continue
		if (startTime >= bucketEndTime):
			continue
		if ( (startTime <= bucketStartTime) and (endTime >= bucketEndTime) ):
			bucketList[bucketIndex] += value
			continue
		if ( (startTime > bucketStartTime) and (endTime < bucketEndTime) ):
			fractionOfBucketOccupied = float(duration) / float(MS_PER_BUCKET)
			if (fractionOfBucketOccupied >= 1):
				sys.exit("Bucket fraction error")
			bucketList[bucketIndex] += (fractionOfBucketOccupied * float(value))
			continue
		if ( (startTime <= bucketStartTime) and (endTime < bucketEndTime) ):
			fractionOfBucketOccupied = float(endTime - bucketStartTime) / float(MS_PER_BUCKET)
			bucketList[bucketIndex] += (fractionOfBucketOccupied * float(value))
			continue
		if ( (startTime > bucketStartTime) and (endTime >= bucketEndTime) ):
			fractionOfBucketOccupied = float(bucketEndTime - startTime) / float(MS_PER_BUCKET)
			bucketList[bucketIndex] += (fractionOfBucketOccupied * float(value))
			continue
		sys.exit("Problem with bucket logic")

def printBucketListsToStrings(bucketListSigsPerSec, bucketListInvalidSigs):

	outputString = ""
	outputInvalidSigsString = ""

	for bucketIndex in range(0, int(numBuckets)):
		currentValue = bucketListSigsPerSec[bucketIndex]
		bucketListSigsPerSec[bucketIndex] = float(currentValue) / float(NUM_PROGRAM_ITERATIONS)
		timePeriod = (bucketIndex * MS_PER_BUCKET) + (MS_PER_BUCKET / 2)
		valueToWrite = bucketListSigsPerSec[bucketIndex]
		outputString += str(timePeriod) + " " + str(valueToWrite) + "\n"


		currentValue = bucketListInvalidSigs[bucketIndex]
		bucketListInvalidSigs[bucketIndex] = float(currentValue) / float(NUM_PROGRAM_ITERATIONS)
		timePeriod = (bucketIndex * MS_PER_BUCKET) + (MS_PER_BUCKET / 2)
		valueToWrite = bucketListInvalidSigs[bucketIndex]
		outputInvalidSigsString += str(timePeriod) + " " + str(valueToWrite) + "\n"

	return (outputString, outputInvalidSigsString)

if __name__ == '__main__':
	if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + sys.argv[0] + "\n\t[dictionary with valid messages/signatures]\n\t[dictionary with invalid messages/signatures]\n\t[path and filename of invalid sig distribution]\n\t[path and filename of group param file]\n\t[name of output file for SIGS PER SEC]\n\t[name of output file for % invalid sigs]")

	validDictArg = open(sys.argv[1], 'rb').read()
	invalidDictArg = open(sys.argv[2], 'rb').read()
	invalidSigDistro = open(sys.argv[3], 'r').readlines()
	groupParamArg = PairingGroup(int(sys.argv[4]))
	outputFileName = sys.argv[5]
	outputInvalidSigsFile = sys.argv[6]

	validDictFile = deserializeDict( unpickleObject(validDictArg), groupParamArg )
	invalidDictFile = deserializeDict( unpickleObject(invalidDictArg), groupParamArg )

	validDict = loadDictDataFromFile(validDictFile, groupParamArg)
	invalidDict = loadDictDataFromFile(invalidDictFile, groupParamArg)

	lastValidSigNum = 0
	lastInvalidSigNum = 0

	#outputString = ""
	#outputInvalidSigsString = ""

	bucketListSigsPerSec = []
	bucketListInvalidSigs = []

	for bucketIndex in range(0, int(numBuckets)):
		bucketListSigsPerSec.append(0)
		bucketListInvalidSigs.append(0)

	for programIteration in range(0, NUM_PROGRAM_ITERATIONS):
		print(programIteration)

		lastValidSigNum = 0
		lastInvalidSigNum = 0
		SIGS_PER_CYCLE = 750
		TIMER = 0

		for cycle in range(0, NUM_CYCLES):

			print("cycle ", cycle)
			sigsDict = {}
			probInvalid = float(invalidSigDistro[cycle])

			endCounter = 0
			numValidSigs = 0
			numInvalidSigs = 0
			realIncorrectSigIndices = []

			for getSigCounter in range(0, SIGS_PER_CYCLE):
				randFloat = random.random()
				if (randFloat >= probInvalid):
					endCounter = loadDataFromDictInMemory(validDict, lastValidSigNum, 1, sigsDict, endCounter)
					lastValidSigNum += 1
					endCounter += 1
					numValidSigs += 1
				else:
					endCounter = loadDataFromDictInMemory(invalidDict, lastInvalidSigNum, 1, sigsDict, endCounter, realIncorrectSigIndices)
					lastInvalidSigNum += 1
					endCounter += 1
					numInvalidSigs += 1

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

			verifyFuncArgs = list(verifyArgsDictRandomized[0].keys())

			bID1 = InitBenchmark()

			StartBenchmark(bID1, [RealTime])
			incorrectSigIndices = runBLS_Ind(verifyArgsDictRandomized, groupParamArg, verifyFuncArgs)
			EndBenchmark(bID1)

			result = (GetBenchmark(bID1, RealTime) / trials) * time_in_ms

			TIMER += result
			TOTAL_SIGS = float(numValidSigs + numInvalidSigs)
			SIGS_PER_SECOND = float ( (TOTAL_SIGS * 1000.0) / (float(result)) )

			#outputString += str(TIMER) + " " + str(SIGS_PER_SECOND) + "\n"

			updateBucketList(bucketListSigsPerSec, (TIMER - result), result, SIGS_PER_SECOND)

			percentInvalid = (float(numInvalidSigs) / TOTAL_SIGS)

			#outputInvalidSigsString += str(TIMER) + " " + str(percentInvalid) + "\n"

			updateBucketList(bucketListInvalidSigs, (TIMER - result), result, percentInvalid)

			if ( (randomizedIncorrectSigIndices.sort()) != (incorrectSigIndices.sort()) ):
				sys.exit("Error:  batch code returned wrong results for which signatures are invalid.")

			if (len(incorrectSigIndices) != numInvalidSigs):
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
			del verifyFuncArgs

	(outputString, outputInvalidSigsString) = printBucketListsToStrings(bucketListSigsPerSec, bucketListInvalidSigs)

	outputFile = open(outputFileName, 'w')
	outputFile.write(outputString)
	outputFile.close()
	del outputFile

	outputInvalidSigs = open(outputInvalidSigsFile, 'w')
	outputInvalidSigs.write(outputInvalidSigsString)
	outputInvalidSigs.close()
	del outputInvalidSigs
