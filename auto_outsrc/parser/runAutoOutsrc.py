from keygen import *
#from config import *
import SDLPreProcessor
import sys, os, importlib

sys.path.extend(['../../', '../../codegen'])

import codegen_PY
import codegen_CPP
import SDLParser

PREPROCESSED_STRING = "_PREPROCESSED"

def writeLOCFromKeygenToFile(LOCFromKeygen, inputSDLScheme):
    f = open(inputSDLScheme + finalSDLSuffix, 'w')

    for line in LOCFromKeygen:
        lenLine = len(line)
        if (line[(lenLine - 1)] != "\n"):
            f.write(line + "\n")
        else:
            f.write(line)

    f.close()

def main(inputSDLScheme, configName, outputFile, outputUserDefFile):
    config = importlib.import_module(configName) # pkg.config
    SDLParser.masterPubVars = config.masterPubVars
    SDLParser.masterSecVars = config.masterSecVars

    SDLPreProcessor.SDLPreProcessor_main(inputSDLScheme, inputSDLScheme + PREPROCESSED_STRING)
    (linesOfCodeFromKeygen, blindingFactors_NonLists, blindingFactors_Lists) = keygen(inputSDLScheme + PREPROCESSED_STRING, config)
    writeLOCFromKeygenToFile(linesOfCodeFromKeygen, inputSDLScheme + PREPROCESSED_STRING)
    codegen_PY.codegen_PY_main(inputSDLScheme + PREPROCESSED_STRING + finalSDLSuffix, outputFile + ".py", outputUserDefFile + ".py")
    codegen_CPP.transformOutputList = transformOutputList
    codegen_CPP.codegen_CPP_main(inputSDLScheme + PREPROCESSED_STRING + finalSDLSuffix, outputFile + ".cpp")

if __name__ == "__main__":
    lenSysArgv = len(sys.argv)

    if ( (lenSysArgv != 5) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        sys.exit("Usage:  python " + sys.argv[0] + " [SDL filename] [SCHEME.config] [output filename] [Python filename for user-defined funcs].")

    configName = sys.argv[2] # format: e.g., "HIBE.config" 
    print("config name: ", configName)
    main(sys.argv[1], configName, sys.argv[3], sys.argv[4])
