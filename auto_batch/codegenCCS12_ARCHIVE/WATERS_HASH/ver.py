from toolbox.pairinggroup import *
from toolbox.iterate import dotprod
from charm.engine.util import *
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
import sys, random, string
import hashlib
import sys

group = None
debug = None
hashObj = None
lam_func = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group , debug , hashObj 
	group= groupObj 
	debug= False 
	hashObj= hashlib.new( 'sha1' ) 

def sha1( message ) : 
	h= hashObj.copy( ) 
	h.update( bytes( message , 'utf-8' ) ) 
	return Bytes( h.digest( ) ) 

def strToId( pk , strID ) : 
	'''Hash the identity string and break it up in to l bit pieces''' 
	hash= sha1( strID ) 
	val= Conversion.OS2IP( hash ) #Convert to integer format 
	bstr= bin( val ) [ 2 : ]   #cut out the 0b header 

	v= [ ] 
	for i in range( pk [ 'z' ] ) :  #z must be greater than or equal to 1 
		pass
		binsubstr= bstr [ pk [ 'l' ] * i : pk [ 'l' ] *( i + 1 ) ] 
		intval= int( binsubstr , 2 ) 
		intelement= group.init( ZR , intval ) 
		v.append( intelement ) 
	return v 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, delta, dotA, dotB):
	z = 0

	group = groupObj

	lam_func = lambda i,a,b: a[i] ** b[i]

	__init__(group)


	dotA_loopVal = group.init(G1, 1)
	dotB_loopVal = group.init(G1, 1)

	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]
		dotB_loopVal = dotB_loopVal * dotB[index]

	if (  pair( dotA_loopVal , verifyArgsDict[z]['pk'][bodyKey] [ 'g^x' ] )== pair( dotB_loopVal , verifyArgsDict[z]['pk'][bodyKey] [ 'g' ] )   ):
		return
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			if startSigNum not in incorrectIndices:
				incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, delta, dotA, dotB)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, delta, dotA, dotB)
