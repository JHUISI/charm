from toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from toolbox.iterate import dotprod
import sys

group = None
lam_func = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group , lam_func 
	group= groupObj 
	lam_func= lambda i , a , b : a [ i ] ** b [ i ] 

def verifySigsRecursive(verifyArgsDict, groupObj, incorrectIndices, startSigNum, endSigNum, delta, dotA, dotB, dotC, dotD, dotE, dotF, dotG):
	z = 0

	group = groupObj

	lam_func = lambda i,a,b: a[i] ** b[i]

	__init__(group)


	dotA_loopVal = group.init(G1, 1)
	dotB_loopVal = group.init(G1, 1)
	dotC_loopVal = group.init(G1, 1)
	dotD_loopVal = group.init(G1, 1)
	dotE_loopVal = group.init(GT, 1)
	dotF_loopVal = group.init(G1, 1)
	dotG_loopVal = group.init(G1, 1)

	for index in range(startSigNum, endSigNum):
		dotA_loopVal = dotA_loopVal * dotA[index]
		dotB_loopVal = dotB_loopVal * dotB[index]
		dotC_loopVal = dotC_loopVal * dotC[index]
		dotD_loopVal = dotD_loopVal * dotD[index]
		dotE_loopVal = dotE_loopVal * dotE[index]
		dotF_loopVal = dotF_loopVal * dotF[index]
		dotG_loopVal = dotG_loopVal * dotG[index]
