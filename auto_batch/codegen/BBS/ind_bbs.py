from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import *
import sys

group = None
debug = None
bodyKey = 'Body'

def __init__( groupObj ) : 
	PKSig.__init__( self ) 
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

		"""alternative verification check for BGLS04 which allows it to be batched"""
		c , T1 , T2 , T3= verifyArgsDict[z]['sigma'][bodyKey][ 'c' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T1' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T2' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'T3' ]
		s_alpha , s_beta= verifyArgsDict[z]['sigma'][bodyKey][ 's_alpha' ] , verifyArgsDict[z]['sigma'][bodyKey][ 's_beta' ]
		s_x , s_gamma1 , s_gamma2= verifyArgsDict[z]['sigma'][bodyKey][ 's_x' ] , verifyArgsDict[z]['sigma'][bodyKey][ 's_gamma1' ] , verifyArgsDict[z]['sigma'][bodyKey][ 's_gamma2' ]
		R3= verifyArgsDict[z]['sigma'][bodyKey][ 'R3' ]
		R1=( verifyArgsDict[z]['gpk'][bodyKey][ 'u' ] ** s_alpha ) *( T1 ** -c )
		R2=( verifyArgsDict[z]['gpk'][bodyKey][ 'v' ] ** s_beta ) *( T2 ** -c )
		R4=( T1 ** s_x ) *( verifyArgsDict[z]['gpk'][bodyKey][ 'u' ] ** -s_gamma1 )
		R5=( T2 ** s_x ) *( verifyArgsDict[z]['gpk'][bodyKey][ 'v' ] ** -s_gamma2 )
		if c== group.hash(( verifyArgsDict[z]['M'][bodyKey] , T1 , T2 , T3 , R1 , R2 , R3 , R4 , R5 ) , ZR ) :
			if debug : print( "c=> '%s'" % c )
			if debug : print( "Valid Group Signature for message: '%s'" % verifyArgsDict[z]['M'][bodyKey] )
			pass
		else :
			if debug : print( "Not a valid signature for message!!!" )
			return False
		if(( pair( T3 , verifyArgsDict[z]['gpk'][bodyKey][ 'g2' ] ) ** s_x ) *( pair( verifyArgsDict[z]['gpk'][bodyKey][ 'h' ] , verifyArgsDict[z]['gpk'][bodyKey][ 'w' ] ) **( -s_alpha -s_beta ) ) *( pair( verifyArgsDict[z]['gpk'][bodyKey][ 'h' ] , verifyArgsDict[z]['gpk'][bodyKey][ 'g2' ] ) **( -s_gamma1 -s_gamma2 ) ) *( pair( T3 , verifyArgsDict[z]['gpk'][bodyKey][ 'w' ] ) ** c ) *( pair( verifyArgsDict[z]['gpk'][bodyKey][ 'g1' ] , verifyArgsDict[z]['gpk'][bodyKey][ 'g2' ] ) ** -c ) )== R3 :
			pass
		else:
			incorrectIndices.append(z)

	return incorrectIndices
