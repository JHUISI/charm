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

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global debug, hashObj, lam_func
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	incorrectIndices = []
	lam_func = lambda i,a,b: a[i] ** b[i]
	__init__(group)

	for z in range(0, N):
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		#M= verifyArgsDict[z]['message'][bodyKey]
		#h= group.hash( M , G1 )
		M= strToId( verifyArgsDict[z]['mpk'][bodyKey] , verifyArgsDict[z]['message'][bodyKey] )
		#print( "M :=" , M )
		h= verifyArgsDict[z]['mpk'][bodyKey][ 'u0' ] * dotprod( 1 , -1 , verifyArgsDict[z]['mpk'][bodyKey][ 'z' ] , lam_func , verifyArgsDict[z]['mpk'][bodyKey][ 'u' ] , M )
		#print( "h :=" , h )
		sig= verifyArgsDict[z]['sigDict'][bodyKey][ 'sig1' ]
		t= verifyArgsDict[z]['sigDict'][bodyKey][ 'sig2' ]
		if pair( sig ,( verifyArgsDict[z]['pk'][bodyKey][ 'g' ] ** t ) )==( pair( h , verifyArgsDict[z]['pk'][bodyKey][ 'g^x' ] ) ** t ) :
			pass
		else:
			if z not in incorrectIndices:
				incorrectIndices.append(z)

	return incorrectIndices
