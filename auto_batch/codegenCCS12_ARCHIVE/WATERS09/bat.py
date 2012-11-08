#NB:  I had to change the imports shown below from the original files that we used for the AutoBatch
#paper.  This is because the Charm namespace has changed.  However, this should not affectt the
#behavior of this file at all.

from charm.toolbox.pairinggroup import *
from charm.toolbox.IBEnc import *
from charm.toolbox.PKSig import PKSig
from charm.toolbox.iterate import dotprod
from charm.core.engine.util import *
from charm.core.math.integer import randomBits
import sys, random, string
import sys
from charm.toolbox.pairinggroup import *
from ver import verifySigsRecursive

group = None
util = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	#IBEnc.__init__(self) 
	global group , util 
	group= groupObj 

def run_Batch(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global util
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
	dotH = {}
	dotI = {}
	dotJ = {}
	dotK = {}
	dotL = {}
	dotM = {}
	sumN = {}

	A= verifyArgsDict[z]['mpk'][bodyKey][ 'egg_alpha' ]

	for z in range(0, N):
		s1 , s2 , t , tagc= group.random( ZR , 4 )
		s= s1 + s2
		M= group.hash( verifyArgsDict[z]['m'][bodyKey] )
		sig1 , sig2 , sig3 , sig4 , sig5 , sig6 , sig7 , sigK , tagk= verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 1 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 2 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 3 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 4 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 5 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 6 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 7 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'K' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'tagk' ]
		theta=  ~( tagc -tagk )

		dotA[z] =   sig1 **( s * delta [ z ] )  
		dotB[z] =   sig2 **( s1 * delta [ z ] )  
		dotC[z] =   sig3 **( s1 * delta [ z ] )  
		dotD[z] =   sig4 **( s2 * delta [ z ] )  
		dotE[z] =   sig5 **( s2 * delta [ z ] )  
		dotF[z] =   sig6 **( delta [ z ] * s1 )  
		dotG[z] =   sig6 **( delta [ z ] * s2 )  
		dotH[z] =   sig7 **( delta [ z ] * s1 )  
		dotI[z] =   sig7 **( delta [ z ] * s2 )  
		dotJ[z] =  ( sig7 **(( delta [ z ] * -t ) +(( theta * delta [ z ] ) *( tagc * t ) ) ) )  
		dotK[z] =   sig7 **(( theta * delta [ z ] ) *( M * t ) )  
		dotL[z] =   sig7 **(( theta * delta [ z ] ) * t )  
		dotM[z] =   sigK **( -t *( theta * delta [ z ] ) )  
		sumN[z] =  ( s2 * delta [ z ] )  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, A, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG, dotH, dotI, dotJ, dotK, dotL, dotM, sumN)

	return incorrectIndices
