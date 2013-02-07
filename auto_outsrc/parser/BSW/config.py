schemeName = "LW"

rootNodeName = 'root'
addNodePrefix = 'ADD'
mulNodePrefix = 'MUL'

inputVarName = "input"
outputVarName = "output"

finalSDLSuffix = ".FINAL_SDL"

transformOutputList = "transformOutputList"

doNotIncludeInTransformList = []

forLoopSeed = 1000

M = 'M'

listNameIndicator = "LISTNAMEINDICATOR"

varNameLeftSideNoBlindedVars = "neverUseThisVarNameNoBlindedVars"
varNameLeftSideBlindedVars = "neverUseThisVarNameBlindedVars"

blindingLoopVar = "y"
blindingLoopVarLength = "yLength"

blindingFactorPrefix = "blindingFactor"

blindingSuffix = "Blinded"
setupFuncName = "setup"
keygenBlindingExponent = "zz"
keygenBlindingExponentType = "ZR"
keygenFuncName = "keygen"

keysForKeygenElemSuffix = "KeysSuffix"

loopVarForKeygenElemKeys = "KeyLoopVar"

encryptFuncName = "encrypt"
decryptFuncName = "decrypt"
transformFuncName = "transform"

mainFuncName = "main"
verifyFuncName = "verify"

masterPubVars = ["pk"]
masterSecVars = ["mk"]

# superset of variables we have used to represent public parameters in
# our crypto schemes
keygenPubVar = ["pk"]
keygenSecVar = "sk"

pySuffix = ".py"
cppSuffix = ".cpp"
#cppSuffix = ".py"
cppHeaderSuffix = ".h"

setupFileName = "setupOutsourcing_" + schemeName + pySuffix
transformFileName = "transformOutsourcing_" + schemeName + pySuffix
decOutFolderName = "../cppCompilation/"
decOutFileName = "decOutOutsourcing_" + schemeName + cppSuffix
#decOutFileName = "decOutOutsourcing_" + schemeName + pySuffix

decOutObjFileName = "client_decout_" + schemeName

userFuncsName = "userFuncs_" + schemeName
userFuncsFileName = userFuncsName + pySuffix
userFuncsCPPFileName = userFuncsName + cppHeaderSuffix
outputSDLFileName = "outsourcedSDL_" + schemeName + pySuffix
makefileFolderName = "../cppCompilation/"
makefileFileName = "Makefile"
makefileTemplateFileName = "../cppCompilation/Makefile_Template"

errorFuncName = "userErrorFunction"
errorFuncArgString = "userErrorFunctionArgString"
errorFuncArgString_CPPType = "string"

transformFunctionName = "transform"
partialCT = "partCT"
decOutFunctionName = "decout"
getStringFunctionName = "GetString"

setupFunctionOrder = [setupFuncName, keygenFuncName, encryptFuncName]
transformFunctionOrder = [transformFunctionName]
decOutFunctionOrder = [decOutFunctionName]

argsToFirstSetupFunc = []
argsToFirstTransformFunc = ["sys.argv[1]", "sys.argv[2]", "sys.argv[3]"]
argsToFirstDecOutFunc = ["sys.argv[1]", "sys.argv[2]", "sys.argv[3]"]

PairingGroupClassName_CPP = "PairingGroup"
SecurityParameter_CPP = "MNT160"
groupObjName = "group"
groupArg = "MNT160"

utilObjName = "util"

rccaRandomVar = "R"

lamFuncName = "lam_func"
lambdaLetters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
lettersMapping = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7, "i":8, "j":9, "k":10, "l":11, "m":12, "n":13, "o":14, "p":15, "q":16, "r":17, "s":18, "t":19, "u":20, "v":21, "w":22, "x":23, "y":24, "z":25}

lenFuncName = "len"
pythonDefinedFuncs = [lenFuncName]

charmImportFuncs = []
charmImportFuncs.append("from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, SymEnc, SymDec")
charmImportFuncs.append("from toolbox.secretutil import SecretUtil")
charmImportFuncs.append("from toolbox.iterate import dotprod2")
charmImportFuncs.append("from charm.pairing import hash as DeriveKey")
charmImportFuncs.append("from charm.engine.util import objectToBytes, bytesToObject")
charmImportFuncs.append("from builtInFuncs import *")

userGlobalsFuncName = "getUserGlobals"

argSuffix = "_Arg"
nonIntDotProdIndex = "loopIndex"

KeysListSuffix_CPP = "_Keys_List"
ListLengthSuffix_CPP = "_List_Length"
TempLoopVar_CPP = "_Temp_Loop_Var"

charmListType = "CharmList"
charmDictType = "CharmDict"

serializeFuncName = "writeToFile"
serializeExt = ".txt"
serializeObjectOutFuncName = "objectOut"
serializeKeysName = "keys"
serializePubKey = "pk[4]"
serializePubKeyType = "GT"
serializePubKey_DecOut = "pk"

linesForSetupMain = []
linesForSetupMain.append("S = ['ONE', 'TWO', 'THREE']")
linesForSetupMain.append("M = \"balls on fire345\"")
linesForSetupMain.append("policy_str = '((four or three) and (two or one))'")

structsToPickleInSetupMain = []
structsToPickleInSetupMain.append("")

charmPickleExt = ".charmPickle"
objectToBytesFuncName = "objectToBytes"
bytesToObjectFuncName = "bytesToObject"

unpickleFileSuffix = "_File"

CPP_Main_Line = "int main(int argc, char* argv[])"

parseParCT_FuncName_DecOut = "parsePartCT"
parseKeys_FuncName_DecOut = "parseKeys"
