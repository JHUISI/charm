from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from toolbox.pairinggroup import PairingGroup,G1,G2,GT,ZR,pair
import sys

group = None
debug = None
H1 = None
H2 = None
lam_func = None
bodyKey = 'Body'

def __init__( groupObj ) : 
	global group , debug 
	group = groupObj 
	debug = False 

def concat( L_id ) : 
	result = "" 
	for i in L_id : 
		result + = ":" + i 
	return result 

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global debug, H1, H2, lam_func
	group = groupObjParam

	N = len(verifyArgsDict)
	l = 5
	incorrectIndices = []
	H1 = lambda x: group.hash(('1', str(x)), G1)
	H2 = lambda a, b, c: group.hash(('2', a, b, c), ZR)
	lam_func = lambda i,a,b,c: a[i] * (b[i] ** c[i]) # => u * (pk ** h) for all signers
	__init__(group)

	for z in range(0, N):
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		u , S = verifyArgsDict[z]['sig'][bodyKey][ 'u' ] , verifyArgsDict[z]['sig'][bodyKey][ 'S' ]
		Lt = concat( verifyArgsDict[z]['L'][bodyKey] )
		num_signers = len( verifyArgsDict[z]['L'][bodyKey] )
		h = [ group.init( ZR , 1 ) for i in range( num_signers ) ]
		for i in range( num_signers ) :
			h [ i ] = H2( verifyArgsDict[z]['M'][bodyKey] , Lt , u [ i ] )
		pk = [ H1( i ) for i in verifyArgsDict[z]['L'][bodyKey] ] # get all signers pub keys
		result = dotprod( group.init( G1 ) , -1 , num_signers , lam_func , u , pk , h )
		if pair( result , verifyArgsDict[z]['mpk'][bodyKey][ 'Pub' ] ) == pair( S , verifyArgsDict[z]['mpk'][bodyKey][ 'g' ] ) :
			pass
		else:
			incorrectIndices.append(z)

	return incorrectIndices
