from toolbox.pairinggroup import *
from toolbox.PKSig import *
from toolbox.iterate import dotprod
from charm.engine.util import *
from charm.integer import randomBits
from pksig_cdh import *
import random, string, time, sys
from math import *

messageSize = 100
numSigs = 100
numProgramIterations = 30

M_index = 1
sig_index = 2
pk_index = 3
verifyFuncArgs = [M_index, sig_index, pk_index]

def individualVerification(group, cdhObj, dict, msgs, sigs, N):

	for i in range(0, N):
		for arg in verifyFuncArgs:
			if (group.ismember(dict[i][arg]) == False):
				sys.exit("group membership failed")

	for i in range(0, N):
		pk = dict[i][pk_index]

		if cdhObj.verify(pk, msgs[i], sigs[i]) == True:
			continue
		else:
			sys.exit("ind. failed")

def runCDH_batch(dict, group):
	N = len(dict)

	delta = {}

	for sigIndex in range(0, N):
		delta[sigIndex] = group.init(ZR, randomBits(80))

	sumB = group.init(ZR, 0)
	sumD = group.init(ZR, 0)
	sumC = group.init(ZR, 0)
	dotA = group.init(G1, 1)
	dotG = group.init(G1, 1)
	dotE = group.init(G1, 1)
	dotF = group.init(G1, 1)

	for i in range(0, N):
		for arg in verifyFuncArgs:
			if (group.ismember(dict[i][arg]) == False):
				sys.exit("group membership failed")

	for i in range(0, N):
		M = dict[i][M_index]
		M = group.hash(M, ZR)

		r = dict[i][sig_index]['r']
		sig1 = dict[i][sig_index][1]
		sig2 = dict[i][sig_index][2]
		sig_i = dict[i][sig_index]['i']

		sumD = sumD + delta[i]
		sumB = sumB + (M * delta[i])
		sumC = sumC + (r * delta[i])
		dotA = dotA * (sig1 ** delta[i])
		dotG = dotG * (sig2 ** delta[i])
		n = group.init(ZR, ceil(log(sig_i, 2)))

		dotE = dotE * (sig2 ** (n * delta[i] ) )
		dotF = dotF * (sig2 ** (sig_i * delta[i] ) )

	U = dict[0][pk_index]['U']
	V = dict[0][pk_index]['V']
	D = dict[0][pk_index]['D']
	g2 = dict[0][pk_index]['g2']
	z2 = dict[0][pk_index]['z2']
	w2 = dict[0][pk_index]['w2']
	h2 = dict[0][pk_index]['h2']

	leftSide = pair(dotA, g2)
	rightSidePair1 = pair(dotE, w2)
	rightSidePair2 = pair(dotF, z2)
	rightSidePair3 = pair(dotG, h2)
	rightSidePairings = rightSidePair1 * rightSidePair2 * rightSidePair3

	U_right = U ** sumB
	V_right = V ** sumC
	D_right = D ** sumD

	rightSide = (U_right * (V_right * (D_right * (rightSidePairings))))

	if (leftSide == rightSide):
		return
	sys.exit("WTF IS HAPPENING????????")

def randomMessages(count):
    msgList = []
    for i in range(0, count):
        msg = ""
        for index in range(0, messageSize):
            msg = msg + random.choice(string.printable)
        msgList.append(msg)
    return msgList
    
def generateSigs(pk, sk, cdhObj, num_sigs):
    m = randomMessages(num_sigs)
    sig = []
    c = pk['s'] + 1 # set state counter from pk (needs to be consistent, right?)
    for i in range(num_sigs):
        sig.append( cdhObj.sign(pk, sk, c, m[i]) )
        c = c + 1
    
    pk['s'] = c # update the state counter
    return (m, sig)

if __name__ == "__main__":
	groupObj = PairingGroup(MNT160)
	cdh = CDH(groupObj)
	N = numSigs
    
	(pk, sk) = cdh.setup()
    
	(mList, sigList) = generateSigs(pk, sk, cdh, N)
    
	CDH_dict = {}

	for indexVar in range(0, N):
		CDH_dict[indexVar] = {}
		CDH_dict[indexVar][M_index] = mList[indexVar]
		CDH_dict[indexVar][sig_index] = sigList[indexVar]
		CDH_dict[indexVar][pk_index] = pk

	batchOutputFile = open(sys.argv[1], "w")
	indOutputFile = open(sys.argv[2], "w")

	for programIteration in range(0, numProgramIterations):

		#print("program iteration " + str(programIteration))

		for numSigs in range(0, N):
			#print("cycle number:  " + str(numSigs))

			dict = {}
			msgListInd = []
			sigListInd = []

			for loadSig in range(0, (numSigs + 1)):
				dict[loadSig] = CDH_dict[loadSig]
				msgListInd.append(mList[loadSig])
				sigListInd.append(sigList[loadSig])

			startTime = time.clock()
			runCDH_batch(dict, groupObj)
			endTime = time.clock()

			result = (endTime - startTime) * 1000

			batchTimeResult = float(result) / float(numSigs + 1)

			batchOutputFile.write(str(batchTimeResult) + ",")

			startTime = time.clock()
			individualVerification(groupObj, cdh, dict, msgListInd, sigListInd, (numSigs + 1))
			endTime = time.clock()

			result = (endTime - startTime) * 1000

			indTimeResult = float(result) / float(numSigs + 1)

			indOutputFile.write(str(indTimeResult) + ",")

		batchOutputFile.write("\n")
		indOutputFile.write("\n")

	batchOutputFile.close()
	indOutputFile.close()
