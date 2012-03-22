from SDLParser import *
import config, sys

#TODO:  move this to config.py
blindingLoopVar = "y"
blindingSuffix = "_Blinded"
keygenBlindingExponent = "z"
keygenFuncName = "keygen"
inputKeyword = "input"
outputKeyword = "output"

SDLLinesForKeygen = ""

def blindKeygenOutputElement(keygenOutputElem, keygenInput):
    global SDLLinesForKeygen

    if (keygenOutputElem in keygenInput):
        SDLLinesForKeygen += keygenOutputElem + blindingSuffix + " := " + keygenOutputElem + "\n"
        return

    if (keygenOutputElem not in assignInfo[keygenFuncName]):
        sys.exit("keygen output element passed to blindKeygenOutputElement in keygen.py is not in assignInfo[keygenFuncName].")

    keygenOutputVarInfo = assignInfo[keygenFuncName][keygenOutputElem]

    if ( (keygenOutputVarInfo.getIsList() == True) and (len(keygenOutputVarInfo.getListNodesList()) > 0) ):
        listMembers = keygenOutputVarInfo.getListNodesList()
        listMembersString = ""
        for listMember in listMembers:
            listMembersString += listMember + blindingSuffix + ", "
            blindKeygenOutputElement(listMember, keygenInput)
        listMembersString = listMembersString[0:(len(listMembersString)-2)]
        SDLLinesForKeygen += keygenOutputElem + blindingSuffix + " := list{" + listMembersString + "}\n"
        return

    if (keygenOutputVarInfo.getIsList() == False):
        SDLLinesForKeygen += keygenOutputElem + blindingSuffix + " := " + keygenOutputElem + " ^ (1/" + keygenBlindingExponent + ")\n"
        return

    SDLLinesForKeygen += "len_" + keygenOutputElem + blindingSuffix + " := len(" + keygenOutputElem + ")\n"
    SDLLinesForKeygen += keygenOutputElem + blindingSuffix + " := init(list)\n"
    SDLLinesForKeygen += "BEGIN :: for\n"
    SDLLinesForKeygen += "for{" + blindingLoopVar + " := 1, len_" + keygenOutputElem + blindingSuffix + "}\n"
    SDLLinesForKeygen += keygenOutputElem + blindingSuffix + LIST_INDEX_SYMBOL + blindingLoopVar + " := " + keygenOutputElem + LIST_INDEX_SYMBOL + blindingLoopVar + " ^ (1/" + keygenBlindingExponent + ")\n"
    SDLLinesForKeygen += "END :: for\n"

def keygen(sdl_scheme):
    global SDLLinesForKeygen

    parseFile2(sdl_scheme, False)
    getVarDepInfLists()    
    getVarsThatProtectM()

    if ( (keygenFuncName not in assignInfo) or (outputKeyword not in assignInfo[keygenFuncName]) ):
        sys.exit("assignInfo structure obtained in keygen function of keygen.py did not have the right keygen function name or output keywords.")

    keygenOutput = assignInfo[keygenFuncName][outputKeyword].getVarDeps()
    if (len(keygenOutput) == 0):
        sys.exit("Variable dependencies obtained for output of keygen in keygen.py was of length zero.")

    if (inputKeyword not in assignInfo[keygenFuncName]):
        sys.exit("assignInfo structure obtained in keygen function of keygen.py did not have the right input keyword.")

    keygenInput = assignInfo[keygenFuncName][inputKeyword].getVarDeps()
    if (len(keygenInput) == 0):
        sys.exit("Variable dependencies obtained for input of keygen in keygen.py was of length zero.")

    SDLLinesForKeygen += keygenBlindingExponent + " := random(ZR)\n"

    for keygenOutput_ind in keygenOutput:
        blindKeygenOutputElement(keygenOutput_ind, keygenInput)

if __name__ == "__main__":
    file = sys.argv[1]
    keygen(file)
    print(SDLLinesForKeygen)
