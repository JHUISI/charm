from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import *
import sys
from verNEW import verifySigsRecursive

group = None
debug = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def run_Batch_Sorted(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global debug
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	delta = {}
	for z in range(0, N):
		delta[z] = prng_bits(80)

	incorrectIndices = []
	__init__(group)


	for z in range(0, N):
		for arg in verifyFuncArgs:
			if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		c , T1 , T2 , T3= verifyArgsDict[z]['sigma'][bodyKey][ 'c' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T1' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T2' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T3' ]
		salpha , sbeta= verifyArgsDict[z]['sigma'][bodyKey][ 's_alpha' ] , verifyArgsDict[z]['sigma'][bodyKey][ 's_beta' ]
		sx , sgamma1 , sgamma2= verifyArgsDict[z]['sigma'][bodyKey][ 's_x' ] , verifyArgsDict[z]['sigma'][bodyKey][ 's_gamma1' ] , verifyArgsDict[z]['sigma'][bodyKey][ 's_gamma2' ]
		R3= verifyArgsDict[z]['sigma'][bodyKey][ 'R3' ]
		R1=( verifyArgsDict[z]['gpk'][bodyKey][ 'u' ] ** salpha ) *( T1 ** -c )
		R2=( verifyArgsDict[z]['gpk'][bodyKey][ 'v' ] ** sbeta ) *( T2 ** -c )
		R4=( T1 ** sx ) *( verifyArgsDict[z]['gpk'][bodyKey][ 'u' ] ** -sgamma1 )
		R5=( T2 ** sx ) *( verifyArgsDict[z]['gpk'][bodyKey][ 'v' ] ** -sgamma2 )
		if c== group.hash(( verifyArgsDict[z]['M'][bodyKey] , T1 , T2 , T3 , R1 , R2 , R3 , R4 , R5 ) , ZR ) :
			if debug : print( "c=> '%s'" % c )
			if debug : print( "Valid Group Signature for message: '%s'" % verifyArgsDict[z]['M'][bodyKey] )
			pass
		else :
			if debug : print( "Not a valid signature for message!!!" )
			incorrectIndices.append(z)

	z = 0
	startSigNum = 0
	endSigNum = N

	dotA = {}
	dotB = {}
	dotC = {}

	for z in range(0, N):
		c , T1 , T2 , T3= verifyArgsDict[z]['sigma'][bodyKey][ 'c' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T1' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T2' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T3' ]
		salpha , sbeta= verifyArgsDict[z]['sigma'][bodyKey][ 's_alpha' ] , verifyArgsDict[z]['sigma'][bodyKey][ 's_beta' ]
		sx , sgamma1 , sgamma2= verifyArgsDict[z]['sigma'][bodyKey][ 's_x' ] , verifyArgsDict[z]['sigma'][bodyKey][ 's_gamma1' ] , verifyArgsDict[z]['sigma'][bodyKey][ 's_gamma2' ]
		R3= verifyArgsDict[z]['sigma'][bodyKey][ 'R3' ]

		dotA[z] =  ( T3 **( sx * delta [ z ] ) *( verifyArgsDict[z]['gpk'][bodyKey] [ 'h' ] **(( -sgamma1 + -sgamma2 ) * delta [ z ] ) * verifyArgsDict[z]['gpk'][bodyKey] [ 'g1' ] **( -c * delta [ z ] ) ) )  
		dotB[z] =  ( verifyArgsDict[z]['gpk'][bodyKey] [ 'h' ] **(( -salpha + -sbeta ) * delta [ z ] ) * T3 **( c * delta [ z ] ) )  
		dotC[z] =   R3 ** delta [ z ]  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, delta, dotA, dotB, dotC)

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
		currentSortVal = verifyArgsDict[z]['gpk'][bodyKey][ 'g1' ]
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
