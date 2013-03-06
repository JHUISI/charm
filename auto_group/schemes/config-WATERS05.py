schemeName = "WATERS05"

setupFuncName 	= "setup"
keygenFuncName 	= "keygen"
signFuncName 	= "sign"
verifyFuncName 	= "verify"

masterPubVars = ["mpk", "u"]
masterSecVars = ["msk"]

# superset of variables we have used to represent public parameters in
# our crypto schemes
keygenPubVar = ["mpk"]

keygenSecVar = "sk" 
signatureVar = "sig" 

schemeType = "SIG"

charmImportFuncs = []
charmImportFuncs.append("from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, SymEnc, SymDec")
charmImportFuncs.append("from toolbox.secretutil import SecretUtil")
charmImportFuncs.append("from toolbox.iterate import dotprod2")
charmImportFuncs.append("from charm.pairing import hash as DeriveKey")
charmImportFuncs.append("from charm.engine.util import objectToBytes, bytesToObject")
charmImportFuncs.append("from builtInFuncs import *")

