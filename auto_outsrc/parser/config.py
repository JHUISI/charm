M = 'M'

blindingLoopVar = "y"
blindingSuffix = "Blinded"
keygenBlindingExponent = "zz"
keygenFuncName = "keygen"
# superset of variables we have used to represent public parameters in
# our crypto schemes
keygenPubVar = ["pk", "mpk", "gpk"]
keygenSecVar = "sk"

setupFileName = "setupOutsourcing_BSW.py"
transformFileName = "transformOutsourcing_BSW.py"
#decOutFileName = "decOutOutsourcing_BSW.cpp"
decOutFileName = "decOutOutsourcing_BSW.py"
userFuncsName = "userFuncs_BSW"
userFuncsFileName = userFuncsName + ".py"
outputSDLFileName = "outsourcedSDL_BSW.py"
errorFuncName = "userErrorFunction"
errorFuncArgString = "userErrorFunctionArgString"

transformFunctionName = "transform"
partialCT = "partCT"
decOutFunctionName = "decout"
getStringFunctionName = "GetString"

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
charmImportFuncs.append("from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair")
charmImportFuncs.append("from toolbox.secretutil import SecretUtil")
charmImportFuncs.append("from toolbox.symcrypto import AuthenticatedCryptoAbstraction")
charmImportFuncs.append("from toolbox.iterate import dotprod2")
charmImportFuncs.append("from charm.pairing import hash as SHA1")

userGlobalsFuncName = "getUserGlobals"

argSuffix = "_Arg"
nonIntDotProdIndex = "loopIndex"
