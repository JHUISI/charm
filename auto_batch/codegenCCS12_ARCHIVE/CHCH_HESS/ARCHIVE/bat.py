from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
from schemes.pksig_hess import Hess
from schemes.pksig_chch import CHCH
import sys
from toolbox.pairinggroup import *
from ver import verifySigsRecursive

group = None
H2 = None
debug = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global H2 , group , debug 
	group= groupObj 
	debug= False 
	H2= lambda x , y : group.hash(( x , y ) , ZR ) 

def run_Batch_Sorted(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global H2, debug
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	delta = {}
	for z in range(0, N):
		delta[z] = prng_bits(80)

	incorrectIndices = []
	H2 = lambda x,y: group.hash((x,y), ZR)
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
		sig1 , sig2= verifyArgsDict[z]['sig'][bodyKey][ 'sig_hess' ] , verifyArgsDict[z]['sig'][bodyKey][ 'sig_chch' ]
		S1h , S2h= sig1 [ 'S1' ] , sig1 [ 'S2' ]
		S1c , S2c= sig2 [ 'S1' ] , sig2 [ 'S2' ]
		ah= H2( verifyArgsDict[z]['M'][bodyKey] , S1h )
		ac= H2( verifyArgsDict[z]['M'][bodyKey] , S1c )

		dotA[z] =  ( verifyArgsDict[z]['pk'][bodyKey] **( ah * delta [ z ] ) *( S1c ** -delta [ z ] * verifyArgsDict[z]['pk'][bodyKey] **( ac * -delta [ z ] ) ) )  
		dotB[z] =   S1h ** delta [ z ]  
		dotC[z] =  ( S2h ** -delta [ z ] * S2c ** delta [ z ] )  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, delta, dotA, dotB, dotC)

	return incorrectIndices
