from toolbox.pairinggroup import *

bodyKey = 'Body'

def verifySigsRecursive_O1(verifyFuncArgs, verifyArgsDict, dotA, dotB, pk_0, pk_1, startIndex, endIndex, group, incorrectSigIndices, BATCH_SIZE, INVALID_SIGNATURE_FRACTION):

	print("startIndex:  ", startIndex)
	print("endIndex:  ", endIndex)
	print("batchSize:  ", BATCH_SIZE)
	print("invalid signature fraction:  ", INVALID_SIGNATURE_FRACTION)

	SEGMENT_SIZE = (endIndex - startIndex) 
	SEGMENT_FRACTION = float(SEGMENT_SIZE) / float(BATCH_SIZE)
	ONE_MINUS = float(1-(SEGMENT_FRACTION))
	EXPONENT = float(INVALID_SIGNATURE_FRACTION) * float(BATCH_SIZE)
	CALCULATION = float(1-(ONE_MINUS) ** (EXPONENT))
	print("calculation:  ", CALCULATION)
	print("\n\n")
	if (CALCULATION > 0.75) and (startIndex != endIndex):
		midWay = int( (endIndex - startIndex) / 2)
		midIndex = startIndex + midWay
		verifySigsRecursive_O1(verifyFuncArgs, verifyArgsDict, dotA, dotB, pk_0, pk_1, startIndex, midIndex, group, incorrectSigIndices, BATCH_SIZE, INVALID_SIGNATURE_FRACTION)
		verifySigsRecursive_O1(verifyFuncArgs, verifyArgsDict, dotA, dotB, pk_0, pk_1, midIndex, endIndex, group, incorrectSigIndices, BATCH_SIZE, INVALID_SIGNATURE_FRACTION)
		return

	dotA_runningProduct = group.init(G1, 1)
	dotB_runningProduct = group.init(G1, 1)

	for index in range(startIndex, endIndex):
		dotA_runningProduct = dotA_runningProduct * dotA[index]
		dotB_runningProduct = dotB_runningProduct * dotB[index]

	if pair ( dotA_runningProduct , pk_0 ) == pair ( dotB_runningProduct , pk_1 ):
		return
	else:
		midWay = int( (endIndex - startIndex) / 2)
		if (midWay == 0):
			incorrectSigIndices.append(startIndex)
			return
		midIndex = startIndex + midWay
		verifySigsRecursive_O1(verifyFuncArgs, verifyArgsDict, dotA, dotB, pk_0, pk_1, startIndex, midIndex, group, incorrectSigIndices, BATCH_SIZE, INVALID_SIGNATURE_FRACTION)
		verifySigsRecursive_O1(verifyFuncArgs, verifyArgsDict, dotA, dotB, pk_0, pk_1, midIndex, endIndex, group, incorrectSigIndices, BATCH_SIZE, INVALID_SIGNATURE_FRACTION)
		return
