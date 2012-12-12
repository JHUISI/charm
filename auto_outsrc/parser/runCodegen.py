import sys, os

import sdlpath
sys.path.extend(['../../', '../../codegen'])

import sdlparser.SDLParser as sdl
import convertToAsymmetric
import codegen_PY

def writeLOCFromKeygenToFile(LOCFromKeygen, inputSDLScheme):
    f = open(inputSDLScheme, 'w')

    for line in LOCFromKeygen:
        lenLine = len(line)
        if (line[(lenLine - 1)] != "\n"):
            f.write(line + "\n")
        else:
            f.write(line)

    f.close()

def compileBV(inputSDLScheme, outputFile, outputUserDefFile):
#    (linesOfCodeFromKeygen, blindingFactors_NonLists, blindingFactors_Lists) = keygen(inputSDLScheme)
#    writeLOCFromKeygenToFile(linesOfCodeFromKeygen, inputSDLScheme)
    codegen_PY.codegen_PY_main(inputSDLScheme, outputFile, outputUserDefFile)

if __name__ == "__main__":
    print(sys.argv)
    lenSysArgv = len(sys.argv)
    
    sdlVerbose = False
    if len(sys.argv) > 2: # and sys.argv[3] == "-v":  sdlVerbose = True
        config = sys.argv[2]
        config = config.split('.')[0]

        configModule = __import__(config)
        sdl.masterPubVars = configModule.masterPubVars
        sdl.masterSecVars = configModule.masterSecVars
            
    bvFile = sys.argv[1]    
    outputBvFile = convertToAsymmetric.main(bvFile, configModule, sdlVerbose)

    compileBV(outputBvFile + ".bv", outputBvFile + ".py", "userFuncs2.py")
    
