from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import PairingGroup,G1,G2,GT,ZR,pair
import sys
from toolbox.pairinggroup import *
from ver_chp import verifySigsRecursive

group = None
H = None
debug = None
H = None
H3 = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group , H , debug 
	group= groupObj 
	debug= False 

def run_Batch(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global H, debug, H, H3
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	delta = {}
	for z in range(0, N):
		delta[z] = prng_bits(80)

	incorrectIndices = []
	H3 = lambda a,b: group.hash(('3', str(a), str(b)), ZR)
	H = lambda prefix,x: group.hash((str(prefix), str(x)), G1)
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

	a= H( 1 , verifyArgsDict[z]['M'][bodyKey][ 't1' ] )
	h= H( 2 , verifyArgsDict[z]['M'][bodyKey][ 't2' ] )

	for z in range(0, N):
		b= H3( verifyArgsDict[z]['M'][bodyKey][ 'str' ] , verifyArgsDict[z]['M'][bodyKey][ 't3' ] )

		dotA[z] =   verifyArgsDict[z]['sig'][bodyKey] ** delta [ z ]  
		dotB[z] =   verifyArgsDict[z]['pk'][bodyKey] ** delta [ z ]  
		dotC[z] =   verifyArgsDict[z]['pk'][bodyKey] **( b * delta [ z ] )  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, a, h, delta, dotA, dotB, dotC)

	return incorrectIndices
