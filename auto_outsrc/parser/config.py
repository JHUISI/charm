M = 'M'

blindingLoopVar = "y"
blindingSuffix = "Blinded"
keygenBlindingExponent = "zz"
keygenFuncName = "keygen"
# superset of variables we have used to represent public parameters in
# our crypto schemes
keygenPubVar = ["pk", "mpk", "gpk"]
keygenSecVar = "sk"

setupFileName = "setupOutsourcing.py"
transformFileName = "transformOutsourcing.py"
#decOutFileName = "decOutOutsourcing.cpp"
decOutFileName = "decOutOutsourcing.py"
userFuncsName = "userFuncs"
userFuncsFileName = userFuncsName + ".py"

transformFunctionName = "transform"
partialCT = "partCT"
decOutFunctionName = "decout"

pySuffix = ".py"
#cppSuffix = ".cpp"
cppSuffix = ".py"

setupFunctionOrder = ["setup", "keygen", "encrypt"]
transformFunctionOrder = ["transform"]
decOutFunctionOrder = ["decout"]

argsToFirstSetupFunc = []
argsToFirstTransformFunc = ["sys.argv[1]", "sys.argv[2]", "sys.argv[3]"]
argsToFirstDecOutFunc = ["sys.argv[1]", "sys.argv[2]", "sys.argv[3]"]

groupObjName = "groupObj"
groupArg = "'SS512'"

utilObjName = "util"

rccaRandomVar = "R"

lamFuncName = "lam_func"
lambdaLetters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
lettersMapping = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7, "i":8, "j":9, "k":10, "l":11, "m":12, "n":13, "o":14, "p":15, "q":16, "r":17, "s":18, "t":19, "u":20, "v":21, "w":22, "x":23, "y":24, "z":25}

lenFuncName = "len"
pythonDefinedFuncs = [lenFuncName]

charmImportFuncs = []
charmImportFuncs.append("from charm import *")
charmImportFuncs.append("from toolbox import *")
charmImportFuncs.append("from toolbox.pairinggroup import *")
charmImportFuncs.append("from toolbox.secretutil import SecretUtil")
charmImportFuncs.append("from schemes import *")
charmImportFuncs.append("from math import *")
charmImportFuncs.append("from charm.pairing import hash as SHA1")

userGlobalsFuncName = "getUserGlobals"
