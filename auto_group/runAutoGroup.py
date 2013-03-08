import sys, getopt, importlib
import src.sdlpath
import SDLParser as sdl
from SDLang import *
from src.convertToAsymmetric import runAutoGroup


if __name__ == "__main__":
    print(sys.argv)
    sdl_file = sys.argv[1]
    sdlVerbose = False
    if len(sys.argv) > 2: # and sys.argv[3] == "-v":  sdlVerbose = True
        config = sys.argv[2]
        config = config.split('.')[0]

        configModule = importlib.import_module("schemes." + config)#__import__(config)
        sdl.masterPubVars = configModule.masterPubVars
        sdl.masterSecVars = configModule.masterSecVars
            
    runAutoGroup(sdl_file, configModule, sdlVerbose)
