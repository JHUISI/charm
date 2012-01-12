from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import *
import sys
from toolbox.pairinggroup import *
from ver_bbs import verifySigsRecursive

group = None
debug = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	#PKSig.__init__( self ) 
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
		c , T1 , T2 , T3= verifyArgsDict[z]['sigma'][bodyKey][ 'c' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T1' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T2' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T3' ]
		R3= verifyArgsDict[z]['sigma'][bodyKey][ 'R3' ]

		dotA[z] =  ( T3 **( -sx * delta [ z ] ) *( verifyArgsDict[z]['gpk'][bodyKey] [ 'h' ] **(( -sgamma1 * -sgamma2 ) * delta [ z ] ) * verifyArgsDict[z]['gpk'][bodyKey] [ 'g1' ] **( c * delta [ z ] ) ) )  
		dotB[z] =  ( verifyArgsDict[z]['gpk'][bodyKey] [ 'h' ] **(( -salpha * -sbeta ) * delta [ z ] ) * T3 **( -c * delta [ z ] ) )  
		dotC[z] =   R3 ** delta [ z ]  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, delta, dotA, dotB, dotC)

	return incorrectIndices

'''
def run_Batch(verifyArgsDict, groupObjParam, verifyFuncArgs, toSort):
	if (toSort == False):
		incorrectIndices = run_Batch_Sorted(verifyArgsDict, groupObjParam, verifyFuncArgs)
		return incorrectIndices

	N = len(verifyArgsDict)
	sortValues = {}
	sigNosMap = {}
	sortedSigEntries = {}
	for z in range(0, N):
'''
