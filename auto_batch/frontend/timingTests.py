from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy, random
from bat_cyh import run_Batch
from ind_cyh import run_Ind

sigNumKey = 'Signature_Number'
bodyKey = 'Body'
charmPickleSuffix = '.charmPickle'
pythonPickleSuffix = '.pythonPickle'
repeatSuffix = '.repeat'
lenRepeatSuffix = len(repeatSuffix)

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
	if ( (len(sys.argv) != 4) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + sys.argv[0] + "\n\t[dictionary with valid messages/signatures]\n\t[dictionary with invalid messages/signatures]\n\t[path and filename of group param file]\n")

	validDictArg = open(sys.argv[1], 'rb').read()
	invalidDictArg = open(sys.argv[2], 'rb').read()
	groupParamArg = PairingGroup(sys.argv[3])

	validDictFile = deserializeDict( unpickleObject(validDictArg), groupParamArg )
	invalidDictFile = deserializeDict( unpickleObject(invalidDictArg), groupParamArg )

	validDict = loadDictDataFromFile(validDictFile, groupParamArg)
	invalidDict = loadDictDataFromFile(invalidDictFile, groupParamArg)

	sigsDict = {}
	probInvalid = 0.5
	realIncorrectSigIndices = []

	loadDataFromDictInMemory(validDict, 0, 10, sigsDict, 0)
	loadDataFromDictInMemory(invalidDict, 0, 10, sigsDict, 10, realIncorrectSigIndices)
			
	preRandomizedIndices = []
	for randomIndex in range(0, 20):
		preRandomizedIndices.append(randomIndex)

	randomizedIndices = shuffle(preRandomizedIndices)

	if (preRandomizedIndices != []):
		sys.exit("Problems with randomly shuffling the valid and invalid signatures.")

	verifyArgsDictRandomized = {}
	randomizedIncorrectSigIndices = []

	for sigIndex in range(0, 20):
		verifyArgsDictRandomized[sigIndex] = sigsDict[randomizedIndices[sigIndex]]
		if (randomizedIndices[sigIndex] in realIncorrectSigIndices):
			randomizedIncorrectSigIndices.append(sigIndex)

	randomizedIncorrectSigIndices.sort()

	print(randomizedIncorrectSigIndices)

	verifyFuncArgs = list(verifyArgsDictRandomized[0].keys())

	incorrectSigIndices = run_Batch(verifyArgsDictRandomized, groupParamArg, verifyFuncArgs)
	incorrectSigIndices.sort()

	print(incorrectSigIndices)

	'''
	if (areListsEqual(randomizedIncorrectSigIndices, incorrectSigIndices) == False):
		sys.exit("Error:  batch code returned wrong results for which signatures are invalid.")

	if (len(incorrectSigIndices) != 10):
		sys.exit("Error:  batch code returned wrong results for number of invalid signatures.")
	'''

	del incorrectSigIndices

	incorrectSigIndices = run_Ind(verifyArgsDictRandomized, groupParamArg, verifyFuncArgs)
	incorrectSigIndices.sort()

	print(incorrectSigIndices)

	if (areListsEqual(randomizedIncorrectSigIndices, incorrectSigIndices) == False):
		sys.exit("Error:  ind code returned wrong results for which signatures are invalid.")

	if (len(incorrectSigIndices) != 10):
		sys.exit("Error:  ind code returned wrong results for number of invalid signatures.")
