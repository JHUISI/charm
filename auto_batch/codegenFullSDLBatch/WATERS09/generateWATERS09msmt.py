from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
import waters09

import sys, random, string, time

group = None
prefixName = None
sigNumKey = 'Signature_Number'
bodyKey = 'Body'
charmPickleSuffix = '.charmPickle'
pythonPickleSuffix = '.pythonPickle'
repeatSuffix = '.repeat'
lenRepeatSuffix = len(repeatSuffix)

trials = 1
time_in_ms = 1000
NUM_PROGRAM_ITERATIONS = 10
NUM_CYCLES = 10

def genNewMessage(messageSize):
    message = ""
    for randomChar in range(0, messageSize):
        message += random.choice(string.ascii_letters + string.digits)
    return message

def genBadMessage(message, messageSize):
    randomIndex = random.randint(0, (messageSize - 1))
    oldValue = message[randomIndex]
    newValue = random.choice(string.ascii_letters + string.digits)
    while (newValue == oldValue):
        newValue = random.choice(string.ascii_letters + string.digits)

    if (messageSize == 1):
        message = newValue
    elif (randomIndex != (messageSize -1) ):
        message = message[0:randomIndex] + newValue + message[(randomIndex + 1):messageSize]
    else:
        message = message[0:randomIndex] + newValue
    return message

def genValidSignature(message, index, pk, sk):
    sig = waters09.sign(pk, sk, message)
    (S1, S2, S3, S4, S5, S6, S7, SK, tagk) = sig
    (g1, g2, g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, uG1, u, wG1, hG1, w, h, A) = pk
    assert waters09.verify(g1, g2, g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, u, w, h, A, S1, S2, S3, S4, S5, S6, S7, SK, tagk, message), "failed verification"
    return sig

def genOutputDictFile(numCount, messageSize, keyName1, keyName2, outputDict, outputDictName, outputMsgSuffix, outputSigSuffix, isValid, *signVars):
    for index in range(0, numCount):
        if (index != 0):
            outputDict[index] = {}
            outputDict[index]['mpk'] = keyName1
#            outputDict[index]['pk'] = keyName2

        message = genNewMessage(messageSize)
        # inputs change for each scheme        
        sig = genValidSignature(message, index, *signVars)

        f_message = open(prefixName + str(index) + outputMsgSuffix, 'wb')
        outputDict[index]['message'] = prefixName + str(index) + outputMsgSuffix
        if isValid == False: # make signature effectively invalid
            message = genBadMessage(message, messageSize)
        
        pickle.dump(message, f_message)
        f_message.close()

        f_sig = open(prefixName + str(index) + outputSigSuffix, 'wb')
        outputDict[index]['sig'] = prefixName + str(index) + outputSigSuffix
        
        pick_sig = objectToBytes(sig, group)

        f_sig.write(pick_sig)
        f_sig.close()

    dict_pickle = objectToBytes(outputDict, group)
    f = open(outputDictName, 'wb')
    f.write(dict_pickle)
    f.close()
    del dict_pickle
    del f
    

def loadDictDataFromFile(verifyParamFilesDict, groupParamArg):
    verifyArgsDict = {}
    totalNumSigs = len(verifyParamFilesDict)
    verifyFuncArgs = list(verifyParamFilesDict[0].keys())

    for sigIndex in range(0, totalNumSigs):
        verifyArgsDict[sigIndex] = {}
        for arg in verifyFuncArgs:
            verifyArgsDict[sigIndex][arg] = {}
            verifyParamFile = str(verifyParamFilesDict[sigIndex][arg])
            if (verifyParamFile.endswith(charmPickleSuffix)):
                verifyParamPickle = open(verifyParamFile, 'rb').read()
                verifyArgsDict[sigIndex][arg][bodyKey] = bytesToObject(verifyParamPickle, groupParamArg)

            elif (verifyParamFile.endswith(pythonPickleSuffix)):
                verifyParamPickle = open(verifyParamFile, 'rb')
                verifyArgsDict[sigIndex][arg][bodyKey] = pickle.load(verifyParamPickle)
            elif (verifyParamFile.endswith(repeatSuffix)):
                verifyArgsDict[sigIndex][arg][sigNumKey] = verifyParamFile[0:(len(verifyParamFile) - lenRepeatSuffix)]
            else:
                tempFile = open(verifyParamFile, 'rb')
                tempBuf = tempFile.read()
                verifyArgsDict[sigIndex][arg][bodyKey] = tempBuf

    return verifyArgsDict

def loadDataFromDictInMemory(verifyParamFilesDict, startIndex, numSigsToProcess, verifyArgsDict, counterToStartFrom, incorrectSigIndices = []):

    totalNumSigs = len(verifyParamFilesDict)
    verifyFuncArgs = list(verifyParamFilesDict[0].keys())
    counterFromZero = counterToStartFrom

    for i in range(startIndex, (startIndex + numSigsToProcess)):
        sigIndex = i % totalNumSigs
        verifyArgsDict[counterFromZero] = verifyParamFilesDict[sigIndex]
        incorrectSigIndices.append(counterFromZero)
        counterFromZero += 1

    return (counterFromZero - 1)

def getResults(resultsDict):
    resultsString = ""

    for cycle in range(0, NUM_CYCLES):
        value = 0.0

        for programIteration in range(0, NUM_PROGRAM_ITERATIONS):
            value += resultsDict[programIteration][cycle]

        value = float(value) / float(NUM_PROGRAM_ITERATIONS)

        resultsString += str(cycle+1) + " " + str(value) + "\n"

    return resultsString


def generate_signatures_main(argv, same_signer=True):
    if ( (len(argv) != 7) or (argv[1] == "-help") or (argv[1] == "--help") ):
        sys.exit("Usage:  python " + argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")
    
    global group, prefixName
    group = PairingGroup('BN256')
    waters09.group = group
    #setup parameters
    numValidMessages = int(sys.argv[1])
    numInvalidMessages = int(sys.argv[2])
    messageSize = int(sys.argv[3])
    prefixName = sys.argv[4]
    validOutputDictName = sys.argv[5]
    invalidOutputDictName = sys.argv[6]
    
    # 1. generate keys
    (pk, sk) = waters09.keygen()
       
    f_mpk = open('mpk.charmPickle', 'wb')
    # 2. serialize the pk's
    pick_mpk = objectToBytes({ 'pk':pk }, group)
    f_mpk.write(pick_mpk)
    f_mpk.close()
    
    
#    f_pk = open('pk.charmPickle', 'wb')
#    # 2. serialize the pk's
#    pick_pk = objectToBytes( pklist, group)
#    f_pk.write(pick_pk)
#    f_pk.close()

    
    validOutputDict = {}
    validOutputDict[0] = {}
    validOutputDict[0]['mpk'] = 'mpk.charmPickle'
#    validOutputDict[0]['pk'] = 'pk.charmPickle'
    
    invalidOutputDict = {}
    invalidOutputDict[0] = {}
    invalidOutputDict[0]['mpk'] = 'mpk.charmPickle'
#    invalidOutputDict[0]['pk'] = 'pk.charmPickle'
    
    # 3. pass right arguments at the end
    genOutputDictFile(numValidMessages, messageSize, 'mpk.charmPickle', 'pk.charmPickle', validOutputDict, validOutputDictName, '_ValidMessage.pythonPickle', '_ValidSignature.charmPickle', True, pk, sk)
    genOutputDictFile(numInvalidMessages, messageSize, 'mpk.charmPickle', 'pk.charmPickle', invalidOutputDict, invalidOutputDictName, '_InvalidMessage.pythonPickle', '_InvalidSignature.charmPickle', False, pk, sk)
    return

def run_batch_verification(argv, same_signer=True):
    if ( (len(argv) != 4) or (argv[1] == "-help") or (argv[1] == "--help") ):
        sys.exit("Usage:  python " + argv[0] + "\n\t[dictionary with valid messages/signatures]\n\t[name of output file for batch results]\n\t[name of output file for ind. results]")
    
    validDictArg = open(sys.argv[1], 'rb').read()
    groupParamArg = PairingGroup('BN256')
    waters09.group = groupParamArg
    batchResultsFile = sys.argv[2]
    indResultsFile = sys.argv[3]

    batchResultsRawFilename = 'raw_' + batchResultsFile
    indResultsRawFilename   = 'raw_' + indResultsFile
    
    validDictFile = bytesToObject(validDictArg, groupParamArg)
    validDict = loadDictDataFromFile(validDictFile, groupParamArg)

    batchResultsTimes = {}
    indResultsTimes = {}

    batchResultsRaw = open(batchResultsRawFilename, 'w')
    indResultsRaw = open(indResultsRawFilename, 'w')

    for initIndex in range(0, NUM_PROGRAM_ITERATIONS):
        batchResultsTimes[initIndex] = {}
        indResultsTimes[initIndex] = {}

    for programIteration in range(0, NUM_PROGRAM_ITERATIONS):
        print("program iteration ", programIteration)

        for cycle in range(0, NUM_CYCLES):
            #print("cycle is ", cycle)
            sigsDict = {}
            loadDataFromDictInMemory(validDict, 0, (cycle+1), sigsDict, 0)
            verifyFuncArgs = list(sigsDict[0].keys())
            #print("verifyFuncArgs: ", verifyFuncArgs)
            N = len(sigsDict.keys())
            waters09.N = N
            # 4. public values/generator
            g1, g2 = sigsDict[0]['mpk'][bodyKey]['pk'][0:2]
            g1b, g1a1, g1a2, g1ba1, g1ba2, tau1, tau2, tau1b, tau2b, uG1, u, wG1, hG1, w, h, A = sigsDict[0]['mpk'][bodyKey]['pk'][2:]

            Mlist =  [ sigsDict[i]['message'][bodyKey] for i in range(0, N) ]
            S1list = [ sigsDict[i]['sig'][bodyKey][0] for i in range(0, N) ]
            S2list = [ sigsDict[i]['sig'][bodyKey][1] for i in range(0, N) ]
            S3list = [ sigsDict[i]['sig'][bodyKey][2] for i in range(0, N) ]
            S4list = [ sigsDict[i]['sig'][bodyKey][3] for i in range(0, N) ]
            S5list = [ sigsDict[i]['sig'][bodyKey][4] for i in range(0, N) ]
            S6list = [ sigsDict[i]['sig'][bodyKey][5] for i in range(0, N) ]
            S7list = [ sigsDict[i]['sig'][bodyKey][6] for i in range(0, N) ]
            SKlist = [ sigsDict[i]['sig'][bodyKey][7] for i in range(0, N) ]
            tagklist = [ sigsDict[i]['sig'][bodyKey][8] for i in range(0, N) ]

            startTime = time.clock()
            incorrectSigIndices = waters09.batchverify(A, S1list, S2list, S3list, S4list, S5list, S6list, S7list, SKlist, g1, g1a1, g1a2, g1b, g1ba1, g1ba2, g2, h, Mlist, tagklist, tau1, tau1b, tau2, tau2b, u, w, [])
            endTime = time.clock()

            result = (endTime - startTime) * time_in_ms
            #print("batch is ", result)

            if (incorrectSigIndices != []):
                print("incorrectSigIndices: ", incorrectSigIndices)
                sys.exit("Batch verification returned invalid signatures.")

            batchResultsTimes[programIteration][cycle] = ( float(result) / float(cycle+1) )
            currentBatchOutputString = str(batchResultsTimes[programIteration][cycle]) + ","
            batchResultsRaw.write(currentBatchOutputString)

            startTime = time.clock()
            incorrectSigIndices = waters09.indivverify(A, S1list, S2list, S3list, S4list, S5list, S6list, S7list, SKlist, g1, g1a1, g1a2, g1b, g1ba1, g1ba2, g2, h, Mlist, tagklist, tau1, tau1b, tau2, tau2b, u, w, [])
            endTime = time.clock()

            result = (endTime - startTime) * time_in_ms
            #print("ind is ", result)

            if (incorrectSigIndices != []):
                sys.exit("Ind. verification returned invalid signatures.")

            indResultsTimes[programIteration][cycle] = ( float(result) / float(cycle+1) )
            currentIndOutputString = str(indResultsTimes[programIteration][cycle]) + ","
            indResultsRaw.write(currentIndOutputString)
            
        batchResultsRaw.write("\n")
        indResultsRaw.write("\n")

    batchResultsRaw.close()
    del batchResultsRaw
    indResultsRaw.close()
    del indResultsRaw
    batchResultsString = getResults(batchResultsTimes)
    indResultsString = getResults(indResultsTimes)

    outputFile = open(batchResultsFile, 'w')
    outputFile.write(batchResultsString)
    outputFile.close()
    del outputFile

    outputFile = open(indResultsFile, 'w')
    outputFile.write(indResultsString)
    outputFile.close()
    del outputFile

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) < 2:
        sys.exit("Usage:  python " + sys.argv[0] + "\t[ -g or -b ]\t[ command-arguments ]\n-g : generate signatures.\n -b : benchmark with generated signatures.")
    command = sys.argv[1]
    same_signer = False
    if command == "-g":
        print("Generating signatures...")        
        sys.argv.remove(command)        
        generate_signatures_main(sys.argv, same_signer)
    elif command == "-b":
        print("Running batch verification...")
        sys.argv.remove(command)
        run_batch_verification(sys.argv, same_signer) # different signers
    else:
        sys.exit("Usage:  python " + sys.argv[0] + "\t[ -g or -b ]\t[ command-arguments ]\n-g : generate signatures.\n-b : benchmark with generated signatures.")
    
