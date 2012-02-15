from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy, random, time
from batNEW import run_Batch
from indNEW import run_Ind

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
NUM_CYCLES = 75
MS_PER_BUCKET = 100

#SPS_FOR_INDIVIDUAL = 65
PERCENT_INVALID_THRESHOLD = 0.15

NUM_PROGRAM_ITERATIONS = 10

numBuckets = (NUM_CYCLES * MS_PER_CYCLE) / MS_PER_BUCKET

def areListsEqual(list1, list2):
	len1 = len(list1)
	len2 = len(list2)

	if (len1 != len2):
		return False

	for index in range(0, len1):
		if ( (list1[index]) != (list2[index]) ):
			return False

	return True

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

def updateBucketList(bucketList, startTime, duration, value):
	endTime = startTime + duration

	for bucketIndex in range(0, int(numBuckets)):
		bucketStartTime = float(bucketIndex) * float(MS_PER_BUCKET)
		bucketEndTime = float(bucketStartTime) + float(MS_PER_BUCKET)

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

def printBucketListsToStrings(bucketListSigsPerSecABOVE, bucketListSigsPerSecBELOW, bucketListInvalidSigs):

	outputStringABOVE = ""
	outputStringBELOW = ""
	outputInvalidSigsString = ""

	for bucketIndex in range(0, int(numBuckets)):
		currentValue = bucketListSigsPerSecABOVE[bucketIndex]
		bucketListSigsPerSecABOVE[bucketIndex] = float(currentValue) / float(NUM_PROGRAM_ITERATIONS)
		timePeriod = (bucketIndex * MS_PER_BUCKET) + (MS_PER_BUCKET / 2)
		valueToWrite = bucketListSigsPerSecABOVE[bucketIndex]
		outputStringABOVE += str(timePeriod) + " " + str(valueToWrite) + "\n"

		currentValue = bucketListSigsPerSecBELOW[bucketIndex]
		bucketListSigsPerSecBELOW[bucketIndex] = float(currentValue) / float(NUM_PROGRAM_ITERATIONS)
		timePeriod = (bucketIndex * MS_PER_BUCKET) + (MS_PER_BUCKET / 2)
		valueToWrite = bucketListSigsPerSecBELOW[bucketIndex]
		outputStringBELOW += str(timePeriod) + " " + str(valueToWrite) + "\n"

		currentValue = bucketListInvalidSigs[bucketIndex]
		bucketListInvalidSigs[bucketIndex] = float(currentValue) / float(NUM_PROGRAM_ITERATIONS)
		timePeriod = (bucketIndex * MS_PER_BUCKET) + (MS_PER_BUCKET / 2)
		valueToWrite = bucketListInvalidSigs[bucketIndex]
		outputInvalidSigsString += str(timePeriod) + " " + str(valueToWrite) + "\n"

	return (outputStringABOVE, outputStringBELOW, outputInvalidSigsString)

if __name__ == '__main__':
	if ( (len(sys.argv) != 8) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + sys.argv[0] + "\n\t[dictionary with valid messages/signatures]\n\t[dictionary with invalid messages/signatures]\n\t[path and filename of invalid sig distribution]\n\t[path and filename of group param file]\n\t[name of output file for SIGS PER SEC for above IND]\n\t[name of output file for % invalid sigs]\n\t[name of output file for SIGS PERSEC for below IND]\n")

	validDictArg = open(sys.argv[1], 'rb').read()
	invalidDictArg = open(sys.argv[2], 'rb').read()
	invalidSigDistro = open(sys.argv[3], 'r').readlines()
	groupParamArg = PairingGroup(MNT160)
	outputFileNameABOVE = sys.argv[5]
	outputInvalidSigsFile = sys.argv[6]
	outputFileNameBELOW = sys.argv[7]

	validDictFile = bytesToObject(validDictArg, groupParamArg)
	invalidDictFile = bytesToObject(invalidDictArg, groupParamArg)

	validDict = loadDictDataFromFile(validDictFile, groupParamArg)
	invalidDict = loadDictDataFromFile(invalidDictFile, groupParamArg)

	lastValidSigNum = 0
	lastInvalidSigNum = 0

	bucketListSigsPerSecABOVE = []
	bucketListSigsPerSecBELOW = []
	bucketListInvalidSigs = []

	for bucketIndex in range(0, int(numBuckets)):
		bucketListSigsPerSecABOVE.append(0)
		bucketListSigsPerSecBELOW.append(0)
		bucketListInvalidSigs.append(0)

	for programIteration in range(0, NUM_PROGRAM_ITERATIONS):
		print(programIteration)

		lastValidSigNum = 0
		lastInvalidSigNum = 0
		SIGS_PER_CYCLE = 750
		TIMER = 0
		INVALID_SIGNATURE_FRACTION = 0
		useBatch = True

		for cycle in range(0, NUM_CYCLES):

			print("cycle ", cycle)
			sigsDict = {}
			probInvalid = float(invalidSigDistro[cycle])

			endCounter = 0
			realIncorrectSigIndices = []

			numInvalidSigs = int(SIGS_PER_CYCLE * probInvalid)
			numValidSigs = SIGS_PER_CYCLE - numInvalidSigs

			endCounter = loadDataFromDictInMemory(validDict, lastValidSigNum, numValidSigs, sigsDict, endCounter)
			lastValidSigNum += numValidSigs
			endCounter += 1

			endCounter = loadDataFromDictInMemory(invalidDict, lastInvalidSigNum, numInvalidSigs, sigsDict, endCounter, realIncorrectSigIndices)
			lastInvalidSigNum += numInvalidSigs
			endCounter += 1

			TOTAL_SIGS = numValidSigs + numInvalidSigs

			if (TOTAL_SIGS != SIGS_PER_CYCLE):
				sys.exit("TOTAL_SIGS != SIGS_PER_CYCLE")

			if (len(sigsDict) != SIGS_PER_CYCLE):
				sys.exit("len(sigsDict) != SIGS_PER_CYCLE")

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

			if (useBatch == True):
				startTime = time.clock()
				incorrectSigIndices = run_Batch(verifyArgsDictRandomized, groupParamArg, verifyFuncArgs, False)
				endTime = time.clock()
			else:
				startTime = time.clock()
				incorrectSigIndices = run_Ind(verifyArgsDictRandomized, groupParamArg, verifyFuncArgs)
				endTime = time.clock()

			result = ( (endTime - startTime) / trials) * time_in_ms

			TIMER += result
			TOTAL_SIGS = float(numValidSigs + numInvalidSigs)
			SIGS_PER_SECOND = float ( (TOTAL_SIGS * 1000.0) / (float(result)) )

			updateBucketList(bucketListSigsPerSecABOVE, (TIMER - result), result, SIGS_PER_SECOND)

			if (useBatch == False):
				startTime_Batch = time.clock()
				incorrectSigIndices_Batch = run_Batch(verifyArgsDictRandomized, groupParamArg, verifyFuncArgs, False)
				endTime_Batch = time.clock()

				result_Batch = ( (endTime_Batch - startTime_Batch) / trials) * time_in_ms

				SIGS_PER_SECOND_BATCH = float ( (TOTAL_SIGS * 1000.0) / (float(result_Batch)) )

				updateBucketList(bucketListSigsPerSecBELOW, (TIMER - result), result, SIGS_PER_SECOND_BATCH)

			percentInvalid = (float(numInvalidSigs) / float(TOTAL_SIGS))

			if (percentInvalid < PERCENT_INVALID_THRESHOLD):
				useBatch = True
			else:
				useBatch = False

			updateBucketList(bucketListInvalidSigs, (TIMER - result), result, percentInvalid)

			randomizedIncorrectSigIndices.sort()
			incorrectSigIndices.sort()

			print(randomizedIncorrectSigIndices)
			print(incorrectSigIndices)
			print("\n\n")

			if (areListsEqual(randomizedIncorrectSigIndices, incorrectSigIndices) == False):
				sys.exit("Error:  wrong results returned for which signatures are invalid.")

			if (len(incorrectSigIndices) != numInvalidSigs):
				sys.exit("Error:  wrong number of invalid signatures returned.")

			SIGS_PER_CYCLE = int( ( float(MS_PER_CYCLE) / float(result) ) * SIGS_PER_CYCLE )
			if (SIGS_PER_CYCLE == 0):
				SIGS_PER_CYCLE = 1

			INVALID_SIGNATURE_FRACTION = float(numInvalidSigs) / float(TOTAL_SIGS)

			del sigsDict
			del randomizedIndices
			del verifyArgsDictRandomized
			del incorrectSigIndices
			del realIncorrectSigIndices
			del randomizedIncorrectSigIndices
			del verifyFuncArgs

	(outputStringABOVE, outputStringBELOW, outputInvalidSigsString) = printBucketListsToStrings(bucketListSigsPerSecABOVE, bucketListSigsPerSecBELOW, bucketListInvalidSigs)

	outputFileABOVE = open(outputFileNameABOVE, 'w')
	outputFileABOVE.write(outputStringABOVE)
	outputFileABOVE.close()
	del outputFileABOVE

	outputFileBELOW = open(outputFileNameBELOW, 'w')
	outputFileBELOW.write(outputStringBELOW)
	outputFileBELOW.close()
	del outputFileBELOW

	outputInvalidSigs = open(outputInvalidSigsFile, 'w')
	outputInvalidSigs.write(outputInvalidSigsString)
	outputInvalidSigs.close()
	del outputInvalidSigs
