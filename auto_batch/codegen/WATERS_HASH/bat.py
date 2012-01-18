from toolbox.pairinggroup import *
from toolbox.iterate import dotprod
from charm.engine.util import *
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
import sys, random, string
import hashlib
import sys
from toolbox.pairinggroup import *
from ver import verifySigsRecursive

group = None
debug = None
hashObj = None
lam_func = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group , debug , hashObj 
	group= groupObj 
	debug= False 
	hashObj= hashlib.new( 'sha1' ) 

def sha1( message ) : 
	h= hashObj.copy( ) 
	h.update( bytes( message , 'utf-8' ) ) 
	return Bytes( h.digest( ) ) 

def strToId( pk , strID ) : 
	'''Hash the identity string and break it up in to l bit pieces''' 
	hash= sha1( strID ) 
	val= Conversion.OS2IP( hash ) #Convert to integer format 
	bstr= bin( val ) [ 2 : ]   #cut out the 0b header 

	v= [ ] 
	for i in range( pk [ 'z' ] ) :  #z must be greater than or equal to 1 
		pass
		binsubstr= bstr [ pk [ 'l' ] * i : pk [ 'l' ] *( i + 1 ) ] 
		intval= int( binsubstr , 2 ) 
		intelement= group.init( ZR , intval ) 
		v.append( intelement ) 
	return v 

def run_Batch_Sorted(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global debug, hashObj, lam_func
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	delta = {}
	for z in range(0, N):
		delta[z] = prng_bits(80)

	incorrectIndices = []
	lam_func = lambda i,a,b: a[i] ** b[i]
	__init__(group)


	for z in range(0, N):
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

	z = 0
	startSigNum = 0
	endSigNum = N

	dotA = {}
	dotB = {}

	for z in range(0, N):
		M= strToId( verifyArgsDict[z]['mpk'][bodyKey] , verifyArgsDict[z]['message'][bodyKey] )
		h= verifyArgsDict[z]['mpk'][bodyKey][ 'u0' ] * dotprod( 1 , -1 , verifyArgsDict[z]['mpk'][bodyKey][ 'z' ] , lam_func , verifyArgsDict[z]['mpk'][bodyKey][ 'u' ] , M )
		sig= verifyArgsDict[z]['sigDict'][bodyKey][ 'sig1' ]
		t= verifyArgsDict[z]['sigDict'][bodyKey][ 'sig2' ]

		dotA[z] =   h **( t * delta [ z ] )  
		dotB[z] =   sig **( delta [ z ] * t )  

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
		currentSortVal = verifyArgsDict[z]['pk'][bodyKey][ 'g^x' ]
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
