from toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from toolbox.iterate import dotprod
import sys
from toolbox.pairinggroup import *
from ver import verifySigsRecursive

group = None
lam_func = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group , lam_func 
	group= groupObj 
	lam_func= lambda i , a , b : a [ i ] ** b [ i ] 

def run_Batch_Sorted(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global lam_func
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
	dotC = {}
	dotD = {}
	dotE = {}
	dotF = {}
	dotG = {}

	for z in range(0, N):
		n , y , pi , pi_0= verifyArgsDict[z]['pk'][bodyKey][ 'n' ] , verifyArgsDict[z]['st'][bodyKey][ 'y' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi0' ]

		dotA[z] =  ( verifyArgsDict[z]['pk'][bodyKey] [ 'g1' ] **(( 1 + -verifyArgsDict[z]['x'][bodyKey] [ 1 ] ) * delta [ z ] ) * verifyArgsDict[z]['pk'][bodyKey] [ 'U1' ] [ 0 ] **( verifyArgsDict[z]['x'][bodyKey] [ 1 ] * delta [ z ] ) )  
		dotB[z] =   pi [ 1 ] ** -delta [ z ]  
		dotC[z] =   pi [ n ] ** delta [ z ]  
		dotD[z] =   pi [ 0 ] ** -delta [ z ]  
		dotE[z] =   y ** delta [ z ]  
		dotF[z] =  ( pi [ t ] ** delta [ z ] * pi [ t ] -1 **(( 1 + -verifyArgsDict[z]['x'][bodyKey] [ t ] ) * -delta [ z ] ) )  
		dotG[z] =   pi [ t ] -1 **( verifyArgsDict[z]['x'][bodyKey] [ t ] * delta [ z ] )  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG)

	return incorrectIndices
