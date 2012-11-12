from keygen import *
from config import *
import sys, os

sys.path.extend(['../../', '../../codegen'])

from codegen_PY import *

def writeLOCFromKeygenToFile(LOCFromKeygen, inputSDLScheme):
    f = open(inputSDLScheme + finalSDLSuffix, 'w')

    for line in LOCFromKeygen:
        lenLine = len(line)
        if (line[(lenLine - 1)] != "\n"):
            f.write(line + "\n")
        else:
            f.write(line)

    f.close()

def main(inputSDLScheme, outputFile, outputUserDefFile):
    (linesOfCodeFromKeygen, blindingFactors_NonLists, blindingFactors_Lists) = keygen(inputSDLScheme)
    writeLOCFromKeygenToFile(linesOfCodeFromKeygen, inputSDLScheme)
    codegen_PY_main(inputSDLScheme + finalSDLSuffix, outputFile, outputUserDefFile)

if __name__ == "__main__":
    lenSysArgv = len(sys.argv)

    if ( (lenSysArgv != 4) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        sys.exit("Usage:  python " + sys.argv[0] + " [name of input SDL file] [name of output Python file] [name of output Python file for user-defined functions].")

    main(sys.argv[1], sys.argv[2], sys.argv[3])
