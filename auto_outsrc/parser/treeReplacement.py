import sdlpath
from SDLParser import *
from SDLang import *

def areNodesEqual(node1, node2):
    if (node1.type != node2.type):
        return False

    if (str(node1) != str(node2)):
        return False

    return True

def recurseTree(mainTree, treeToLookFor, placesWhereTreeToLookForExists):
    if (areNodesEqual(mainTree, treeToLookFor) == True):
        print(mainTree)

    if (mainTree.left != None):
        recurseTree(mainTree.left, treeToLookFor, placesWhereTreeToLookForExists)

    if (mainTree.right != None):
        recurseTree(mainTree.right, treeToLookFor, placesWhereTreeToLookForExists)

def getPlacesWhereTreeToLookForExists(mainTree, treeToLookFor):
    placesWhereTreeToLookForExists = []

    recurseTree(mainTree, treeToLookFor, placesWhereTreeToLookForExists)

def makeTreeReplacement(mainTree, treeToLookFor, subThisTree):
    placesWhereTreeToLookForExists = getPlacesWhereTreeToLookForExists(mainTree, treeToLookFor)

def main():
    parser = SDLParser()
    mainTree = parser.parse(sys.argv[1])

    print(mainTree)
    return

    treeToLookFor = parser.parse(sys.argv[2])
    subThisTree = parser.parse(sys.argv[3])
    makeTreeReplacement(mainTree, treeToLookFor, subThisTree)


    str1 = str(mainTree)
    str2 = str(treeToLookFor)
    str3 = str(subThisTree)
    x = str1.replace(str2, str3)
    print(x)


if __name__ == "__main__":
    main()
