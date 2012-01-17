from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, random, string
import sys

group = None
debug = None
bodyKey = 'Body'

def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global debug
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	incorrectIndices = []
	__init__(group)

	for z in range(0, N):
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		M= verifyArgsDict[z]['message'][bodyKey]
		h= group.hash( M , G1 )
		sig= verifyArgsDict[z]['sigDict'][bodyKey][ 'sig1' ]
		t= verifyArgsDict[z]['sigDict'][bodyKey][ 'sig2' ]
		if pair( sig ,( verifyArgsDict[z]['pk'][bodyKey][ 'g' ] ** t ) )==( pair( h , verifyArgsDict[z]['pk'][bodyKey][ 'g^x' ] ) ** t ) :
			pass
		else:
			if z not in incorrectIndices:
				incorrectIndices.append(z)

	return incorrectIndices
