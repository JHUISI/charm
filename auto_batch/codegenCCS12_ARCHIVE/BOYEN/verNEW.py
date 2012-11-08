from toolbox.pairinggroup import *
from toolbox.PKSig import PKSig
import sys

group = None
debug = None
H = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group , debug 
	group= groupObj 
	debug= False 

def getPKdict( mpk , pk , k ) : 
	A_pk , B_pk , C_pk= { } , { } , { } 
	A_pk [ 0 ]= mpk [ k [ 0 ] ] 
	B_pk [ 0 ]= mpk [ k [ 1 ] ] 
	C_pk [ 0 ]= mpk [ k [ 2 ] ] 
	for i in pk.keys( ) : 
		pass
		A_pk [ i ]= pk [ i ] [ k [ 0 ] ] 
		B_pk [ i ]= pk [ i ] [ k [ 1 ] ] 
		C_pk [ i ]= pk [ i ] [ k [ 2 ] ] 
	return A_pk , B_pk , C_pk 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, D, delta, dotD):
	z = 0

	group = groupObj

	At , Bt , Ct= getPKdict( verifyArgsDict[z]['mpk'][bodyKey] , verifyArgsDict[z]['pk'][bodyKey] , [ 'At' , 'Bt' , 'Ct' ] )
	l= len( At.keys( ) )
	H = lambda a: group.hash(('1', str(a)), ZR)

	__init__(group)

	dotE_loopVal = group.init(GT, 1)
	for y in range(0, l):
		dotA_loopVal = group.init(G1, 1)
		dotB_loopVal = group.init(G1, 1)
		dotC_loopVal = group.init(G1, 1)
		for z in range(startSigNum, endSigNum):
			S , t= verifyArgsDict[z]['sig'][bodyKey][ 'S' ] , verifyArgsDict[z]['sig'][bodyKey][ 't' ]
			m= H( verifyArgsDict[z]['M'][bodyKey] )

			dotA_loopVal = dotA_loopVal *   S [ y ] ** delta [ z ]  
			dotB_loopVal = dotB_loopVal *   S [ y ] **( m * delta [ z ] )  
			dotC_loopVal = dotC_loopVal *   S [ y ] **( t [ y ] * delta [ z ] )  
		At , Bt , Ct= getPKdict( verifyArgsDict[z]['mpk'][bodyKey] , verifyArgsDict[z]['pk'][bodyKey] , [ 'At' , 'Bt' , 'Ct' ] )

		dotE_loopVal = dotE_loopVal *  ( pair( dotA_loopVal , At [ y ] ) *( pair( dotB_loopVal , Bt [ y ] ) * pair( dotC_loopVal , Ct [ y ] ) ) )  

	dotD_loopVal = group.init(GT, 1)

	for index in range(startSigNum, endSigNum):
		dotD_loopVal = dotD_loopVal * dotD[index]

	if (  dotE_loopVal== dotD_loopVal   ):
		return
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			if startSigNum not in incorrectIndices:
				incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, D, delta, dotD)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, D, delta, dotD)
