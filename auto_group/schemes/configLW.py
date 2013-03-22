schemeType = "PKENC"
short = "secret_keys"

extraSetupFuncName = "setup"
setupFuncName = "authsetup"
keygenFuncName = "keygen"
encryptFuncName = "encrypt"
decryptFuncName = "decrypt"

masterPubVars = ["gpk", "pk"]
masterSecVars = ["msk"]

keygenPubVar = ["pk", "gpk"]
keygenSecVar = "sk"
ciphertextVar = ["C1", "C2", "C3"] # "ct"

functionOrder = [extraSetupFuncName, setupFuncName, keygenFuncName, encryptFuncName, decryptFuncName]
