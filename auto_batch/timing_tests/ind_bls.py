from toolbox.pairinggroup import *

message = 1337

bodyKey = 'Body'

def runBLS_Ind(verifyArgsDict, group, verifyFuncArgs):

	numSigs = len(verifyArgsDict)

	incorrectSigIndices = []

	for sigIndex in range(0, numSigs):

		if group.ismember(verifyArgsDict[sigIndex]['sig'][bodyKey]) == False:
			sys.exit("The sig member of signature number " + sigIndex + " has failed the group membership check.  Exiting.\n")

		if (type(verifyArgsDict[sigIndex][message][bodyKey]) != str):
			sys.exit("The message member of signature number " + sigIndex + " has failed the group membership check.  Exiting.\n")

		if group.ismember(verifyArgsDict[sigIndex]['pk'][bodyKey][ 'g' ]) == False:
			sys.exit("The g member of signature number " + sigIndex + " has failed the group membership check.  Exiting.\n")

		if group.ismember(verifyArgsDict[sigIndex]['pk'][bodyKey][ 'g^x' ]) == False:
			sys.exit("The g ^ x member of signature number " + sigIndex + " has failed the group membership check.  Exiting.\n")







		h = group.hash( verifyArgsDict[sigIndex][message][bodyKey] , G1 )
		if pair( verifyArgsDict[sigIndex]['sig'][bodyKey] , verifyArgsDict[sigIndex]['pk'][bodyKey][ 'g' ] ) == pair( h , verifyArgsDict[sigIndex]['pk'][bodyKey][ 'g^x' ] )  :
			pass
		else:
			incorrectSigIndices.append(sigIndex)

	return incorrectSigIndices
