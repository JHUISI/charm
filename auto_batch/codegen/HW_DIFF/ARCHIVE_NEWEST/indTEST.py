from toolbox.PKSig import PKSig
from math import *
from charm.engine.util import *
import sys, random, string
from toolbox.pairinggroup import *
import sys
group = None
bodyKey = 'Body'
def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))
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
	delta = {}
	for z in range(0, N):
		delta[z] = prng_bits(80)
		#print(delta[z])
		#delta[z] = group.init(ZR, 468536023931948155953145)

	for z in range(0, N):

		M= group.hash( verifyArgsDict[z]['msg'][bodyKey] , ZR )
		sigma1 , sigma2= verifyArgsDict[z]['sig'][bodyKey][ 1 ] , verifyArgsDict[z]['sig'][bodyKey][ 2 ]
		r , s= verifyArgsDict[z]['sig'][bodyKey][ 'r' ] , verifyArgsDict[z]['sig'][bodyKey][ 'i' ]
		S= group.init( ZR , s )
		U , V , D= verifyArgsDict[z]['pk'][bodyKey][ 'U' ] , verifyArgsDict[z]['pk'][bodyKey][ 'V' ] , verifyArgsDict[z]['pk'][bodyKey][ 'D' ]
		n= ceilog( s )
		rhs_pair= pair( sigma2 ,( verifyArgsDict[z]['pk'][bodyKey][ 'w2' ] * n ) *( verifyArgsDict[z]['pk'][bodyKey][ 'z2' ] ** S ) * verifyArgsDict[z]['pk'][bodyKey][ 'h2' ] )

		#if( pair( sigma1 , verifyArgsDict[z]['pk'][bodyKey][ 'g2' ] )==( U ** M ) *( V ** r ) * D * rhs_pair ) :

		dotA = sigma1 ** delta[z]
		dotB = U ** (M * delta[z])
		dotC = V ** (r * delta[z])
		dotD = D ** delta[z]
		dotE = sigma2 ** (delta[z] * n)
		dotF = sigma2 ** (delta[z] * S)
		dotG = sigma2 ** delta[z]

		if( pair( dotA , verifyArgsDict[z]['pk'][bodyKey][ 'g2' ] )== (dotB * (dotC * (dotD * (pair(dotE, verifyArgsDict[z]['pk'][bodyKey]['w2']) * (pair(dotF, verifyArgsDict[z]['pk'][bodyKey]['z2']) * pair(dotG, verifyArgsDict[z]['pk'][bodyKey]['h2']))))))):
			pass
		else:
			if z not in incorrectIndices:
				incorrectIndices.append(z)

	return incorrectIndices

'''
Final version => e(dotA,pk#4?) == (dotB * (dotC * (dotD * (e(dotE,pk#7?) * (e(dotF,pk#9?) * e(dotG,pk#11?)))))) 

Compute:  dotA := (prod{z := 0,N} on sigma1_z^delta_z)
Compute:  dotB := (prod{z := 0,N} on U_z^(M_z * delta_z))
Compute:  dotC := (prod{z := 0,N} on V_z^(r_z * delta_z))
Compute:  dotD := (prod{z := 0,N} on D_z^delta_z)
Compute:  dotE := (prod{z := 0,N} on sigma2_z^(delta_z * n))
Compute:  dotF := (prod{z := 0,N} on sigma2_z^(delta_z * S))
Compute:  dotG := (prod{z := 0,N} on sigma2_z^delta_z)
'''

#pk = {'U':U, 'V':V, 'D':D, 'g1':g1, 'g2':g2, 'A':A, 'w1':w1, 'w2':w2, 'z1':z1, 'z2':z2, 'h1':h1, 'h2':h2, 'u':u, 'v':v, 'd':d, 's':s }
