import sys, time
from AutoBatch_CodeGen_FOR_TIMING_MSMTS import *

schemeNames = ["Boyen", "ChCh_Hess", "VRF", "CL", "HW_Single", "HW_Different", "Waters09"]
extension = ".dat"
numIterations = 100

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

	schemesDetails["HW_Different"][0] = "HW_DIFF/

	return schemesDetails

def processOneIteration(schemeName, schemesDetails):
	dddddd

def processIndScheme(prefixName, schemeName, schemesDetails):
	outputFile = open(prefixName + "_" + schemeName + extension, 'w')
	outputString = ""

	for iteration in numIterations:
		outputString += processOneIteration(schemeName, schemesDetails)

	outputFile.write(outputString)
	outputFile.close()
	del outputFile

def main(prefixName):
	schemesDetails = buildSchemesDetails()

	for schemeName in schemeNames:
		processIndScheme(prefixName, schemeName, schemesDetails)

if __name__ == '__main__':
	if ( (len(sys.argv) != 2) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  " + str(sys.argv[0]) + " [PREFIX OF OUTPUT FILES]")

	main(sys.argv[1])
