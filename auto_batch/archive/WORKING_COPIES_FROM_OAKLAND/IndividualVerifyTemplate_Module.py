from charm.engine.util import *
from toolbox.pairinggroup import *

bodyKey = 'Body'


def runBLS_Ind(verifyArgsDict, group, verifyFuncArgs):

	numSigs = len(verifyArgsDict)

	incorrectSigIndices = []

