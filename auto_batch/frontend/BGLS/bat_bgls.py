import sys, random, string
from charm.engine.util import *
from toolbox.pairinggroup import *
import sys
from toolbox.pairinggroup import *
from ver_bgls import verifySigsRecursive

group = None
g2 = None
debug = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

def __init__( groupObj ) : 
	global group , g2 , debug 
	group= groupObj 
	g2= group.random( G2 ) 
	debug= False 

def run_Batch(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global g2, debug
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	l = 5
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

	for z in range(0, N):

		dotA[z] =   verifyArgsDict[z]['sig'][bodyKey] ** delta [ z ]  

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, delta, dotA)

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
