from toolbox.PKSig import PKSig
from math import *
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import *
import sys
from toolbox.pairinggroup import *
from verTEST import verifySigsRecursive

group = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group 
	group= groupObj 

def ceilog( value ) : 
	return group.init( ZR , ceil( log( value , 2 ) ) ) 

def run_Batch(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	r , s= verifyArgsDict[z]['sig'][bodyKey][ 'r' ] , verifyArgsDict[z]['sig'][bodyKey][ 'i' ]
	n= ceilog( s )
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

	z = 0
	startSigNum = 0
	endSigNum = N

	dotA = {}
	dotB = {}
	dotC = {}
	dotD = {}
	dotE = {}
	dotF = {}
	dotG = {}

	r , s= verifyArgsDict[z]['sig'][bodyKey][ 'r' ] , verifyArgsDict[z]['sig'][bodyKey][ 'i' ]
	S= group.init( ZR , s )
	n= ceilog( s )

	for z in range(0, N):
		M= group.hash( verifyArgsDict[z]['msg'][bodyKey] , ZR )
		sigma1 , sigma2= verifyArgsDict[z]['sig'][bodyKey][ 1 ] , verifyArgsDict[z]['sig'][bodyKey][ 2 ]
		r , s= verifyArgsDict[z]['sig'][bodyKey][ 'r' ] , verifyArgsDict[z]['sig'][bodyKey][ 'i' ]
		U , V , D= verifyArgsDict[z]['pk'][bodyKey][ 'U' ] , verifyArgsDict[z]['pk'][bodyKey][ 'V' ] , verifyArgsDict[z]['pk'][bodyKey][ 'D' ]

		dotA[z] =   sigma1 ** delta [ z ]  
		dotB[z] =   U **( M * delta [ z ] )  
		dotC[z] =   V **( r * delta [ z ] )  
		dotD[z] =   D ** delta [ z ]  
		dotE[z] =   sigma2 **( delta [ z ] * n )  
		dotF[z] =   sigma2 **( delta [ z ] * S )  
		dotG[z] =   sigma2 ** delta [ z ]  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, n, S, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG)

	return incorrectIndices
