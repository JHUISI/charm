from charm.pairing import *
from toolbox.iterate import dotprod
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
import hashlib
import sys, random, string
from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys
from toolbox.pairinggroup import *
from verNEW import verifySigsRecursive

group = None
lam_func = None
hashObj = None
debug = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group , lam_func , hashObj , debug 
	debug= False 
	group= groupObj 
	lam_func= lambda i , a , b : a [ i ] ** b [ i ] 
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
	global lam_func, hashObj, debug
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	l = 5
	delta = {}
	for z in range(0, N):
		delta[z] = prng_bits(80)

	incorrectIndices = []
	lam_func = lambda i,a,b: a[i] ** b[i]
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
	dotD = {}
	sumE = {}

	A , g2= verifyArgsDict[z]['mpk'][bodyKey][ 'A' ] , verifyArgsDict[z]['mpk'][bodyKey][ 'g2' ]

	for z in range(0, N):
		( S1 , S2 , S3 )= verifyArgsDict[z]['sig'][bodyKey][ 'S1' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S2' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S3' ]

		dotA[z] =   S1 ** delta [ z ]  
		dotB[z] =   S2 ** delta [ z ]  
		dotD[z] =   S3 ** delta [ z ]  
		sumE[z] =   delta [ z ]  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, A, delta, dotA, dotB, dotD, sumE)

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

	for sortValKey in sortedSigEntries:
		incorrectsFromSortedBatch = run_Batch_Sorted(sortedSigEntries[sortValKey], groupObjParam, verifyFuncArgs)
		actualIndices = sigNosMap[sortValKey]
		for incorrect in incorrectsFromSortedBatch:
			incorrectIndices.append(actualIndices[incorrect])

	return incorrectIndices
