import sys

numIterations = 100
numSignatures = 100

runningTimesPrefix = "timing_autobatch/dontDelete_"
runningTimesSuffix = ".dat"
runningTimeSchemes = ["BBS", "BLS", "Boyen", "CHCH", "ChCh_Hess", "CHP", "CL", "CYH", "HESS", "HW_Different", "VRF", "WATERS", "Waters09"]
runningTimeTypes = ["batcher", "codegen"]

benchmarkPrefix = "CCS2012_Benchmarks_"
benchmarkSuffix = ".dat"
benchmarkTypes = ["bat", "ind"]
#benchmarkSchemes = ["BOYEN", "CHCH_HESS", "CL", "CDH/CDH", "HW_DIFF", "VRF", "WATERS09"]
benchmarkSchemes = ["BOYEN", "CHCH_HESS", "CL", "CDH/CDH", "HW_DIFF"]

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

def getRunningTimesOutput(runningInNames):
	retDict = {}

	return retDict

def main(prefixName):
	(runningInNames, benchmarkInNames) = buildIOFileNames()
	runningTimesOutputDict = getRunningTimesOutput(runningInNames)

if __name__ == '__main__':
	if ( (len(sys.argv) != 2) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  python " + str(sys.argv[0]) + " [PREFIX OF OUTPUT FILES]")

	main(sys.argv[1])
