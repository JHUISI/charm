from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import *
import sys
from toolbox.pairinggroup import *
from verNEW import verifySigsRecursive

group = None
debug = None
H1 = None
H2 = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def run_Batch_Sorted(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global debug, H1, H2
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	delta = {}
	for z in range(0, N):
		delta[z] = prng_bits(80)

	incorrectIndices = []
	H1 = lambda x: group.hash(x, G1)
	H2 = lambda x,y: group.hash((x,y), ZR)
	__init__(group)


	for z in range(0, N):
		for arg in verifyFuncArgs:
			if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

	z = 0
	startSigNum = 0
	endSigNum = N

	dotA = {}
	dotB = {}

	for z in range(0, N):
		( S1 , S2 )= verifyArgsDict[z]['sig'][bodyKey][ 'S1' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S2' ]
		a= H2( verifyArgsDict[z]['M'][bodyKey] , S1 )

		dotA[z] =   S2 ** delta [ z ]  
		dotB[z] =  ( S1 * verifyArgsDict[z]['pk'][bodyKey] ** a ) ** delta [ z ]  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, delta, dotA, dotB)

	return incorrectIndices

def run_Batch(verifyArgsDict, groupObjParam, verifyFuncArgs, toSort):
	if (toSort == False):
		incorrectIndices = run_Batch_Sorted(verifyArgsDict, groupObjParam, verifyFuncArgs)
		return incorrectIndices

	N = len(verifyArgsDict)
	sortValues = {}
	sigNosMap = {}
	sortedSigEntries = {}
	for z in range(0, N):
		currentSortVal = verifyArgsDict[z]['mpk'][bodyKey][ 'P' ]
		matchingIndex = None
		sortKey = -1
		for sortKey in sortValues:
			if (sortValues[sortKey] == currentSortVal):
				matchingIndex = sortKey
				break
		if (matchingIndex != None):
			sigNosMap[matchingIndex].append(z)
			lenCurrentSigsBatch = len(sortedSigEntries[matchingIndex])
			sortedSigEntries[matchingIndex][lenCurrentSigsBatch] = verifyArgsDict[z]
		else:
			newIndex = sortKey + 1
			sortValues[newIndex] = currentSortVal
			sigNosMap[newIndex] = []
			sigNosMap[newIndex].append(z)
			sortedSigEntries[newIndex] = {}
			sortedSigEntries[newIndex][0] = verifyArgsDict[z]

	incorrectIndices = []

	for sortValKey in sortedSigEntries:
		incorrectsFromSortedBatch = run_Batch_Sorted(sortedSigEntries[sortValKey], groupObjParam, verifyFuncArgs)
		actualIndices = sigNosMap[sortValKey]
		for incorrect in incorrectsFromSortedBatch:
			incorrectIndices.append(actualIndices[incorrect])

	return incorrectIndices
