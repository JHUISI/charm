import sys, numpy

numIterations = 100
numSignatures = 100

runningTimesPrefix = "timing_autobatch/dontDelete_"
runningTimesSuffix = ".dat"
runningTimeSchemes = ["BBS", "BLS", "Boyen", "CHCH", "ChCh_Hess", "CHP", "CL", "CYH", "HESS", "HW_Different", "VRF", "WATERS", "Waters09"]
runningTimeTypes = ["batcher", "codegen"]

runningTimesOutputFileSuffix = "_Running_Times"
benchmarksOutputFileSuffix = "_Benchmarks_"

benchmarkPrefix = "CCS2012_Benchmarks_"
benchmarkSuffix = ".dat"
benchmarkTypes = ["bat", "ind"]
benchmarkSchemes = ["BOYEN", "CHCH_HESS", "CL", "CDH/CDH", "HW_DIFF", "VRF", "WATERS09"]

inputDelimiter = ","
outputDelimiter = " : "

def buildIOFileNames():
	runningInNames = {}
	benchmarkInNames = {}

	for scheme in runningTimeSchemes:
		runningInNames[scheme] = {}
		for type in runningTimeTypes:
			runningInNames[scheme][type] = runningTimesPrefix + scheme + "_" + type + runningTimesSuffix

	for scheme in benchmarkSchemes:
		benchmarkInNames[scheme] = {}
		for type in benchmarkTypes:
			benchmarkInNames[scheme][type] = scheme + "/" + benchmarkPrefix + type + benchmarkSuffix

	return (runningInNames, benchmarkInNames)

def getBenchmarksOutput(benchmarkInNames, prefixName):
	for scheme in benchmarkInNames:
		for type in benchmarkInNames[scheme]:
			processOneSchemeType_Benchmarks(benchmarkInNames, prefixName, scheme, type)

def processInputLineSplit(inputLineSplit, scheme, type, lineNumberInFile):
	if (len(inputLineSplit) != (numIterations + 1) ):
		print("num iterations made through:  ", str(len(inputLineSplit)))
		print(scheme)
		print(type)
		print("line No:  ", str(lineNumberInFile))
		sys.exit("processInputLineSplit:  problem with length of input.")

	lastValue = inputLineSplit.pop()
	if (lastValue != '\n'):
		sys.exit("processInputLineSplit:  problem with last value.")

	retList = []
	for currentInput in inputLineSplit:
		retList.append(float(currentInput))

	if (len(retList) != numIterations):
		sys.exit("processInputLineSplit:  len(retList) != numIterations.")

	return retList

def processOneSchemeType_Benchmarks(benchmarkInNames, prefixName, scheme, type):
	inputFileName = benchmarkInNames[scheme][type]
	inputFile = open(inputFileName, 'r').readlines()
	if (len(inputFile) < numIterations):
		sys.exit("getBenchmarksOutput:  # of lines read in for one of the files was less than numIterations.")

	reverseNos = {}
	for reverseNosIndex in range(1, 101):
		reverseNos[reverseNosIndex] = []

	counter = 0
	for line in inputFile:
		counter += 1
		if (counter > numIterations):
			break
		inputLineSplit = line.split(inputDelimiter)
		floatsList = processInputLineSplit(inputLineSplit, scheme, type, counter)
		msmtsCounter = 0
		for msmt in floatsList:
			msmtsCounter += 1
			reverseNos[msmtsCounter].append(msmt)
		if (msmtsCounter != numIterations):
			sys.exit("getBenchmarksOutput:  msmtsCounter probs.")

	if ( (counter != numIterations) and (counter != (numIterations + 1)) ):
		sys.exit("getBenchmarksOutput:  bad counter number at end of loop.")

	if (scheme != "CDH/CDH"):
		outputFile = open(prefixName + scheme + "_" + type + benchmarkSuffix, 'w')
	else:
		outputFile = open(prefixName + "CDH_" + type + benchmarkSuffix, 'w')

	outputString = ""

	for counter in range(1, (numIterations + 1)):
		outputString += str(counter) + " "
		if (len(reverseNos[counter]) != numIterations):
			sys.exit("getBenchmarksOutput:  probs with reverseNos length.")

		outputString += str(numpy.mean(reverseNos[counter], dtype=numpy.float64)) + " "
		outputString += str(numpy.std(reverseNos[counter], dtype=numpy.float64)) + "\n"

	outputFile.write(outputString)
	outputFile.close()

def getRunningTimesOutput(runningInNames, prefixName):
	outputFile = open(prefixName + runningTimesOutputFileSuffix + runningTimesSuffix, 'w')
	outputString = ""

	for scheme in runningInNames:
		for type in runningInNames[scheme]:
			inputFileName = runningInNames[scheme][type]
			inputFile = open(inputFileName, 'r').readlines()
			if (len(inputFile) != 1):
				sys.exit("One of the running time input files did not have only one line.")

			inputSplit = inputFile[0].split(inputDelimiter)
			if (len(inputSplit) != (numIterations + 1) ):
				sys.exit("One of the running time input files did not have numIterations+1 split entries.")

			lastValue = inputSplit.pop()
			if (lastValue != ""):
				sys.exit("One of the running time input files had a last element that was non-NULL.")

			inputAsFloats = []
			for currentInput in inputSplit:
				inputAsFloats.append(float(currentInput))

			if (len(inputAsFloats) != numIterations):
				sys.exit("inputAsFloats for running times was not of length numIterations.")

			outputString += scheme + outputDelimiter + type + outputDelimiter + str(numpy.mean(inputAsFloats, dtype=numpy.float64)) + outputDelimiter + str(numpy.std(inputAsFloats, dtype=numpy.float64)) + "\n"

	outputFile.write(outputString)
	outputFile.close()

def main(prefixName):
	(runningInNames, benchmarkInNames) = buildIOFileNames()
	#getRunningTimesOutput(runningInNames, prefixName)
	getBenchmarksOutput(benchmarkInNames, prefixName)

if __name__ == '__main__':
	if ( (len(sys.argv) != 2) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + str(sys.argv[0]) + " [PREFIX OF OUTPUT FILES]")

	main(sys.argv[1])
