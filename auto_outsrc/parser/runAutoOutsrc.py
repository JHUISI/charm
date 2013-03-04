from keygen import *
#from config import *
import SDLPreProcessor
import sys, os, importlib, time, gc

sys.path.extend(['../../', '../../codegen'])

import codegen_PY
import codegen_CPP
import SDLParser

PREPROCESSED_STRING = "_PREPROCESSED"

def writeLOCFromKeygenToFile(LOCFromKeygen, inputSDLScheme, config):
    f = open(inputSDLScheme + config.finalSDLSuffix, 'w')

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
    if hasattr(config, userFuncListName):
       userFuncList = getattr(config, userFuncListName)
    else:
       userFuncList = []

    SDLPreProcessor.SDLPreProcessor_main(inputSDLScheme, inputSDLScheme + PREPROCESSED_STRING, config)
    
    startTime = time.clock()
    (linesOfCodeFromKeygen, blindingFactors_NonLists, blindingFactors_Lists) = keygen(inputSDLScheme + PREPROCESSED_STRING, config)
    endTime = time.clock()
    runningTime = (endTime - startTime) * 1000
    print("running time for keygen is ", runningTime)


    writeLOCFromKeygenToFile(linesOfCodeFromKeygen, inputSDLScheme + PREPROCESSED_STRING, config)
    cleanParseLinesOfCode()

    startTime = time.clock()
    codegen_PY.codegen_PY_main(inputSDLScheme + PREPROCESSED_STRING + config.finalSDLSuffix, outputFile + ".py", outputUserDefFile + ".py")
    endTime = time.clock()
    runningTime = (endTime - startTime) * 1000
    print("running time for codegen python is ", runningTime)

    codegen_CPP.transformOutputList = transformOutputList

    startTime = time.clock()
    codegen_CPP.codegen_CPP_main(inputSDLScheme + PREPROCESSED_STRING + config.finalSDLSuffix, outputFile + ".cpp", userFuncList)
    endTime = time.clock()
    runningTime = (endTime - startTime) * 1000
    print("running time for codegen CPP is ", runningTime)

if __name__ == "__main__":
    lenSysArgv = len(sys.argv)

    if ( (lenSysArgv != 5) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        sys.exit("Usage:  python " + sys.argv[0] + " [SDL filename] [SCHEME.config] [output filename] [Python filename for user-defined funcs].")

    configName = sys.argv[2] # format: e.g., "HIBE.config" 
    print("config name: ", configName)
    main(sys.argv[1], configName, sys.argv[3], sys.argv[4])
