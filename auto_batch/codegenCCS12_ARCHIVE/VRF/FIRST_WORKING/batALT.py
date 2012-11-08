from toolbox.pairinggroup import *
from toolbox.iterate import dotprod
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
import sys
from toolbox.pairinggroup import *
from verALT import verifySigsRecursive

group = None
lam_func = None
debug = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group , lam_func , debug 
	group= groupObj 
	debug= False 
	lam_func= lambda i , a , b : a [ i ] ** b [ i ] 

def run_Batch(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global lam_func, debug
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	n , y , pi , pi_0= verifyArgsDict[z]['pk'][bodyKey][ 'n' ] , verifyArgsDict[z]['st'][bodyKey][ 'y' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi0' ]
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
	dotC = {}
	dotD = {}
	dotE = {}
	dotF = {}
	dotG = {}

	for z in range(0, N):
		n , y , pi , pi_0= verifyArgsDict[z]['pk'][bodyKey][ 'n' ] , verifyArgsDict[z]['st'][bodyKey][ 'y' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi0' ]

		dotA[z] =  ( verifyArgsDict[z]['pk'][bodyKey] [ 'g1' ] **(( 1 + -verifyArgsDict[z]['x'][bodyKey] [ 0 ] ) * delta [ z ] ) * verifyArgsDict[z]['pk'][bodyKey] [ 'U1' ] [ 0 ] **( verifyArgsDict[z]['x'][bodyKey] [ 0 ] * delta [ z ] ) )  
		dotB[z] =   pi[ 0 ] ** -delta [ z ]  
		dotC[z] =   pi [( n -1 ) ] ** delta [ z ]  
		dotD[z] =   pi_0 ** -delta [ z ]  
		dotE[z] =   y ** delta [ z ]  
		dotF[z] = {}
		dotG[z] = {}
		for t in range(1, n):
			dotF[z][t] =  ( pi [ t ] ** delta [ z ] * pi [ t -1 ] **(( 1 + -verifyArgsDict[z]['x'][bodyKey] [ t ] ) * -delta [ z ] ) )  
			dotG[z][t] =   pi [ t -1 ] **( verifyArgsDict[z]['x'][bodyKey] [ t ] * delta [ z ] )  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG)

	return incorrectIndices
