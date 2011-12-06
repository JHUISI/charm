from toolbox.pairinggroup import *

bodyKey = 'Body'

def runCHP_Ind(verifyArgsDict, group, verifyFuncArgs):
	numSigs = len(verifyArgsDict)

	H = lambda prefix,x: group.H((str(prefix), str(x)), G1)
	H3 = lambda a,b: group.H(('3', str(a), str(b)), ZR)

	incorrectIndices = []

	for z in range(0, numSigs):
		if (type(verifyArgsDict[z]['message'][bodyKey][ 't1' ]) != str):
			sys.exit("member check failed")

		if (type(verifyArgsDict[z]['message'][bodyKey][ 't2' ]) != str):
			sys.exit("member check failed")

		if (type(verifyArgsDict[z]['message'][bodyKey][ 'str' ]) != str):
			sys.exit("member check failed")

		if (type(verifyArgsDict[z]['message'][bodyKey][ 't3' ]) != str):
			sys.exit("member check failed")

		if (group.ismember(verifyArgsDict[z]['sig'][bodyKey]) == False):
			sys.exit("member check failed")

		if (group.ismember(verifyArgsDict[z]['mpk'][bodyKey][ 'g' ]) == False):
			sys.exit("member check failed")

		if (group.ismember(verifyArgsDict[z]['pk'][bodyKey]) == False):
			sys.exit("member check failed")


		a = H( 1 , verifyArgsDict[z]['message'][bodyKey][ 't1' ]  )
		h = H( 2 , verifyArgsDict[z]['message'][bodyKey][ 't2' ]  )
		b = H3( verifyArgsDict[z]['message'][bodyKey][ 'str' ] , verifyArgsDict[z]['message'][bodyKey][ 't3' ]  )
		if pair( verifyArgsDict[z]['sig'][bodyKey] , verifyArgsDict[z]['mpk'][bodyKey][ 'g' ] ) ==( pair( a , verifyArgsDict[z]['pk'][bodyKey] ) * pair( h , verifyArgsDict[z]['pk'][bodyKey] ** b ) )  :
			pass
		else:
			incorrectIndices.append(z)

	return incorrectIndices
