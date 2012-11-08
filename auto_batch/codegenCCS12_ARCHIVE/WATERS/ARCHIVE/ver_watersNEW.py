from charm.pairing import *
from toolbox.iterate import dotprod
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
import hashlib
import sys, random, string
from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys

group = None
lam_func = None
hashObj = None
debug = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group , lam_func , hashObj , debug 
	debug = False 
	group = groupObj 
	lam_func = lambda i , a , b : a [ i ] ** b [ i ] 
	hashObj = hashlib.new( 'sha1' ) 

def sha1( message ) : 
	h = hashObj.copy( ) 
	h.update( bytes( message , 'utf-8' ) ) 
	return Bytes( h.digest( ) ) 

def strToId( pk , strID ) : 
	'''Hash the identity string and break it up in to l bit pieces''' 
	hash = sha1( strID ) 
	val = Conversion.OS2IP( hash ) #Convert to integer format 
	bstr = bin( val ) [ 2 : ]   #cut out the 0b header 

	v = [ ] 
	for i in range( pk [ 'z' ] ) :  #z must be greater than or e qual to 1 
		binsubstr = bstr [ pk [ 'l' ] * i : pk [ 'l' ] *( i + 1 ) ] 
		intval = int( binsubstr , 2 ) 
		intelement = group.init( ZR , intval ) 
		v.append( intelement ) 
	return v 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, dotA, dotB, dotD, sumE, A, delta):
	group = groupObj

	l = 5

	lam_func = lambda i,a,b: a[i] ** b[i]

	__init__(group)

	dotF_loopVal = group.init(GT, 1)
	for y in range(0, l):
		dotC_loopVal = group.init(G1, 1)
		for z in range(startSigNum, endSigNum):
			k = strToId( verifyArgsDict[z]['mpk'][bodyKey] , verifyArgsDict[z]['ID'][bodyKey] )
			m = strToId( verifyArgsDict[z]['mpk'][bodyKey] , verifyArgsDict[z]['M'][bodyKey] )
			( S1 , S2 , S3 ) = verifyArgsDict[z]['sig'][bodyKey][ 'S1' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S2' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S3' ]

			dotC_loopVal = dotC_loopVal *  ( S2 **( delta [ z ] * k [ y ] ) * S3 **( delta [ z ] * m [ y ] ) )  

		dotF_loopVal = dotF_loopVal *   pair( dotC_loopVal , verifyArgsDict[0]['mpk'][bodyKey] [ 'ub' ] [ y ] )  

	dotA_loopVal = group.init(G1, 1)
	dotB_loopVal = group.init(G1, 1)
	dotD_loopVal = group.init(G1, 1)
	sumE_loopVal = group.init(ZR, 0)

	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]
		dotB_loopVal = dotB_loopVal * dotB[index]
		dotD_loopVal = dotD_loopVal * dotD[index]
		sumE_loopVal = sumE_loopVal + sumE[index]

	if ( ( pair( dotA_loopVal , verifyArgsDict[0]['mpk'][bodyKey] [ 'g2' ] ) *(( pair( dotB_loopVal , verifyArgsDict[0]['mpk'][bodyKey] [ 'u1b' ] ) * dotF_loopVal ) * pair( dotD_loopVal , verifyArgsDict[0]['mpk'][bodyKey] [ 'u2b' ] ) ) ) == A ** sumE_loopVal   ):
		return
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, dotA, dotB, dotD, sumE, A, delta)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, dotA, dotB, dotD, sumE, A, delta)
