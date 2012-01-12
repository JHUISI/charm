from toolbox.iterate import dotprod
from toolbox.conversion import Conversion
from toolbox.bitstring import Bytes
from toolbox.PKSig import PKSig
from toolbox.pairinggroup import *
from charm.engine.util import *
import hashlib
import sys, copy
from charm.engine.util import *
from toolbox.pairinggroup import *

bodyKey = 'Body'

def verifySigsRecursive(group, deltaz, verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotD, sumE, mpk_1, mpk_6, mpk_7, A, startIndex, endIndex):

	l = 5

	sigNumKey = 'Signature_Number'

	hashObj = hashlib.new('sha1')

	lam_func = lambda i,a,b: a[i] ** b[i]
	for arg in verifyFuncArgs:
		argSigIndexMap[arg] = 0

	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G1, 1)
	dotF_runningProduct = group.init(GT, 1)
	dotD_runningProduct = group.init(G1, 1)
	sumE_runningProduct = group.init(ZR, 0)
	dotF_runningProduct = group.init(GT, 1)
	for y in range(0, l):
		dotC_runningProduct = group.init(G1, 1)
		for z in range(startIndex, endIndex):
			for arg in verifyFuncArgs:
				if (sigNumKey in verifyArgsDict[z][arg]):
					argSigIndexMap[arg] = int(verifyArgsDict[z][arg][sigNumKey])
				else:
					argSigIndexMap[arg] = z

			h = hashObj.copy(  )
			h.update( bytes( verifyArgsDict[argSigIndexMap['ID']]['ID'][bodyKey] , 'utf-8' )  )
			hash = Bytes( h.digest( )  )
			val = Conversion.OS2IP( hash )
			bstr = bin( val ) [ 2 :  ]
			v = [  ]
			for i in range( verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'x' ] )  :
				binsubstr = bstr [ verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'l' ] * i : verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'l' ] *( i + 1 )  ]
				intval = int( binsubstr , 2 )
				intelement = group.init( ZR , intval )
				v.append( intelement )
			k = v
			h = hashObj.copy(  )
			h.update( bytes( verifyArgsDict[argSigIndexMap['M']]['M'][bodyKey] , 'utf-8' )  )
			hash = Bytes( h.digest( )  )
			val = Conversion.OS2IP( hash )
			bstr = bin( val ) [ 2 :  ]
			v = [  ]
			for i in range( verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'x' ] )  :
				binsubstr = bstr [ verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'l' ] * i : verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey][ 'l' ] *( i + 1 )  ]
				intval = int( binsubstr , 2 )
				intelement = group.init( ZR , intval )
				v.append( intelement )
			m = v
			S2 = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'S2' ]
			S3 = verifyArgsDict[argSigIndexMap['sig']]['sig'][bodyKey][ 'S3' ]


			dotC_runningProduct = dotC_runningProduct *  ( S2 ** ( deltaz[z] * k[y] ) * S3 ** ( deltaz[z] * m[y] )  ) 

		dotF_runningProduct = dotF_runningProduct *  pair ( dotC_runningProduct ,  verifyArgsDict[argSigIndexMap['mpk']]['mpk'][bodyKey]['ub'][y] ) 



	for index in range(startIndex, endIndex):
		dotA_runningProduct = dotA_runningProduct * dotA[index]
		dotB_runningProduct = dotB_runningProduct * dotB[index]
		dotD_runningProduct = dotD_runningProduct * dotD[index]
		sumE_runningProduct = sumE_runningProduct + sumE[index]

	if ( pair ( dotA_runningProduct , mpk_1 ) * ( ( pair ( dotB_runningProduct , mpk_6 ) * dotF_runningProduct ) * pair ( dotD_runningProduct , mpk_7 ) ) ) == A ** sumE_runningProduct:
		return
	else:
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			print("sig " + str(startIndex) + " failed\n")
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(group, deltaz, verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotD, sumE, mpk_1, mpk_6, mpk_7, A, startIndex, midIndex)
		verifySigsRecursive(group, deltaz, verifyFuncArgs, argSigIndexMap, verifyArgsDict, dotA, dotB, dotD, sumE, mpk_1, mpk_6, mpk_7, A, midIndex, endIndex)
