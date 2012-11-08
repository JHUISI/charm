import sys, random, string
from charm.engine.util import *
from toolbox.pairinggroup import *
import sys

group = None
g2 = None
debug = None
bodyKey = 'Body'

def __init__( groupObj ) : 
	global group , g2 , debug 
	group= groupObj 
	g2= group.random( G2 ) 
	debug= False 

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global g2, debug
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	l = 5
	incorrectIndices = []
	__init__(group)

	for z in range(0, N):
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		rightSideProduct= group.init( GT , 1 )
		for index in range( 0 , len( verifyArgsDict[z]['M'][bodyKey] ) ) :
			pass
			h= group.hash( verifyArgsDict[z]['M'][bodyKey][ index ] , G1 )
			rightSideProduct= rightSideProduct * pair( h , verifyArgsDict[z]['pk'][bodyKey][ index ] [ 'g^x' ] )
		if pair( verifyArgsDict[z]['sig'][bodyKey] , verifyArgsDict[z]['pk'][bodyKey][ 0 ] [ 'g2' ] )== rightSideProduct :
			pass
		else:
			if z not in incorrectIndices:
				incorrectIndices.append(z)

	return incorrectIndices
