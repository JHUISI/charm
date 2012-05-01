import sys, time
from AutoBatch_Batcher import *
from AutoBatch_CodeGen_FOR_TIMING_MSMTS import *

# NOTE: CHP, HESS, CHCH, WATERS05, CYH and BBS give this error: "SubscriptName->setValue: value passed in is of None type."
schemeNames = ["BLS", "Boyen", "ChCh_Hess", "VRF", "CL", "HW_Single", "HW_Different", "Waters09", "CHP", "HESS", "CHCH", "WATERS", "CYH", "BBS"]
extensionCG = "codegen.dat"
extensionBT = "batcher.dat"
numIterations = 1 #100
numArgsToCodegen = 6
time_in_ms = 1000

def buildSchemesDetails():
	schemesDetails = {}

	for schemeName in schemeNames:
		schemesDetails[schemeName] = {}

	# Bls
	schemesDetails["BLS"]["codegen"] = ["BLS/pksig_bls04.py", "BLS/batchOutput_BLS", "garbageValue", "tmp/blsIND.py", "tmp/blsBAT.py", "tmp/blsIND.py"] 
	schemesDetails["BLS"]["batcher"] = ["batchverify.py", "../tests/bls.bv", "-b", "-c", "-p"]

	# Chp
	schemesDetails["CHP"]["codegen"] = ["CHP/pksig_chp.py", "CHP/batchOutputCHP", "garbageValue", "tmp/chpIND.py", "tmp/chpBAT.py", "tmp/chpIND.py"] 
	schemesDetails["CHP"]["batcher"] = ["batchverify.py", "../tests/chp.bv", "-b", "-c", "-p"]

	# Hess
	schemesDetails["HESS"]["codegen"] = ["HESS/pksig_hess.py", "HESS/batchOutputHess", "garbageValue", "tmp/hessIND.py", "tmp/hessBAT.py", "tmp/hessIND.py"] 
	schemesDetails["HESS"]["batcher"] = ["batchverify.py", "../tests/hess.bv", "-b", "-c", "-p"]

	# ChCh
	schemesDetails["CHCH"]["codegen"] = ["CHCH/pksig_chch.py", "CHCH/batchOutputCHCH", "garbageValue", "tmp/chchIND.py", "tmp/chchBAT.py", "tmp/chchIND.py"] 
	schemesDetails["CHCH"]["batcher"] = ["batchverify.py", "../tests/chch.bv", "-b", "-c", "-p"]

	# Waters05
	schemesDetails["WATERS"]["codegen"] = ["WATERS/pksig_waters.py", "WATERS/batchOutput", "garbageValue", "tmp/watersIND.py", "tmp/watersBAT.py", "tmp/watersIND.py"] 
	schemesDetails["WATERS"]["batcher"] = ["batchverify.py", "../tests/waters.bv", "-b", "-c", "-p"]

	# Cyh
	schemesDetails["CYH"]["codegen"] = ["CYH/pksig_cyh.py", "CYH/batchOutputCYH", "garbageValue", "tmp/cyhIND.py", "tmp/cyhBAT.py", "tmp/cyhIND.py"] 
	schemesDetails["CYH"]["batcher"] = ["batchverify.py", "../tests/cyh.bv", "-b", "-c", "-p"]

	# Boyen
	schemesDetails["Boyen"]["codegen"] = ["BOYEN/pksig_boyen.py.ORIGINAL.py", "BOYEN/batchOutputBoyen", "garbageValue", "tmp/boyenIND.py", "tmp/boyenBAT.py", "tmp/boyenIND.py"] 
	schemesDetails["Boyen"]["batcher"] = ["batchverify.py", "../tests/boyen.bv", "-b", "-c", "-p"]

        # BBS
	schemesDetails["BBS"]["codegen"] = ["BBS/groupsig_bgls04_var.py", "BBS/batchOutput_AFTERAYOMODS", "garbageValue", "tmp/bbsIND.py", "tmp/bbsBAT.py", "tmp/bbsIND.py"] 
	schemesDetails["BBS"]["batcher"] = ["batchverify.py", "../tests/bbs.bv", "-b", "-c", "-p"]
	
	# Chch + Hess
	schemesDetails["ChCh_Hess"]["codegen"] = ["CHCH_HESS/pksig_case21.py", "CHCH_HESS/batchOutput", "garbageValue", "tmp/chchhessIND.py", "tmp/chchhessBAT.py", "tmp/chchhessVER.py"]
	schemesDetails["ChCh_Hess"]["batcher"] = ["batchverify.py", "../tests/case2.bv", "-b", "-c", "-p"]

	# VRF
	schemesDetails["VRF"]["codegen"] = ["VRF/pk_vrf.py", "VRF/batchOutput", "garbageValue", "tmp/vrfIND.py", "tmp/vrfBAT.py", "tmp/vrfVER.py"]
	schemesDetails["VRF"]["batcher"] = ["batchverify.py", "../tests/vrf.bv", "-b", "-c", "-p"]

	# Cl
	schemesDetails["CL"]["codegen"] = ["CL/pksig_cl04.py", "CL/batchOutput", "garbageValue", "tmp/clIND.py", "tmp/clBAT.py", "tmp/clVER.py"]
	schemesDetails["CL"]["batcher"] = ["batchverify.py", "../tests/case1.bv", "-b", "-c", "-p"]

	# HW - diff signers
	schemesDetails["HW_Different"]["codegen"] = ["HW_DIFF/pksig_hw.py", "HW_DIFF/batchOutput", "gargabeValue", "tmp/hwdiffIND.py", "tmp/hwdiffBAT.py", "tmp/hwdiffVER.py"] 
	schemesDetails["HW_Different"]["batcher"] = ["batchverify.py", "../tests/hw-diff.bv", "-b", "-c", "-p"]

	# Waters09
	schemesDetails["Waters09"]["codegen"] = ["WATERS09/pksig_waters09_mod.py", "WATERS09/batchOutput", "garbageValue", "tmp/waters09IND.py", "tmp/waters09BAT.py", "tmp/waters09VER.py"]
	schemesDetails["Waters09"]["batcher"] = ["batchverify.py", "../tests/waters09.bv", "-b", "-c", "-p"]

	return schemesDetails

def processOneIterationForCodegen(argsDict):
	print("Call: ", argsDict)
	startTime = time.clock()
	# calling codegen
	mainFunctionForTimings(argsDict[0], argsDict[1], argsDict[2], argsDict[3], argsDict[4], argsDict[5])
	endTime = time.clock()

	result = (endTime - startTime) * time_in_ms

	outputString = ""
	outputString += str(result) + ","
	return outputString

def processOneIterationForBatcher(argsDict):
	print("Call: ", argsDict)
	startTime = time.clock()
	# calling batcher
	Batcher(argsDict)
	endTime = time.clock()

	result = (endTime - startTime) * time_in_ms

	outputString = ""
	outputString += str(result) + ","
	return outputString

def processIndSchemeCG(prefixName, schemeName, schemesDetails):
	outputFile = open(prefixName + "_" + schemeName + extensionCG, 'w')
	outputString = ""

	#for index in range(0, numArgsToCodegen):
	#	argsDict[index] = schemesDetails[schemeName][index]
	argsDictCG = schemesDetails[ schemeName ][ "codegen" ]
	for iteration in range(0, numIterations):
		outputString += processOneIterationForCodegen(argsDictCG)

	outputFile.write(outputString)
	outputFile.close()
	del outputFile

def processIndSchemeBT(prefixName, schemeName, schemesDetails):
	outputFile = open(prefixName + "_" + schemeName + extensionBT, 'w')
	outputString = ""

	argsDictBT = schemesDetails[ schemeName ][ "batcher" ]
	for iteration in range(0, numIterations):
		outputString += processOneIterationForBatcher(argsDictBT)

	outputFile.write(outputString)
	outputFile.close()
	del outputFile

def main(prefixName):
	schemesDetails = buildSchemesDetails()

	for schemeName in schemeNames:
		if (schemeName != "HW_Single"):
			# run batcher first
			processIndSchemeBT(prefixName, schemeName, schemesDetails)

	for schemeName in schemeNames:
		if (schemeName != "HW_Single"):
			# then, run codegen 
			processIndSchemeCG(prefixName, schemeName, schemesDetails)

if __name__ == '__main__':
	if ( (len(sys.argv) != 2) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  " + str(sys.argv[0]) + " [PREFIX OF OUTPUT FILES]")

	main(sys.argv[1])
