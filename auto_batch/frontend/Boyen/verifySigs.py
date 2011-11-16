from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
import sys, copy
from charm.engine.util import *
from toolbox.pairinggroup import *

bodyKey = 'Body'

def verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotC, sumE, D, startIndex, endIndex):
	#group = pairing('../../../param/d224.param')

	group = pairing(80)
	H = lambda a: group.H(('1', str(a)), ZR)
	for arg in verifyFuncArgs:
		argSigIndexMap[arg] = 0

	dotD_runningProduct = group.init(GT, 1)
	sumE_runningProduct = group.init(ZR, 0)
	dotD_runningProduct = group.init(GT, 1)
	for y in range(0, l):
		dotA_runningProduct = group.init(G1, 1)
		dotB_runningProduct = group.init(G1, 1)
		dotC_runningProduct = group.init(G1, 1)
		for z in range(startIndex, EndIndex):
			for arg in verifyFuncArgs:
				if (sigNumKey in verifyArgsDict[z][arg]):
					argSigIndexMap[arg] = int(verifyArgsDict[z][arg][sigNumKey])
				else:
					argSigIndexMap[arg] = z

			Atpk = { }
			Btpk = { }
			Ctpk = { }
			Atpk [ 0 ] = verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'At'  ]
			Btpk [ 0 ] = verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'Bt'  ]
			Ctpk [ 0 ] = verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'Ct'  ]
			for i in pk.keys( )  :
				Atpk [ i ] = verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ i ] [ 'At'  ]
				Btpk [ i ] = verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ i ] [ 'Bt'  ]
				Ctpk [ i ] = verifyArgsDict[argSigIndexMap['pk']]['pk'][bodyKey][ i ] [ 'Ct'  ]


			dotA_runningProduct = dotA_runningProduct * dotA[z]

			dotB_runningProduct = dotB_runningProduct * dotB[z]

			dotC_runningProduct = dotC_runningProduct * dotC[z]

		dotD_runningProduct = dotD_runningProduct *  ( pair ( dotA_runningProduct , Atpk[y] ) * ( pair ( dotB_runningProduct , Btpk[y] ) * pair ( dotC_runningProduct , Ctpk[y] ) )  ) 



	for index in range(startIndex, endIndex):
		sumE_runningProduct = sumE_runningProduct + sumE[index]

	if dotD_runningProduct == D ** sumE_runningProduct:
		return
	else:
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			print("sig " + str(startIndex) + " failed\n")
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotD, sumE, D, startIndex, midIndex)
		verifySigsRecursive(verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotD, sumE, D, midIndex, endIndex)
