from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from charm.engine.util import *
import sys, random, string
#from toolbox.IBEnc import *
import sys
#from toolbox.pairinggroup import *
from ver import verifySigsRecursive

group = None
util = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	#IBEnc.__init__( self ) 
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
	sumI = {}

	A= verifyArgsDict[z]['mpk'][bodyKey][ 'egg_alpha' ]

	for z in range(0, N):
		s1 , s2 , t , tagc= group.random( ZR , 4 )
		s= s1 + s2
		sig1 , sig2 , sig3 , sig4 , sig5 , sig6 , sig7 , sigK , tagk= verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 1 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 2 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 3 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 4 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 5 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 6 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 7 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'K' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'tagk' ]
		M= group.hash( verifyArgsDict[z]['m'][bodyKey] )
		theta=  ~( tagc -tagk )

		B = (verifyArgsDict[z]['mpk'][bodyKey]['tau1^b'] ** s1) * (verifyArgsDict[z]['mpk'][bodyKey]['tau2^b'] ** s2)

		dotA[z] =   sig1 **( s * delta [ z ] )  
		dotB[z] =   sig2 **( s1 * delta [ z ] )  
		dotC[z] =   sig3 **( s1 * delta [ z ] )  
		dotD[z] =   sig4 **( s2 * delta [ z ] )  
		dotE[z] =   sig5 **( s2 * delta [ z ] )  
		#dotF[z] =   sig6 **( s1 *( s2 * delta [ z ] ) )  
		#dotG[z] =   sig7 **( s1 *( delta [ z ] *( s2 *( -t *( M *( tagc *( t * theta ) ) ) ) ) ) )  

		dotF[z] = pair(((verifyArgsDict[z]['mpk'][bodyKey]['tau1'] ** s1) * (verifyArgsDict[z]['mpk'][bodyKey]['tau2'] ** s2)), sig6 ** delta[z]) 
		dotG[z] = pair((B * (verifyArgsDict[z]['mpk'][bodyKey]['w1'] ** -t)) * ((verifyArgsDict[z]['mpk'][bodyKey]['u'] ** (M * t * theta)) * (verifyArgsDict[z]['mpk'][bodyKey]['w1'] ** (t * theta * tagc)) * (verifyArgsDict[z]['mpk'][bodyKey]['h1'] ** (t * theta)) )  , sig7 ** delta[z])

		dotH[z] =   sigK **( -t *( theta * delta [ z ] ) )  
		sumI[z] =  ( s2 * delta [ z ] )  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, A, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG, dotH, sumI)

	return incorrectIndices
