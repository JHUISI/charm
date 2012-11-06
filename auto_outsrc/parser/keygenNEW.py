from SDLParser import *
from config import *
from transformNEW import *
from secretListInKeygen import *
import sys

assignInfo = None
varTypes = None
astNodes = None
publicVarNames = None
secretVarNames = None

def keygen(file):
    if ( (type(file) is not str) or (len(file) == 0) ):
        sys.exit("First argument passed to keygenNEW.py is invalid.")

    parseFile2(file, False)

    config = __import__('config')

    varsToBlindList = getSecretList(config, False)

    if ( (keygenFuncName not in assignInfo) or (outputKeyword not in assignInfo[keygenFuncName]) ):
        sys.exit("assignInfo structure obtained in keygen function of keygen.py did not have the right keygen function name or output keywords.")

    keygenOutput = assignInfo[keygenFuncName][outputKeyword].getVarDeps()
    if (len(keygenOutput) == 0):
        sys.exit("Variable dependencies obtained for output of keygen in keygen.py was of length zero.")
