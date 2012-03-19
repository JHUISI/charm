from SDLParser import *
import config, sys

#TODO:  move this to config.py
keygenFuncName = "keygen"
outputKeyword = "output"

SDLLinesForKeygen = ""

def keygen(sdl_scheme):
    parseFile2(sdl_scheme)
    getVarDepInfLists()    
    getVarsThatProtectM()

    if ( (keygenFuncName not in assignInfo) or (outputKeyword not in assignInfo[keygenFuncName]) ):
        sys.exit("assignInfo structure obtained in keygen function of keygen.py did not have the right keygen function name or output keywords.")

    keygenOutput = assignInfo[keygenFuncName][outputKeyword].getVarDeps()
    if (len(keygenOutput) == 0):
        sys.exit("Variable dependencies obtained for output of keygen in keygen.py was of length zero.")

    p

if __name__ == "__main__":
    file = sys.argv[1]
    keygen(file)
