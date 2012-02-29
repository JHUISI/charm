from toolbox.pairinggroup import PairingGroup,G1,G2,GT,ZR,pair
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, random, string
import sys
from toolbox.pairinggroup import *
from verNEW import verifySigsRecursive

group = None
debug = None
H1 = None
H2 = None
lam_func = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def concat( L_id ) : 
	result= "" 
	for i in L_id : 
		pass
		result += ":" + i 
	return result 

def run_Batch_Sorted(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global debug, H1, H2, lam_func
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	l= len( verifyArgsDict[z]['L'][bodyKey] )
	delta = {}
	for z in range(0, N):
		delta[z] = prng_bits(80)

	incorrectIndices = []
	lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i]) # => u * (pk ** h) for all signers
	H1 = lambda x: group.hash(('1', str(x)), G1)
	H2 = lambda a, b, c: group.hash(('2', a, b, c), ZR)
	__init__(group)


	for z in range(0, N):
		for arg in verifyFuncArgs:
			if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

	z = 0
	startSigNum = 0
	endSigNum = N

	dotC = {}
	dotB = {}

	for z in range(0, N):
		u , S= verifyArgsDict[z]['sig'][bodyKey][ 'u' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S' ]

		dotC[z] =   S ** delta [ z ]  
	for z in range(0, N):
		dotA_loopVal = group.init(G1, 1)
		for y in range(0, l):
			u , S= verifyArgsDict[z]['sig'][bodyKey][ 'u' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S' ]
			Lt= concat( verifyArgsDict[z]['L'][bodyKey] )
			l= len( verifyArgsDict[z]['L'][bodyKey] )
			h= [ group.init( ZR , 1 ) for i in range( l ) ]
			for i in range( l ) :
				pass
				h [ i ]= H2( verifyArgsDict[z]['M'][bodyKey] , Lt , u [ i ] )
			pk= [ H1( i ) for i in verifyArgsDict[z]['L'][bodyKey] ] # get all signers pub keys

			dotA_loopVal = dotA_loopVal *  ( u [ y ] * pk [ y ] ** h [ y ] )  

		dotB[z] =   dotA_loopVal ** delta [ z ]  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, delta, dotC, dotB)

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
		currentSortVal = verifyArgsDict[z]['mpk'][bodyKey][ 'Pub' ]
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
