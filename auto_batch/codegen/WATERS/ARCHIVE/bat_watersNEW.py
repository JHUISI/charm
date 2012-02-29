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
from toolbox.pairinggroup import *
from WATERS/ver_watersNEW import verifySigsRecursive

group = None
lam_func = None
hashObj = None
debug = None
bodyKey = 'Body'

def prng_bits(bits=80):
	return group.init(ZR, randomBits(bits))

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

def run_Batch(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global lam_func, hashObj, debug
	group = groupObjParam

	N = len(verifyArgsDict)
	l = 5
	delta = {}
	for z in range(0, N):
		delta[z] = prng_bits(80)

	incorrectIndices = []
	lam_func = lambda i,a,b: a[i] ** b[i]
	__init__(group)


	for z in range(0, N):
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

	dotA = {}
	dotB = {}
	dotD = {}
	sumE = {}

	for z in range(0, N):
		( S1 , S2 , S3 ) = verifyArgsDict[z]['sig'][bodyKey][ 'S1' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S2' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S3' ]

		dotA[z] =   S1 ** delta [ z ]  
		dotB[z] =   S2 ** delta [ z ]  
		dotD[z] =   S3 ** delta [ z ]  
		sumE[z] =   delta [ z ]  

	A , g2 = verifyArgsDict[z]['mpk'][bodyKey][ 'A' ] , verifyArgsDict[z]['mpk'][bodyKey][ 'g2' ]

	verifySigsRecursive(verifyArgsDict, group, incorrectIndices, 0, N, dotA, dotB, dotD, sumE, A, delta)

	return incorrectIndices
