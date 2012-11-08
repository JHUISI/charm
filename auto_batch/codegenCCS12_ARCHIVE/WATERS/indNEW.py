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
	debug= False 
	group= groupObj 
	lam_func= lambda i , a , b : a [ i ] ** b [ i ] 
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

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global lam_func, hashObj, debug
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	l = 5
	incorrectIndices = []
	lam_func = lambda i,a,b: a[i] ** b[i]
	__init__(group)

	for z in range(0, N):
		for arg in verifyFuncArgs:
			if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		if debug : print( "Verify..." )
		k= strToId( verifyArgsDict[z]['mpk'][bodyKey] , verifyArgsDict[z]['ID'][bodyKey] )
		m= strToId( verifyArgsDict[z]['mpk'][bodyKey] , verifyArgsDict[z]['M'][bodyKey] )
		( S1 , S2 , S3 )= verifyArgsDict[z]['sig'][bodyKey][ 'S1' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S2' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S3' ]
		A , g2= verifyArgsDict[z]['mpk'][bodyKey][ 'A' ] , verifyArgsDict[z]['mpk'][bodyKey][ 'g2' ]
		comp1= dotprod( group.init( G2 ) , -1 , verifyArgsDict[z]['mpk'][bodyKey][ 'z' ] , lam_func , verifyArgsDict[z]['mpk'][bodyKey][ 'ub' ] , k )
		comp2= dotprod( group.init( G2 ) , -1 , verifyArgsDict[z]['mpk'][bodyKey][ 'z' ] , lam_func , verifyArgsDict[z]['mpk'][bodyKey][ 'ub' ] , m )
		if( pair( S1 , g2 ) * pair( S2 , verifyArgsDict[z]['mpk'][bodyKey][ 'u1b' ] * comp1 ) * pair( S3 , verifyArgsDict[z]['mpk'][bodyKey][ 'u2b' ] * comp2 ) )== A :
			pass
		else:
			if z not in incorrectIndices:
				incorrectIndices.append(z)

	return incorrectIndices
