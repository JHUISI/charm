from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
import sys
from toolbox.pairinggroup import *
from verNEW import verifySigsRecursive

group = None
debug = None
H = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def getPKdict( mpk , pk , k ) : 
	A_pk , B_pk , C_pk= { } , { } , { } 
	A_pk [ 0 ]= mpk [ k [ 0 ] ] 
	B_pk [ 0 ]= mpk [ k [ 1 ] ] 
	C_pk [ 0 ]= mpk [ k [ 2 ] ] 
	for i in pk.keys( ) : 
		pass
		A_pk [ i ]= pk [ i ] [ k [ 0 ] ] 
		B_pk [ i ]= pk [ i ] [ k [ 1 ] ] 
		C_pk [ i ]= pk [ i ] [ k [ 2 ] ] 
	return A_pk , B_pk , C_pk 

def run_Batch_Sorted(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global debug, H
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	At , Bt , Ct= getPKdict( verifyArgsDict[z]['mpk'][bodyKey] , verifyArgsDict[z]['pk'][bodyKey] , [ 'At' , 'Bt' , 'Ct' ] )
	l= len( At.keys( ) )
	delta = {}
	for z in range(0, N):
		delta[z] = prng_bits(80)

	incorrectIndices = []
	H = lambda a: group.hash(('1', str(a)), ZR)
	__init__(group)


	for z in range(0, N):
		for arg in verifyFuncArgs:
			if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

	z = 0
	startSigNum = 0
	endSigNum = N

	dotD = {}

	D= pair( verifyArgsDict[z]['mpk'][bodyKey][ 'g1' ] , verifyArgsDict[z]['mpk'][bodyKey][ 'g2' ] )

	for z in range(0, N):

		dotD[z] =   D ** delta [ z ]  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, D, delta, dotD)

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
		currentSortVal = verifyArgsDict[z]['mpk'][bodyKey][ 'g1' ]
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

	#print(sigNosMap)

	for sortValKey in sortedSigEntries:
		incorrectsFromSortedBatch = run_Batch_Sorted(sortedSigEntries[sortValKey], groupObjParam, verifyFuncArgs)
		actualIndices = sigNosMap[sortValKey]
		for incorrect in incorrectsFromSortedBatch:
			incorrectIndices.append(actualIndices[incorrect])

	return incorrectIndices
