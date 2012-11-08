from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import PairingGroup,G1,G2,GT,ZR,pair
import sys

group = None
H = None
debug = None
H = None
H3 = None
bodyKey = 'Body'

def __init__( groupObj ) : 
	global group , H , debug 
	group= groupObj 
	debug= False 

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global H, debug, H, H3
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	incorrectIndices = []
	H3 = lambda a,b: group.hash(('3', str(a), str(b)), ZR)
	H = lambda prefix,x: group.hash((str(prefix), str(x)), G1)
	__init__(group)

	for z in range(0, N):
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		a= H( 1 , verifyArgsDict[z]['M'][bodyKey][ 't1' ] )
		h= H( 2 , verifyArgsDict[z]['M'][bodyKey][ 't2' ] )
		b= H3( verifyArgsDict[z]['M'][bodyKey][ 'str' ] , verifyArgsDict[z]['M'][bodyKey][ 't3' ] )
		if pair( verifyArgsDict[z]['sig'][bodyKey] , verifyArgsDict[z]['mpk'][bodyKey][ 'g' ] )==( pair( a , verifyArgsDict[z]['pk'][bodyKey] ) *( pair( h , verifyArgsDict[z]['pk'][bodyKey] ) ** b ) ) :
			pass
		else:
			incorrectIndices.append(z)

	return incorrectIndices
