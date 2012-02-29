from toolbox.PKSig import PKSig
from math import *
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import *
import sys

group = None
bodyKey = 'Body'

def __init__( groupObj ) : 
	global group 
	group= groupObj 

def ceilog( value ) : 
	return group.init( ZR , ceil( log( value , 2 ) ) ) 

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	r , s= verifyArgsDict[z]['sig'][bodyKey][ 'r' ] , verifyArgsDict[z]['sig'][bodyKey][ 'i' ]
	n= ceilog( s )
	incorrectIndices = []
	__init__(group)

	for z in range(0, N):
		for arg in verifyFuncArgs:
			if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		M= group.hash( verifyArgsDict[z]['msg'][bodyKey] , ZR )
		sigma1 , sigma2= verifyArgsDict[z]['sig'][bodyKey][ 1 ] , verifyArgsDict[z]['sig'][bodyKey][ 2 ]
		r , s= verifyArgsDict[z]['sig'][bodyKey][ 'r' ] , verifyArgsDict[z]['sig'][bodyKey][ 'i' ]
		S= group.init( ZR , s )
		U , V , D= verifyArgsDict[z]['pk'][bodyKey][ 'U' ] , verifyArgsDict[z]['pk'][bodyKey][ 'V' ] , verifyArgsDict[z]['pk'][bodyKey][ 'D' ]
		n= ceilog( s )
		rhs_pair= pair( sigma2 ,( verifyArgsDict[z]['pk'][bodyKey][ 'w2' ] * n ) *( verifyArgsDict[z]['pk'][bodyKey][ 'z2' ] ** S ) * verifyArgsDict[z]['pk'][bodyKey][ 'h2' ] )
		if( pair( sigma1 , verifyArgsDict[z]['pk'][bodyKey][ 'g2' ] )==( U ** M ) *( V ** r ) * D * rhs_pair ) :
			pass
		else:
			if z not in incorrectIndices:
				incorrectIndices.append(z)

	return incorrectIndices
