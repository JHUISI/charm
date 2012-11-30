import sys, time
import AutoBatch 
#from AutoBatch_CodeGen_FOR_TIMING_MSMTS import *

# NOTE: CHP, HESS, CHCH, WATERS05, CYH and BBS give this error: "SubscriptName->setValue: value passed in is of None type."
schemeNames = ["BLS", "Boyen", "ChCh_Hess", "VRF", "CL", "HW_Single", "HW_Different", "Waters09", "CHP", "HESS", "CHCH", "WATERS", "CYH", "BBS"]
schemeUsedList = schemeNames
extensionCG = "_codegen.dat"
extensionBT = "_batcher.dat"
numIterations = 1 #100
numArgsToCodegen = 2
time_in_ms = 1000
dest = "tmp"

def buildSchemesDetails():
	schemesDetails = {}

	for schemeName in schemeNames:
		schemesDetails[schemeName] = {}

	# Bls
	schemesDetails["BLS"]["codegen"] = [dest+'/bls-full-batch.bv', dest+'/bls.py'] # ["BLS/pksig_bls04.py", "BLS/batchOutput_BLS", "garbageValue", "tmp/blsIND.py", "tmp/blsBAT.py", "tmp/blsIND.py"] 
	schemesDetails["BLS"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/BLS/bls-full.bv', 'out_file':dest+'/bls-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None}   # ["batchverify.py", "../tests/bls.bv", "-p"]

	# Chp
	schemesDetails["CHP"]["codegen"] = [dest+'/chp-full-batch.bv', dest+'/chp.py'] # ["CHP/pksig_chp.py", "CHP/batchOutputCHP", "garbageValue", "tmp/chpIND.py", "tmp/chpBAT.py", "tmp/chpIND.py"] 
	schemesDetails["CHP"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/CHP/chp.bv', 'out_file':dest+'/chp-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None}   # ["batchverify.py", "../tests/bls.bv", "-p"]

	# Hess
	schemesDetails["HESS"]["codegen"] = [dest+'/hess-full-batch.bv', dest+'/hess.py'] # ["HESS/pksig_hess.py", "HESS/batchOutputHess", "garbageValue", "tmp/hessIND.py", "tmp/hessBAT.py", "tmp/hessIND.py"] 
	schemesDetails["HESS"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/HESS/hess-full.bv', 'out_file':dest+'/hess-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None} #["batchverify.py", "../tests/hess.bv", "-p"]

	# ChCh
	schemesDetails["CHCH"]["codegen"] = [dest+'/chch-full-batch.bv', dest+'/chch.py'] # ["CHCH/pksig_chch.py", "CHCH/batchOutputCHCH", "garbageValue", "tmp/chchIND.py", "tmp/chchBAT.py", "tmp/chchIND.py"] 
	schemesDetails["CHCH"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/CHCH/chch-full.bv', 'out_file':dest+'/chch-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None} #["batchverify.py", "../tests/chch.bv", "-p"]

	# Waters05
	schemesDetails["WATERS"]["codegen"] = [dest+'/waters05-full-batch.bv', dest+'/waters05.py'] # ["WATERS/pksig_waters.py", "WATERS/batchOutput", "garbageValue", "tmp/watersIND.py", "tmp/watersBAT.py", "tmp/watersIND.py"] 
	schemesDetails["WATERS"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/WATERS05/waters05.bv', 'out_file':dest+'/waters05-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None} #["batchverify.py", "../tests/waters.bv", "-p"]

	# Cyh
	schemesDetails["CYH"]["codegen"] = [dest+'/cyh-full-batch.bv', dest+'/cyh.py'] # ["CYH/pksig_cyh.py", "CYH/batchOutputCYH", "garbageValue", "tmp/cyhIND.py", "tmp/cyhBAT.py", "tmp/cyhIND.py"] 
	schemesDetails["CYH"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/CYH/cyh.bv', 'out_file':dest+'/cyh-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None} #["batchverify.py", "../tests/cyh.bv", "-p"]

	# Boyen
	schemesDetails["Boyen"]["codegen"] = [dest+'/boyen-full-batch.bv', dest+'/boyen.py'] # ["BOYEN/pksig_boyen.py.ORIGINAL.py", "BOYEN/batchOutputBoyen", "garbageValue", "tmp/boyenIND.py", "tmp/boyenBAT.py", "tmp/boyenIND.py"] 
	schemesDetails["Boyen"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/BOYEN/boyen.bv', 'out_file':dest+'/boyen-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None}#["batchverify.py", "../tests/boyen.bv", "-p"]

        # BBS
	schemesDetails["BBS"]["codegen"] = [dest+'/bbs-full-batch.bv', dest+'/bbs.py'] # ["BBS/groupsig_bgls04_var.py", "BBS/batchOutput_AFTERAYOMODS", "garbageValue", "tmp/bbsIND.py", "tmp/bbsBAT.py", "tmp/bbsIND.py"] 
	schemesDetails["BBS"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/BBS/bbs.bv', 'out_file':dest+'/bbs-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None}#["batchverify.py", "../tests/bbs.bv", "-p"]
	
	# Chch + Hess
	schemesDetails["ChCh_Hess"]["codegen"] = [dest+'/chch-hess-full-batch.bv', dest+'/chch-hess.py'] # ["CHCH_HESS/pksig_case21.py", "CHCH_HESS/batchOutput", "garbageValue", "tmp/chchhessIND.py", "tmp/chchhessBAT.py", "tmp/chchhessVER.py"]
	schemesDetails["ChCh_Hess"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/CHCH-HESS/chch-hess.bv', 'out_file':dest+'/chch-hess-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None} #["batchverify.py", "../tests/case2.bv", "-p"]

	# VRF
	schemesDetails["VRF"]["codegen"] = [dest+'/vrf-full-batch.bv', dest+'/vrf.py'] # ["VRF/pk_vrf.py", "VRF/batchOutput", "garbageValue", "tmp/vrfIND.py", "tmp/vrfBAT.py", "tmp/vrfVER.py"]
	schemesDetails["VRF"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/VRF/vrf.bv', 'out_file':dest+'/vrf-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None} #["batchverify.py", "../tests/vrf.bv", "-p"]

	# Cl
	schemesDetails["CL"]["codegen"] = [dest+'/cl-full-batch.bv', dest+'/cl.py'] # ["CL/pksig_cl04.py", "CL/batchOutput", "garbageValue", "tmp/clIND.py", "tmp/clBAT.py", "tmp/clVER.py"]
	schemesDetails["CL"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/CL/cl04.bv', 'out_file':dest+'/cl-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None} #["batchverify.py", "../tests/case1.bv", "-p"]

	# HW - diff signers
	schemesDetails["HW_Different"]["codegen"] = [dest+'/hwdiff-full-batch.bv', dest+'/hwdiff.py'] # ["HW_DIFF/pksig_hw.py", "HW_DIFF/batchOutput", "gargabeValue", "tmp/hwdiffIND.py", "tmp/hwdiffBAT.py", "tmp/hwdiffVER.py"] 
	schemesDetails["HW_Different"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/HWdiff/hw.bv', 'out_file':dest+'/hwdiff-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None} #["batchverify.py", "../tests/hw-diff.bv", "-p"]

	# Waters09
	schemesDetails["Waters09"]["codegen"] = [dest+'/waters09-full-batch.bv', dest+'/waters09.py'] # ["WATERS09/pksig_waters09_mod.py", "WATERS09/batchOutput", "garbageValue", "tmp/waters09IND.py", "tmp/waters09BAT.py", "tmp/waters09VER.py"]
	schemesDetails["Waters09"]["batcher"] = {'verbose':False, 'sdl_file':'../codegenFullSDLBatch/WATERS09/waters09.bv', 'out_file':dest+'/waters09-full-batch.bv', 'codegen':False, 'threshold':False, 'proof':True, 'strategy':'bfs', 'pre_check':False, 'library':'miracl', 'test_stmt':None} # ["batchverify.py", "../tests/waters09.bv", "-p"] # removed -b, -c

	return schemesDetails

def processOneIterationForCodegenPY(argsDict):
	#mainFunctionForTimings(argsDict[0], argsDict[1], argsDict[2], argsDict[3], argsDict[4], argsDict[5])
	(startTime, endTime) = AutoBatch.CodegenPY(argsDict)
	result = (endTime - startTime) * time_in_ms
	print("Full CG PY: ", argsDict, ", time: ", result)

	outputString = ""
	outputString += str(result) + ","
	return outputString

def processOneIterationForBatcher(argsDict):
	#startTime = time.clock()
	# calling batcher
	(startTime, endTime) = AutoBatch.Batcher(argsDict)
	result = (endTime - startTime) * time_in_ms
	print("Batcher: ", argsDict, ", time: ", result)

	outputString = ""
	outputString += str(result) + ","
	return outputString

def processIndSchemeCG_PY(prefixName, schemeName, schemesDetails):
	outputFile = open(prefixName + "_" + schemeName + extensionCG, 'w')
	outputString = ""

	#for index in range(0, numArgsToCodegen):
	#	argsDict[index] = schemesDetails[schemeName][index]
	argsDictCG = schemesDetails[ schemeName ][ "codegen" ]
	for iteration in range(0, numIterations):
		outputString += processOneIterationForCodegenPY(argsDictCG)

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

	for schemeName in schemeUsedList:
		if (schemeName != "HW_Single"):
			# run batcher first
			processIndSchemeBT(prefixName, schemeName, schemesDetails)

	for schemeName in schemeUsedList:
		if (schemeName != "HW_Single"):
			# then, run codegen 
			processIndSchemeCG_PY(prefixName, schemeName, schemesDetails)

if __name__ == '__main__':
	if ( (len(sys.argv) != 2) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
		sys.exit("Usage:  " + str(sys.argv[0]) + " [PREFIX OF OUTPUT FILES]")

	main(sys.argv[1])
