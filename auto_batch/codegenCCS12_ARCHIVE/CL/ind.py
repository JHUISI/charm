from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import *
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
		for arg in verifyFuncArgs:
			if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		( a , b , c )= verifyArgsDict[z]['sig'][bodyKey][ 'a' ] , verifyArgsDict[z]['sig'][bodyKey][ 'a_y' ] , verifyArgsDict[z]['sig'][bodyKey][ 'a_xy' ]
		m= group.hash( verifyArgsDict[z]['M'][bodyKey] , ZR )
		if pair( verifyArgsDict[z]['pk'][bodyKey][ 'Y' ] , a )== pair( verifyArgsDict[z]['pk'][bodyKey][ 'g' ] , b ) and( pair( verifyArgsDict[z]['pk'][bodyKey][ 'X' ] , a ) *( pair( verifyArgsDict[z]['pk'][bodyKey][ 'X' ] , b ) ** m ) )== pair( verifyArgsDict[z]['pk'][bodyKey][ 'g' ] , c ) :
			pass
		else:
			if z not in incorrectIndices:
				incorrectIndices.append(z)

	return incorrectIndices
