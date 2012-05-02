import sys, numpy

numIterations = 200
numSignatures = 100

runningTimesPrefix = "timing_autobatch/dontDelete_"
runningTimesSuffix = ".dat"
runningTimeSchemes = ["BBS", "BLS", "Boyen", "CHCH", "ChCh_Hess", "CHP", "CL", "CYH", "HESS", "HW_Different", "VRF", "WATERS", "Waters09"]
runningTimeTypes = ["batcher", "codegen"]

runningTimesOutputFileSuffix = "_Running_Times"

benchmarkPrefix = "CCS2012_Benchmarks_"
benchmarkSuffix = ".dat"
benchmarkTypes = ["bat", "ind"]
#benchmarkSchemes = ["BOYEN", "CHCH_HESS", "CL", "CDH/CDH", "HW_DIFF", "VRF", "WATERS09"]
benchmarkSchemes = ["BOYEN", "CHCH_HESS", "CL", "CDH/CDH", "HW_DIFF"]

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
	runningTimesOutputDict = getRunningTimesOutput(runningInNames, prefixName)

if __name__ == '__main__':
	if ( (len(sys.argv) != 2) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + str(sys.argv[0]) + " [PREFIX OF OUTPUT FILES]")

	main(sys.argv[1])
