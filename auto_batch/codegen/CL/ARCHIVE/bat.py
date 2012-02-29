from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import *
import sys
from toolbox.pairinggroup import *
from ver import verifySigsRecursive

group = None
debug = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def run_Batch(verifyArgsDict, groupObjParam, verifyFuncArgs):
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
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

	z = 0
	startSigNum = 0
	endSigNum = N

	dotA = {}
	dotB = {}
	dotC = {}

	for z in range(0, N):
		( a , b , c )= verifyArgsDict[z]['sig'][bodyKey][ 'a' ] , verifyArgsDict[z]['sig'][bodyKey][ 'a_y' ] , verifyArgsDict[z]['sig'][bodyKey][ 'a_xy' ]
		m= group.hash( verifyArgsDict[z]['M'][bodyKey] , ZR )

		dotA[z] =   a ** delta [ z ]  
		dotB[z] =  ( b ** -delta [ z ] * c ** -delta [ z ] )  
		dotC[z] =  ( a ** delta [ z ] * b **( m * delta [ z ] ) )  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, delta, dotA, dotB, dotC)

	return incorrectIndices
