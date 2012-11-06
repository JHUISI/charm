import sdlpath
from sdlparser.SDLParser import *


TYPE, CONST, PRECOMP, TRANSFORM = 'types', 'constant', 'precompute', 'transform'
MESSAGE, SIGNATURE, PUBLIC, SETTING, SETUP, KEYGEN, SIGN, VERIFY = 'message','signature', 'public','setting', 'setup', 'keygen', 'sign', 'verify'
BATCH_VERIFY = 'batch_verify'
PRECHECK_HEADER = 'precheck' # special section for computation and variables that need to be check before verification check
BATCH_VERIFY_MAP = BATCH_VERIFY + "_map"
BATCH_VERIFY_OTHER_TYPES = BATCH_VERIFY + "_other_types"
SCHEME_NAME, BATCH_COUNT, SECPARAM = 'name', 'count', 'secparam'
MSG_CNT, SIG_CNT, PUB_CNT = 'message_count', 'signature_count', 'public_count'
MEMBERSHIP_TEST_CHECK = 'membership'
# qualifier (means only one instance of that particular keyword exists)
SAME = 'one'
NUM_SIGNATURES = 'N'
NUM_SIGNER_TYPES = ['L', 'l']
linkVar = "link"
listVar = "list"
hasLoop, loopVar, startVal, endVal = "hasLoop", "loopVar", "startVal", "endVal"

class SDLSetting():
    def __init__(self, debug=False):
        self.verifyEqList = []
        self.latex_symbols = {}
        self.data = { CONST : None, PUBLIC: None, MESSAGE : None, SIGNATURE: None, SETTING : None, MEMBERSHIP_TEST_CHECK:{} }
        self.numSignatures = 0
        self.varTypes = {}
        self.indiv_precompute = {}
        self.batch_precompute = {}
        self.debug = debug
        self.partialSDL = False
        
    def parse(self, assignInfoDict, theVarTypes):
        self.__parseVerifyEq(assignInfoDict)
        self.__parseTypes(assignInfoDict, theVarTypes.get(TYPE))
        self.__parseTypes(assignInfoDict, theVarTypes.get(SETUP))
        self.__parseTypes(assignInfoDict, theVarTypes.get(KEYGEN))
        self.__parseTypes(assignInfoDict, theVarTypes.get(SIGN))
        self.__parseTypes(assignInfoDict, theVarTypes.get(VERIFY))
        self.__parseNumSignatures(assignInfoDict)
        self.__parseOneValueInKey(assignInfoDict, SCHEME_NAME)
        self.__parseOneValueInKey(assignInfoDict, SECPARAM)
        self.varTypes[SCHEME_NAME] = self.data[SCHEME_NAME]
        for i in NUM_SIGNER_TYPES:
            self.__parseOneValueInKey(assignInfoDict, i)
            self.varTypes[i] = self.data[i]
        self.__parseBatchCount(assignInfoDict)
        self.__parseValuesInKey(assignInfoDict, CONST)
        self.__parseValuesInKey(assignInfoDict, PUBLIC)
        self.__parseValuesInKey(assignInfoDict, SIGNATURE)
        self.__parseValuesInKey(assignInfoDict, MESSAGE)
        self.__parseValuesInKey(assignInfoDict, TRANSFORM)

        # this part will fail if Batch Count and CONST, PUBLIC, SIGNATURE and MESSAGE sections are not filled in.
        self.__processPublicVars()   
#        self.__processSignatureVars()
        self.__processMessageVars()
        
        self.__parsePrecomputeAssign(assignInfoDict)
#        self.__parsePreCheckIfExists(assignInfoDict)
        self.__parseLatexAssign(assignInfoDict)
        self.__parseVerifyInputArgs(assignInfoDict)
        
        if self.debug: 
            print("variable types: ", self.varTypes)
            print("constants: ", self.data.get(CONST))
            print("public: ", self.data.get(PUBLIC))
            print("signature: ", self.data.get(SIGNATURE))
            print("message: ", self.data.get(MESSAGE))
            print("batch_count: ", self.data.get(COUNT_HEADER))
            print("precompute: ", self.batch_precompute)
            print("transform: ", self.data.get(TRANSFORM))
            print("latex: ", self.latex_symbols)
            print("verify args: ", self.data.get(VERIFY))
    
    def __processPublicVars(self):
        batchCount = self.data[COUNT_HEADER]
        self.data[PUB_CNT] = {SAME:[], NUM_SIGNATURES:[], }
        publicKeyCount = batchCount.get(PUB_CNT) # either SAME, NUM_SIGS, etc
        if publicKeyCount not in self.data[PUB_CNT].keys():
            # add to pub_cnt dict
            self.data[PUB_CNT][publicKeyCount] = []
            
        for i in self.data.get(PUBLIC):
            self.data[PUB_CNT].get(publicKeyCount).append(i)

        print("__processPublicVars in batchconfig.py: ", self.data[PUB_CNT])
        return
    
    def __processMessageVars(self):
        batchCount = self.data[COUNT_HEADER]
        self.data[MSG_CNT] = {SAME:[], NUM_SIGNATURES:[], }
        messageKeyCount = batchCount.get(MSG_CNT) # either SAME, NUM_SIGS, etc
        if messageKeyCount not in self.data[MSG_CNT].keys():
            # add to pub_cnt dict
            self.data[MSG_CNT][messageKeyCount] = []
        for i in self.data.get(MESSAGE):
            self.data[MSG_CNT].get(messageKeyCount).append(i)

        print("__processMessageVars in batchconfig.py: ", self.data[MSG_CNT])
        return
    
    def __parseVerifyInputArgs(self, assignInfoDict):
        verifyDict = assignInfoDict.get(VERIFY)
        if verifyDict:
            if verifyDict.get('input') and self.data[COUNT_HEADER] != None:
                self.data[VERIFY] = list(verifyDict.get('input').getListNodesList())
                self.data[BATCH_VERIFY] = {}
                self.data[BATCH_VERIFY_MAP] = {}
#                self.data[BATCH_VERIFY_OTHER_TYPES] = {}
                # figure out which bach verify args are constant and which ones are not
                for k in self.data[VERIFY]:
                    if (k in self.data[CONST]) or (k in self.data[SIGNATURE] and self.data[COUNT_HEADER][SIG_CNT] != NUM_SIGNATURES) or (k in self.data[PUBLIC] and self.data[COUNT_HEADER][PUB_CNT] != NUM_SIGNATURES) or (k in self.data[MESSAGE] and self.data[COUNT_HEADER][MSG_CNT] != NUM_SIGNATURES):
                        self.data[BATCH_VERIFY][k] = self.returnRealType(self.varTypes[k])
                    else:
                        # change type into a list
                        self.setTypeString(k, self.varTypes[k]) # "list{%s}" % self.varTypes[k]  # it is variable

#                print("batchverify input types: ", self.data[BATCH_VERIFY], "\n", self.data[BATCH_VERIFY].items()) 
#                print("Sorted: ", self.data[BATCH_VERIFY].keys())
#                print("\n\n<=======>\nNew map for batch verify vars: ", self.data[BATCH_VERIFY_MAP])
#                sys.exit(0)
                self.partialSDL = False
        else:
            self.partialSDL = True

    def returnRealType(self, typeVar):
        newTypeTmp = ""
        if typeVar == "listZR":
            newTypeTmp = "list{ZR}"
        elif typeVar == "listG1":
            newTypeTmp = "list{G1}"
        elif typeVar == "listG2":
            newTypeTmp = "list{G2}"
        elif typeVar == "listGT":
            newTypeTmp = "list{GT}"
        elif typeVar == "listStr":
            newTypeTmp = "list{str}"
        elif typeVar == "listInt":
            newTypeTmp = "list{int}"
        else:
            return typeVar
        return newTypeTmp
    
    def setTypeString(self, k, typeVar):
        newType = listVar + "{%s}"
        newTypeTmp = ""
        if typeVar == "listZR":
            newTypeTmp = "list{ZR}"
        elif typeVar == "listG1":
            newTypeTmp = "list{G1}"
        elif typeVar == "listG2":
            newTypeTmp = "list{G2}"
        elif typeVar == "listGT":
            newTypeTmp = "list{GT}"
        elif typeVar == "listStr":
            newTypeTmp = "list{str}"
        elif typeVar == "listInt":
            newTypeTmp = "list{int}"
        
        
        if newTypeTmp != "":
            # if variable name includes the "list" keyword, then no need adding a list to the name.
            self.data[BATCH_VERIFY][k + linkVar] = newTypeTmp
            if listVar not in k:
                self.data[BATCH_VERIFY][k + listVar] = newType % (k + linkVar)
                self.data[BATCH_VERIFY_MAP][k] = k + listVar
                self.data[MEMBERSHIP_TEST_CHECK][k + listVar] = newTypeTmp
            else:
                self.data[MEMBERSHIP_TEST_CHECK][k] = newTypeTmp
                self.data[BATCH_VERIFY][k] = newType % (k + linkVar)                
                self.data[BATCH_VERIFY_MAP][k] = k
                
        else:
            self.data[BATCH_VERIFY][k + listVar] = newType % typeVar
            self.data[BATCH_VERIFY_MAP][k] = k + listVar

    
    def __parseBatchCount(self, assignInfoDict):
        countDict = assignInfoDict.get(COUNT_HEADER)
        self.data[COUNT_HEADER] = {}
        if type(countDict) == dict:
            for k,v in countDict.items():
                self.data[COUNT_HEADER][k] = v.getAssignNode().getRight().getAttribute()

    def __parsePrecomputeAssign(self, assignInfoDict):
        precomp = assignInfoDict.get(PRECOMPUTE_HEADER)
        self.data[PRECOMPUTE_HEADER] = {}
        if precomp == None: return
        index = 0
        if type(precomp) == dict:
            for k,v in precomp.items():
                node = v.getAssignNode() # might need 
                if(node.type == ops.EQ):
                    self.indiv_precompute[ node.left ] = node.right
#                    self.batch_precompute[ BinaryNode.copy(node.left) ] = BinaryNode.copy(node.right)
                    self.batch_precompute [ index ] = (BinaryNode.copy(node.left), BinaryNode.copy(node.right)) 
                    index += 1
        return
        
    def __parseLatexAssign(self, assignInfoDict):
        latex = assignInfoDict.get(LATEX_HEADER)
        if type(latex) == dict:
            for k,v in latex.items():
                self.latex_symbols[k] = v.getLineStrValue() # get second item
        return
      
    def __parseVerifyEq(self, assignInfoDict):
        non_funcDict = assignInfoDict.get(NONE_FUNC_NAME)
        self.verifyEqMap = {}
        if non_funcDict:
            if non_funcDict.get(VERIFY): #  and hasattr(non_funcDict[VERIFY], 'getAssignNode'):
                eq = non_funcDict[VERIFY].getAssignNode() # assumes VarInfo object
                if self.debug: print("Found verify eq: ", eq)
#                self.verifyEqList.append(eq)
                if non_funcDict[VERIFY].getOutsideForLoopObj() != None:
                    self.verifyEqMap[ VERIFY ] = { hasLoop:True, VERIFY: non_funcDict[VERIFY].getAssignNode() }
                else:
                    self.verifyEqMap[ VERIFY ] = { hasLoop:False, VERIFY: non_funcDict[VERIFY].getAssignNode() }                    
            else:
                for k,v in non_funcDict.items():
                    if VERIFY in k:# and hasattr(non_funcDict[k], 'getAssignNode'):
                        if non_funcDict[k].getOutsideForLoopObj() != None:
                            forLoopObj = non_funcDict[k].getOutsideForLoopObj()
                            self.verifyEqMap[ k ] = { hasLoop:True, loopVar: forLoopObj.getLoopVar(), startVal:forLoopObj.getStartVal(), endVal: forLoopObj.getEndVal(), VERIFY : non_funcDict[k].getAssignNode() }
                        else:
#                            self.verifyEqList.append(non_funcDict[k].getAssignNode()) # assumes VarInfo object
                            self.verifyEqMap[ k ] = { hasLoop:False, VERIFY: non_funcDict[k].getAssignNode() }
        return
    
    def getVerifyEq(self):
        return self.verifyEqMap # dictionary

    def __parseTypes(self, assignInfoDict, varTypeDict):
        if not varTypeDict: return
        for key in varTypeDict.keys():
            # save types
            if varTypeDict[key].getType() != types.NO_TYPE and self.varTypes.get(key) == None:
                self.varTypes[ key ] = str(varTypeDict[key].getType())
            
        return
    
    def __parseNumSignatures(self, assignInfoDict):
        non_funcDict = assignInfoDict.get(NONE_FUNC_NAME)
        if non_funcDict.get(NUM_SIGNATURES):
            eq_node = non_funcDict.get(NUM_SIGNATURES).getAssignNode()# assumes VarInfo
            numSigs = eq_node.getRight().getAttribute()
            assert numSigs.isdigit(), "variable '%s' needs to be an integer." % (NUM_SIGNATURES)
            self.varTypes[NUM_SIGNATURES] = int(numSigs)                 
        return
        
    def __parseValuesInKey(self, assignInfoDict, key):
        non_funcDict = assignInfoDict.get(NONE_FUNC_NAME)
        self.data[key] = []
        values = non_funcDict.get(key)
        if values:
            if type(values) == VarInfo: # check that it is VarInfo
#                if values.type == ops.LIST and len(values.getListNodesList()) > 0:
#                    self.data[key].extend(values.getListNodesList())
                if values.type == ops.LIST:
                    self.data[key].extend(values.getAssignNode().getRight().getListNode())
                else:
                    self.data[key].append(values.getAssignNode().getRight().getAttribute())
            return True
        else:
            return False

    def __parseOneValueInKey(self, assignInfoDict, key):
        non_funcDict = assignInfoDict.get(NONE_FUNC_NAME)
        self.data[key] = None
        values = non_funcDict.get(key)
        if values:
            if type(values) == VarInfo: # check that it is VarInfo
                self.data[key] = values.getAssignNode().getRight().getAttribute()
                if self.data.get(key).isdigit(): self.data[key] = int(self.data[key])
                return True
        else:
            return False

    def getTypes(self):
        return self.varTypes

    def getNumSignatures(self):
        return self.varTypes.get(NUM_SIGNATURES)
    
    def getSecParam(self):
        return self.data.get(SECPARAM)
    
    def getConstantVars(self):
        return self.data.get(CONST)

    def getPublicVars(self):
        return self.data.get(PUBLIC)
    
    def getMessageVars(self):
        return self.data.get(MESSAGE)
    
    def getSignatureVars(self):
        return self.data.get(SIGNATURE)
        
    def getLatexVars(self):
        return self.latex_symbols
    
    def getPrecomputeVars(self):
        return self.indiv_precompute, self.batch_precompute

    def getTransformList(self):
        return self.data.get(TRANSFORM)
    
    def getBatchCount(self):
        return self.data.get(COUNT_HEADER)
    
    def getVerifyInputArgs(self):
        return self.data.get(BATCH_VERIFY)
    
    def getVerifyInputArgsMap(self):
        return self.data.get(BATCH_VERIFY_MAP)
    
    def getPublicVarsCount(self):
        return self.data.get(PUB_CNT)
    
    def getMessageVarsCount(self):
        return self.data.get(MSG_CNT)
    
    def getModifiedTypes(self): # e.g., someVar := list{someVarLink}; someVarLink := list{ZR} # or G1, etc
        return self.data.get(MEMBERSHIP_TEST_CHECK)