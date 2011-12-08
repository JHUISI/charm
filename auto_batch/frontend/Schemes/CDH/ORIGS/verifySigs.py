from toolbox.pairinggroup import *

bodyKey = 'Body'

def verifySigsRecursive(verifyFuncArgs, verifyArgsDict, dotA, dotB, dotC, mpk_0, a, h, startIndex, endIndex, group, incorrectIndices):


	H = lambda prefix,x: group.H((str(prefix), str(x)), G1)
	H3 = lambda a,b: group.H(('3', str(a), str(b)), ZR)


	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G2, 1)
	dotC_runningProduct = group.init(G2, 1)

	for index in range(startIndex, endIndex):
		dotA_runningProduct = dotA_runningProduct * dotA[index]
		dotB_runningProduct = dotB_runningProduct * dotB[index]
		dotC_runningProduct = dotC_runningProduct * dotC[index]

	if pair ( dotA_runningProduct , mpk_0 ) == ( pair ( a , dotB_runningProduct ) * pair ( h , dotC_runningProduct ) ):
		return
	else:
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			incorrectIndices.append(startIndex)
			return
		midIndex = startIndex + midWay
		verifySigsRecursive(verifyFuncArgs, verifyArgsDict, dotA, dotB, dotC, mpk_0, a, h, startIndex, midIndex, group, incorrectIndices)
		verifySigsRecursive(verifyFuncArgs, verifyArgsDict, dotA, dotB, dotC, mpk_0, a, h, midIndex, endIndex, group, incorrectIndices)
