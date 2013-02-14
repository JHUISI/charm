possibleGroupTypes = ["G1", "G2", "GT", "ZR"]

INIT_FUNC_NAME = "init"
ISMEMBER_FUNC_NAME = "ismember"
INTEGER_FUNC_NAME = "integer"
LEN_FUNC_NAME = "len"
ADD_TO_LIST = "addToList"
STRING_TO_INT = "stringToInt" # args: 1. group, 2. three args, 3. output arg
NONE_FUNC_NAME = "NONE_FUNC_NAME"
RETURN_KEYWORD = "return"
RETURN_STATEMENT = "return := None"
DOT_PROD_WORD = "dot"
SUM_PROD_WORD = "sum"

numSignaturesVarName = "N"
numSignersVarName = "l"
smallExp = "SmallExp(secparam)"
secParamVarName = "secparam"
elementName = "Element"
strArgName = "str"

inputVarName = "input"
outputVarName = "output"

M = 'M'

blindingLoopVar = "y"

blindingFactorPrefix = "blindingFactor"

blindingSuffix = "Blinded"
setupFuncName = "authsetup"
keygenBlindingExponent = "zz"
keygenBlindingExponentType = "ZR"
keygenFuncName = "keygen"

encryptFuncName = "encrypt"

mainFuncName = "main"
verifyFuncName = "verify"
membershipFuncName = "membership"
batchVerifyFuncName = "batchverify"
precheckFuncName = "precheck"

masterPubVars = ["gpk", "pk"]
masterSecVars = ["msk"]

# superset of variables we have used to represent public parameters in
# our crypto schemes
keygenPubVar = ["pk", "gpk"]
keygenSecVar = "sk"

pySuffix = ".py"
cppSuffix = ".cpp"
cppHeaderSuffix = ".h"

errorFuncName = "userErrorFunction"
errorFuncArgString = "userErrorFunctionArgString"
errorFuncArgString_CPPType = "string"

partialCT = "partCT"
getStringFunctionName = "GetString"

setupFunctionOrder = [setupFuncName, keygenFuncName, encryptFuncName]

argsToFirstSetupFunc = []

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

KeysListSuffix_CPP = "_keys"
ListLengthSuffix_CPP = "_len"
TempLoopVar_CPP = "_var"

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
