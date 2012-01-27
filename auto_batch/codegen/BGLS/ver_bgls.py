import sys, random, string
from charm.engine.util import *
from toolbox.pairinggroup import *
import sys

group = None
g2 = None
debug = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group , g2 , debug 
	group= groupObj 
	g2= group.random( G2 ) 
	debug= False 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, delta, dotA):
	z = 0

	group = groupObj

	l = 5

	__init__(group)

	dotC_loopVal = group.init(GT, 1)
	for y in range(0, l):
		dotB_loopVal = group.init(G1, 1)
		for z in range(startSigNum, endSigNum):
			for index in range( 0 , len( verifyArgsDict[z]['M'][bodyKey] ) ) :
				pass
				h= group.hash( verifyArgsDict[z]['M'][bodyKey][ index ] , G1 )

			dotB_loopVal = dotB_loopVal *   h ** delta [ z ]  

		#print("start")
		#print(dotB_loopVal,verifyArgsDict[z]['pk'][bodyKey][y]['g^x'])
		#print("end")

		#print(dotB_loopVal.type)
		print(verifyArgsDict[z]['pk'][bodyKey][y]['g^x'])

		dotC_loopVal=dotC_loopVal*pair(dotB_loopVal,verifyArgsDict[z]['pk'][bodyKey][y]['g^x'])  

	dotA_loopVal = group.init(G1, 1)

	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]

	if (  pair( dotA_loopVal , verifyArgsDict[z]['pk'][bodyKey] [ 'g2' ] )== dotC_loopVal   ):
		return
	else:
		midWay = int( (endSigNum - startSigNum) / 2)
		if (midWay == 0):
			incorrectIndices.append(startSigNum)
			return
		midSigNum = startSigNum + midWay
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, startSigNum, midSigNum, delta, dotA)
		verifySigsRecursive(verifyArgsDict, group, incorrectIndices, midSigNum, endSigNum, delta, dotA)
