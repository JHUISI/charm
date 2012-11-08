from toolbox.pairinggroup import *
from toolbox.iterate import dotprod
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
import sys
from toolbox.pairinggroup import *
from ver import verifySigsRecursive

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
	n , y , pi , pizero= verifyArgsDict[z]['pk'][bodyKey][ 'n' ] , verifyArgsDict[z]['st'][bodyKey][ 'y' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi0' ]
	delta1 = {}; delta2 = {}; delta3 = {}
	for z in range(0, N):
		delta1[z] = prng_bits(80)
		delta2[z] = prng_bits(80)
		delta3[z] = prng_bits(80)

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

	for z in range(0, N):
		n , y , pi , pizero= verifyArgsDict[z]['pk'][bodyKey][ 'n' ] , verifyArgsDict[z]['st'][bodyKey][ 'y' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi0' ]

		dotA[z] =  ( verifyArgsDict[z]['pk'][bodyKey] [ 'g1' ] **(( 1-verifyArgsDict[z]['x'][bodyKey] [ 0 ] ) * delta1 [ z ] ) * verifyArgsDict[z]['pk'][bodyKey] [ 'U1' ] [ 0 ] **( verifyArgsDict[z]['x'][bodyKey] [ 0 ] * delta1 [ z ] ) )  
		dotB[z] =   pi [ 0 ] ** -delta1 [ z ]  
		dotC[z] =   pi [ n -1 ] ** delta1 [ z ]  
		dotD[z] =   pizero ** -delta1 [ z ]  
		dotE[z] =   y ** -delta1 [ z ]  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, delta1, dotA, dotB, dotC, dotD, dotE)

	return incorrectIndices
