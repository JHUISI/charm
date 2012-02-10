from toolbox.pairinggroup import *
from charm.engine.util import *

bodyKey = 'Body'

def runBLS_Ind(verifyArgsDict, group, verifyFuncArgs):

	numSigs = len(verifyArgsDict)

	incorrectSigIndices = []

	for sigIndex in range(0, numSigs):
		A , B = verifyArgsDict[sigIndex]['pk'][bodyKey] , verifyArgsDict[sigIndex]['sig'][bodyKey]
		h = group.hash( verifyArgsDict[sigIndex]['message'][bodyKey] , G1 )
		if pair( verifyArgsDict[sigIndex]['sig'][bodyKey] , verifyArgsDict[sigIndex]['pk'][bodyKey][ 'g' ] ) == pair( h , verifyArgsDict[sigIndex]['pk'][bodyKey][ 'g^x' ] )  :
			pass
		else:
			incorrectSigIndices.append(sigIndex)

	return incorrectSigIndices
