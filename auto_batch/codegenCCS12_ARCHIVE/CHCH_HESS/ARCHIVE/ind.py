from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
from schemes.pksig_hess import Hess
from schemes.pksig_chch import CHCH
import sys

group = None
H2 = None
debug = None
bodyKey = 'Body'

def __init__( groupObj ) : 
	global H2 , group , debug 
	group= groupObj 
	debug= False 
	H2= lambda x , y : group.hash(( x , y ) , ZR ) 

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global H2, debug
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	incorrectIndices = []
	H2 = lambda x,y: group.hash((x,y), ZR)
	__init__(group)

	for z in range(0, N):
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		sig1 , sig2= verifyArgsDict[z]['sig'][bodyKey][ 'sig_hess' ] , verifyArgsDict[z]['sig'][bodyKey][ 'sig_chch' ]
		S1h , S2h= sig1 [ 'S1' ] , sig1 [ 'S2' ]
		S1c , S2c= sig2 [ 'S1' ] , sig2 [ 'S2' ]
		ah= H2( verifyArgsDict[z]['M'][bodyKey] , S1h )
		ac= H2( verifyArgsDict[z]['M'][bodyKey] , S1c )
		if pair( S2h , verifyArgsDict[z]['mpk'][bodyKey][ 'g2' ] )==( pair( verifyArgsDict[z]['pk'][bodyKey] , verifyArgsDict[z]['mpk'][bodyKey][ 'P' ] ) ** ah ) * S1h and pair( S2c , verifyArgsDict[z]['mpk'][bodyKey][ 'g2' ] )== pair( S1c *( verifyArgsDict[z]['pk'][bodyKey] ** ac ) , verifyArgsDict[z]['mpk'][bodyKey][ 'P' ] ) :
			pass
		else:
			if z not in incorrectIndices:
				incorrectIndices.append(z)

	return incorrectIndices
