from toolbox.pairinggroup import PairingGroup,G1,G2,GT,ZR,pair
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, random, string
import sys

group = None
debug = None
H1 = None
H2 = None
lam_func = None
bodyKey = 'Body'

def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def concat( L_id ) : 
	result= "" 
	for i in L_id : 
		pass
		result += ":" + i 
	return result 

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global debug, H1, H2, lam_func
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	l= len( verifyArgsDict[z]['L'][bodyKey] )
	incorrectIndices = []
	lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i]) # => u * (pk ** h) for all signers
	H1 = lambda x: group.hash(('1', str(x)), G1)
	H2 = lambda a, b, c: group.hash(('2', a, b, c), ZR)
	__init__(group)

	for z in range(0, N):
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		u , S= verifyArgsDict[z]['sig'][bodyKey][ 'u' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S' ]
		Lt= concat( verifyArgsDict[z]['L'][bodyKey] )
		l= len( verifyArgsDict[z]['L'][bodyKey] )
		h= [ group.init( ZR , 1 ) for i in range( l ) ]
		for i in range( l ) :
			pass
			h [ i ]= H2( verifyArgsDict[z]['M'][bodyKey] , Lt , u [ i ] )
		pk= [ H1( i ) for i in verifyArgsDict[z]['L'][bodyKey] ] # get all signers pub keys
		result= dotprod( group.init( G1 ) , -1 , l , lam_func , u , pk , h )
		if pair( result , verifyArgsDict[z]['mpk'][bodyKey][ 'Pub' ] )== pair( S , verifyArgsDict[z]['mpk'][bodyKey][ 'g' ] ) :
			pass
		else:
			incorrectIndices.append(z)

	return incorrectIndices
