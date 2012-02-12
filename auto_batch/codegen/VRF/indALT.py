from toolbox.pairinggroup import *
from toolbox.iterate import dotprod
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string
import sys

group = None
lam_func = None
debug = None
bodyKey = 'Body'

def __init__( groupObj ) : 
	global group , lam_func , debug 
	group= groupObj 
	debug= False 
	lam_func= lambda i , a , b : a [ i ] ** b [ i ] 

def run_Ind(verifyArgsDict, groupObjParam, verifyFuncArgs):
	global group
	global lam_func, debug
	group = groupObjParam

	N = len(verifyArgsDict)
	z = 0
	n , y , pi , pi_0= verifyArgsDict[z]['pk'][bodyKey][ 'n' ] , verifyArgsDict[z]['st'][bodyKey][ 'y' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi0' ]
	incorrectIndices = []
	lam_func = lambda i,a,b: a[i] ** b[i]
	__init__(group)

	for z in range(0, N):
		#for arg in verifyFuncArgs:
			#if (group.ismember(verifyArgsDict[z][arg][bodyKey]) == False):
				#sys.exit("ALERT:  Group membership check failed!!!!\n")

		pass

		n , y , pi , pi_0= verifyArgsDict[z]['pk'][bodyKey][ 'n' ] , verifyArgsDict[z]['st'][bodyKey][ 'y' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi' ] , verifyArgsDict[z]['st'][bodyKey][ 'pi0' ]
		# check first index
		check1= pair( pi [ 0 ] , verifyArgsDict[z]['pk'][bodyKey][ 'g2' ] )
		if verifyArgsDict[z]['x'][bodyKey][ 0 ]== 0 and check1== pair( verifyArgsDict[z]['pk'][bodyKey][ 'g1' ] , verifyArgsDict[z]['pk'][bodyKey][ 'U_t' ] ) :
			if debug : print( "Verify: check 0 successful!\t\tcase:" , verifyArgsDict[z]['x'][bodyKey][ 0 ] )
		elif verifyArgsDict[z]['x'][bodyKey][ 0 ]== 1 and check1== pair( verifyArgsDict[z]['pk'][bodyKey][ 'U1' ] [ 0 ] , verifyArgsDict[z]['pk'][bodyKey][ 'U_t' ] ) :
			if debug : print( "Verify: check 0 successful!\t\tcase:" , verifyArgsDict[z]['x'][bodyKey][ 0 ] )
		else :
			if debug : print( "Verify: check 0 FAILURE!\t\tcase:" , verifyArgsDict[z]['x'][bodyKey][ 0 ] )
			incorrectIndices.append(z)
		for i in range( 1 , len( verifyArgsDict[z]['x'][bodyKey] ) ) :
			pass
			check2= pair( pi [ i ] , verifyArgsDict[z]['pk'][bodyKey][ 'g2' ] )
			if verifyArgsDict[z]['x'][bodyKey][ i ]== 0 and check2== pair( pi [ i -1 ] , verifyArgsDict[z]['pk'][bodyKey][ 'g2' ] ) :
				if debug : print( "Verify: check" , i , "successful!\t\tcase:" , verifyArgsDict[z]['x'][bodyKey][ i ] )
			elif verifyArgsDict[z]['x'][bodyKey][ i ]== 1 and check2== pair( pi [ i -1 ] , verifyArgsDict[z]['pk'][bodyKey][ 'U2' ] [ i ] ) :
				if debug : print( "Verify: check" , i , "successful!\t\tcase:" , verifyArgsDict[z]['x'][bodyKey][ i ] )
			else :
				if debug : print( "Verify: check" , i , "FAILURE!\t\tcase:" , verifyArgsDict[z]['x'][bodyKey][ i ] )
				incorrectIndices.append(z)
#        if pair(pi_0, pk['g2'])== pair(pi[n-1], pk['U2'][0]) and pair(pi_0, pk['h'])== y:
		if pair( pi_0 , verifyArgsDict[z]['pk'][bodyKey][ 'g2' ] * verifyArgsDict[z]['pk'][bodyKey][ 'h' ] )== pair( pi [ n -1 ] , verifyArgsDict[z]['pk'][bodyKey][ 'U2' ] [ 0 ] ) * y :
			pass
		else:
			if z not in incorrectIndices:
				incorrectIndices.append(z)

	return incorrectIndices
