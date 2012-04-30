import sys, time
from AutoBatch_CodeGen_FOR_TIMING_MSMTS import *

schemeNames = ["Boyen", "ChCh_Hess", "VRF", "CL", "HW_Single", "HW_Different", "Waters09"]
extension = ".dat"
numIterations = 100
numArgsToCodegen = 6
time_in_ms = 1000

def buildSchemesDetails():
	schemesDetails = {}

	for schemeName in schemeNames:
		schemesDetails[schemeName] = {}

	schemesDetails["Boyen"][0] = "BOYEN/pksig_boyen.py.ORIGINAL.py"
	schemesDetails["Boyen"][1] = "BOYEN/batchOutputBoyen"
	schemesDetails["Boyen"][2] = "garbageValue"
	schemesDetails["Boyen"][3] = "ARCHIVE/boyenIND.py"
	schemesDetails["Boyen"][4] = "ARCHIVE/boyenBAT.py"
	schemesDetails["Boyen"][5] = "ARCHIVE/boyenVER.py"

	schemesDetails["ChCh_Hess"][0] = "CHCH_HESS/pksig_case21.py"
	schemesDetails["ChCh_Hess"][1] = "CHCH_HESS/batchOutput"
	schemesDetails["ChCh_Hess"][2] = "garbageValue"
	schemesDetails["ChCh_Hess"][3] = "ARCHIVE/chchhessIND.py"
	schemesDetails["ChCh_Hess"][4] = "ARCHIVE/chchhessBAT.py"
	schemesDetails["ChCh_Hess"][5] = "ARCHIVE/chchhessVER.py"

	schemesDetails["VRF"][0] = "VRF/pk_vrf.py"
	schemesDetails["VRF"][1] = "VRF/batchOutput"
	schemesDetails["VRF"][2] = "garbageValue"
	schemesDetails["VRF"][3] = "ARCHIVE/vrfIND.py"
	schemesDetails["VRF"][4] = "ARCHIVE/vrfBAT.py"
	schemesDetails["VRF"][5] = "ARCHIVE/vrfVER.py"

	schemesDetails["CL"][0] = "CL/pksig_cl04.py"
	schemesDetails["CL"][1] = "CL/batchOutput"
	schemesDetails["CL"][2] = "garbageValue"
	schemesDetails["CL"][3] = "ARCHIVE/clIND.py"
	schemesDetails["CL"][4] = "ARCHIVE/clBAT.py"
	schemesDetails["CL"][5] = "ARCHIVE/clVER.py"

	schemesDetails["HW_Different"][0] = "HW_DIFF/pksig_hw.py"
	schemesDetails["HW_Different"][1] = "HW_DIFF/batchOutput"
	schemesDetails["HW_Different"][2] = "garbageValue"
	schemesDetails["HW_Different"][3] = "ARCHIVE/hwdiffIND.py"
	schemesDetails["HW_Different"][4] = "ARCHIVE/hwdiffBAT.py"
	schemesDetails["HW_Different"][5] = "ARCHIVE/hwdiffVER.py"

	schemesDetails["Waters09"][0] = "WATERS09/pksig_waters09_mod.py"
	schemesDetails["Waters09"][1] = "WATERS09/batchOutput"
	schemesDetails["Waters09"][2] = "garbageValue"
	schemesDetails["Waters09"][3] = "ARCHIVE/waters09IND.py"
	schemesDetails["Waters09"][4] = "ARCHIVE/waters09BAT.py"
	schemesDetails["Waters09"][5] = "ARCHIVE/waters09VER.py"

	return schemesDetails

def processOneIteration(argsDict):
	startTime = time.clock()
	mainFunctionForTimings(argsDict[0], argsDict[1], argsDict[2], argsDict[3], argsDict[4], argsDict[5])
	endTime = time.clock()

	result = (endTime - startTime) * time_in_ms

	outputString = ""
	outputString += str(result) + ","
	return outputString

def processIndScheme(prefixName, schemeName, schemesDetails):
	outputFile = open(prefixName + "_" + schemeName + extension, 'w')
	outputString = ""

	argsDict = {}
	for index in range(0, numArgsToCodegen):
		argsDict[index] = schemesDetails[schemeName][index]

	for iteration in range(0, numIterations):
		outputString += processOneIteration(argsDict)

	outputFile.write(outputString)
	outputFile.close()
	del outputFile

def main(prefixName):
	schemesDetails = buildSchemesDetails()

	for schemeName in schemeNames:
		if (schemeName != "HW_Single"):
			processIndScheme(prefixName, schemeName, schemesDetails)

if __name__ == '__main__':
	if ( (len(sys.argv) != 2) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  " + str(sys.argv[0]) + " [PREFIX OF OUTPUT FILES]")

	main(sys.argv[1])
