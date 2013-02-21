import os, sys

def main(inputFile1, inputFile2, outputFile):
    input1 = open(inputFile1, 'r')
    input2 = open(inputFile2, 'r')
    output = open(outputFile, 'w')

    dict1 = {}
    dict2 = {}
    outputDict = {}

    for line in input1:
        lineSplit = line.split(' ')
        lineSplit[1] = lineSplit[1].rstrip()
        dict1[int(lineSplit[0])] = float(lineSplit[1])

    for line in input2:
        lineSplit = line.split(' ')
        lineSplit[1] = lineSplit[1].rstrip()
        dict2[int(lineSplit[0])] = float(lineSplit[1])

    for key in dict1:
        if key not in dict2:
            sys.exit("Keys of dict1 and dict2 don't align.")
        outputDict[key] = dict1[key] + dict2[key]

    for key in outputDict:
        output.write(str(key) + " " + str(outputDict[key]) + "\n")

    input1.close()
    input2.close()
    output.close()

if __name__ == "__main__":
    if (len(sys.argv) != 4):
        sys.exit("Usage:  python " + sys.argv[0] + " [name of first input file] [name of second input file] [name of output file]")

    main(sys.argv[1], sys.argv[2], sys.argv[3])
