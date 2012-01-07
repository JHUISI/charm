from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from toolbox.pairinggroup import PairingGroup,G1,G2,GT,ZR,pair
import sys
from toolbox.pairinggroup import *
from ver_cyh import verifySigsRecursive

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
	group = groupObj 
	debug = False 

def concat( L_id ) : 
	result = "" 
	for i in L_id : 
		result + = ":" + i 
	return result 

def run_Batch(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global debug, H1, H2, lam_func
	group = groupObjParam

	N = len(verifyArgsDict)
	l = 5
	delta = {}
	for z in range(0, N):
		delta[z] = prng_bits(80)

	incorrectIndices = []
	H1 = lambda x: group.hash(('1', str(x)), G1)
	H2 = lambda a, b, c: group.hash(('2', a, b, c), ZR)
	lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i]) # => u * (pk ** h) for all signers
	__init__(group)


	for z in range(0, N):
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

	z = 0
	startSigNum = 0
	endSigNum = N

	dotC = {}
	dotB = {}

	for z in range(0, N):
		u , S = verifyArgsDict[z]['sig'][bodyKey][ 'u' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S' ]

		dotC[z] =   S ** delta [ z ]  
	for z in range(0, N):
		for y in range(0, l):
			u , S = verifyArgsDict[z]['sig'][bodyKey][ 'u' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S' ]
			num_signers = len( verifyArgsDict[z]['L'][bodyKey] )
			h = [ group.init( ZR , 1 ) for i in range( num_signers ) ]
			for i in range( num_signers ) :
			pk = [ H1( i ) for i in verifyArgsDict[z]['L'][bodyKey] ] # get all signers pub keys

			dotA[z] =  ( u [ l ] * pk [ l ] ** h [ l ] )  

		dotB[z] =   dotA_loopVal ** delta [ z ]  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, delta, dotC, dotA, dotB)

	return incorrectIndices
