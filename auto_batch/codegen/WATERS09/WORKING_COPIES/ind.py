from toolbox.pairinggroup import *
from toolbox.IBEnc import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from charm.engine.util import *
import sys, random, string
import sys

group = None
util = None
bodyKey = 'Body'

def __init__( groupObj ) : 
	#IBEnc.__init__(self) 
	global group , util 
	group= groupObj 

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global util
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

		s1 , s2 , t , tagc= group.random( ZR , 4 )
		s= s1 + s2
		M= group.hash( verifyArgsDict[z]['m'][bodyKey] )
		sig1 , sig2 , sig3 , sig4 , sig5 , sig6 , sig7 , sigK , tagk= verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 1 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 2 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 3 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 4 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 5 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 6 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'sig' ] [ 7 ] , verifyArgsDict[z]['sigma'][bodyKey][ 'K' ] , verifyArgsDict[z]['sigma'][bodyKey][ 'tagk' ]
		E1=( verifyArgsDict[z]['mpk'][bodyKey][ 'u2' ] **( M * t ) ) *( verifyArgsDict[z]['mpk'][bodyKey][ 'w2' ] **( tagc * t ) ) *( verifyArgsDict[z]['mpk'][bodyKey][ 'h2' ] ** t )
		E2= verifyArgsDict[z]['mpk'][bodyKey][ 'g1' ] ** t
		A= verifyArgsDict[z]['mpk'][bodyKey][ 'egg_alpha' ]
		theta=  ~( tagc -tagk )
		lhs_pair= pair( verifyArgsDict[z]['mpk'][bodyKey][ 'g1^b' ] ** s , sig1 ) * pair( verifyArgsDict[z]['mpk'][bodyKey][ 'g^ba1' ] ** s1 , sig2 ) * pair( verifyArgsDict[z]['mpk'][bodyKey][ 'g^a1' ] ** s1 , sig3 ) * pair( verifyArgsDict[z]['mpk'][bodyKey][ 'g^ba2' ] ** s2 , sig4 ) * pair( verifyArgsDict[z]['mpk'][bodyKey][ 'g^a2' ] ** s2 , sig5 )
		rhs_pair= pair( sig6 ,( verifyArgsDict[z]['mpk'][bodyKey][ 'tau1' ] ** s1 ) *( verifyArgsDict[z]['mpk'][bodyKey][ 'tau2' ] ** s2 ) ) * pair( sig7 ,( verifyArgsDict[z]['mpk'][bodyKey][ 'tau1^b' ] ** s1 ) *( verifyArgsDict[z]['mpk'][bodyKey][ 'tau2^b' ] ** s2 ) *( verifyArgsDict[z]['mpk'][bodyKey][ 'w2' ] ** -t ) ) *(( pair( sig7 , E1 ) / pair( E2 , sigK ) ) ** theta ) *( A ** s2 )
		if lhs_pair== rhs_pair :
			pass
		else:
			if z not in incorrectIndices:
				incorrectIndices.append(z)

	return incorrectIndices
