from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import PairingGroup,G1,G2,ZR,pair
import sys

group = None
debug = None
H1 = None
H2 = None
bodyKey = 'Body'

def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global debug, H1, H2
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	incorrectIndices = []
	H2 = lambda x,y: group.hash((x,y), ZR)
	H1 = lambda x: group.hash(x, G1)
	__init__(group)

	for z in range(0, N):
		for arg in verifyFuncArgs:
			if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		if debug : print( "verify..." )
		#( S1 , S2 )= verifyArgsDict[z]['sig'][bodyKey]
		S1= verifyArgsDict[z]['sig'][bodyKey][ 'S1' ]
		S2= verifyArgsDict[z]['sig'][bodyKey][ 'S2' ]
		a= H2( verifyArgsDict[z]['M'][bodyKey] , S1 )
		if pair( S2 , verifyArgsDict[z]['mpk'][bodyKey][ 'g2' ] )==( pair( verifyArgsDict[z]['pk'][bodyKey] , verifyArgsDict[z]['mpk'][bodyKey][ 'P' ] ) ** a ) * S1 :
			pass
		else:
			if z not in incorrectIndices:
				incorrectIndices.append(z)

	return incorrectIndices
