schemeName = "DSE"

inputVarName = "input"
outputVarName = "output"

finalSDLSuffix = ".FINAL_SDL"

doNotIncludeInTransformList = ["prod"]

transformOutputList = "transformOutputList"

M = 'M'

forLoopSeed = 1000

listNameIndicator = "LISTNAMEINDICATOR"

varNameLeftSideNoBlindedVars = "neverUseThisVarNameNoBlindedVars"
varNameLeftSideBlindedVars = "neverUseThisVarNameBlindedVars"

blindingLoopVar = "y"
blindingLoopVarLength = "yLength"

blindingLoopVarForOrigKeygenElem = "loopVarOrigKeygenElem"

loopVarForKeygenElemKeys = "KeyLoopVar"
keysForKeygenElemSuffix = "KeysSuffix"

blindingFactorPrefix = "blindingFactor"

blindingSuffix = "Blinded"
keygenBlindingExponent = "zz"
keygenBlindingExponentType = "ZR"

setupFuncName = "setup"
keygenFuncName = "keygen"
encryptFuncName = "encrypt"
decryptFuncName = "decrypt"
transformFuncName = "transform"

masterPubVars = ["mpk"]
masterSecVars = ["msk"]

# superset of variables we have used to represent public parameters in
# our crypto schemes
keygenPubVar = ["pk"]
# TODO: make D and D#1, D#2 interchangeable...that is, map the two
keygenSecVar  = "sk" # ["D#1", "D#2", "D#3", "D#4", "D#5", "D#6", "D#7", "K"]
ciphertextVar = "ct" # ["C#1", "C#2", "C#3", "C#4", "C#5", "C#6", "C#7", "E1", "E2"]

schemeType = "PUB"
setupFunctionOrder = [setupFuncName, keygenFuncName, encryptFuncName, decryptFuncName]

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
