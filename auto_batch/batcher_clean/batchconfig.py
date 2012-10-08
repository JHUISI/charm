import sdlpath
from sdlparser.SDLParser import *


TYPE, CONST, PRECOMP, TRANSFORM = 'types', 'constant', 'precompute', 'transform'
MESSAGE, SIGNATURE, PUBLIC, SETTING, VERIFY = 'message','signature', 'public','setting', 'verify'
BATCH_VERIFY = 'batch_verify'
BATCH_VERIFY_MAP = BATCH_VERIFY + "_map"
SCHEME_NAME, BATCH_COUNT = 'name', 'count'
MSG_CNT, SIG_CNT, PUB_CNT = 'message_count', 'signature_count', 'public_count'
# qualifier (means only one instance of that particular keyword exists)
SAME = 'one'
NUM_SIGNATURES = 'N'
NUM_SIGNER_TYPES = ['L', 'l']

class SDLSetting():
    def __init__(self, debug=False):
        self.verifyEqList = []
        self.latex_symbols = {}
        self.data = { CONST : None, PUBLIC: None, MESSAGE : None, SIGNATURE: None, SETTING : None }
        self.numSignatures = 0
        self.varTypes = {}
        self.indiv_precompute = {}
        self.batch_precompute = {}
        self.debug = debug
        self.partialSDL = False
        
    def parse(self, assignInfoDict, theVarTypes):
        self.__parseVerifyEq(assignInfoDict)
        self.__parseTypes(assignInfoDict, theVarTypes.get(TYPE))
        self.__parseNumSignatures(assignInfoDict)
        self.__parseOneValueInKey(assignInfoDict, SCHEME_NAME)
        self.varTypes[SCHEME_NAME] = self.data[SCHEME_NAME]
        for i in NUM_SIGNER_TYPES:
            self.__parseOneValueInKey(assignInfoDict, i)
            self.varTypes[i] = self.data[i]       
        self.__parseValuesInKey(assignInfoDict, CONST)
        self.__parseValuesInKey(assignInfoDict, PUBLIC)
        self.__parseValuesInKey(assignInfoDict, SIGNATURE)
        self.__parseValuesInKey(assignInfoDict, MESSAGE)
        self.__parseValuesInKey(assignInfoDict, TRANSFORM)
        self.__parseBatchCount(assignInfoDict)
        self.__parsePrecomputeAssign(assignInfoDict)
        self.__parseLatexAssign(assignInfoDict)
        self.__parseVerifyInputArgs(assignInfoDict)
        
        if self.debug: 
            print("variable types: ", self.varTypes)
            print("constants: ", self.data[CONST])
            print("public: ", self.data[PUBLIC])
            print("signature: ", self.data[SIGNATURE])
            print("message: ", self.data[MESSAGE])
            print("batch_count: ", self.data[COUNT_HEADER])
            print("precompute: ", self.batch_precompute)
            print("transform: ", self.data[TRANSFORM])
            print("latex: ", self.latex_symbols)
            print("verify args: ", self.data[VERIFY])
    
    def __parseVerifyInputArgs(self, assignInfoDict):
        verifyDict = assignInfoDict.get(VERIFY)
        if verifyDict:
            if verifyDict.get('input') and self.data[COUNT_HEADER] != None:
                self.data[VERIFY] = list(verifyDict.get('input').getListNodesList())
                self.data[BATCH_VERIFY] = {}
                self.data[BATCH_VERIFY_MAP] = {}
                # figure out which bach verify args are constant and which ones are not
                for k in self.data[VERIFY]:
                    if (k in self.data[CONST]) or (k in self.data[SIGNATURE] and self.data[COUNT_HEADER][SIG_CNT] != NUM_SIGNATURES) or (k in self.data[PUBLIC] and self.data[COUNT_HEADER][PUB_CNT] != NUM_SIGNATURES) or (k in self.data[MESSAGE] and self.data[COUNT_HEADER][MSG_CNT] != NUM_SIGNATURES):
                        self.data[BATCH_VERIFY][k] = self.varTypes[k]
                    else:
                        self.data[BATCH_VERIFY][k + "list"] = "list{%s}" % self.varTypes[k]  # it is variable
                        self.data[BATCH_VERIFY_MAP][k] = k + "list"
#                print("batchverify input types: ", self.data[BATCH_VERIFY], "\n", self.data[BATCH_VERIFY].items()) 
#                print("new map for batch verify vars: ", self.data[BATCH_VERIFY_MAP])
#                sys.exit(0)
                self.partialSDL = False
        else:
            self.partialSDL = True
    
    def __parseBatchCount(self, assignInfoDict):
        countDict = assignInfoDict.get(COUNT_HEADER)
        self.data[COUNT_HEADER] = {}
        if type(countDict) == dict:
            for k,v in countDict.items():
                self.data[COUNT_HEADER][k] = v.getAssignNode().getRight().getAttribute()

    def __parsePrecomputeAssign(self, assignInfoDict):
        precomp = assignInfoDict.get(PRECOMPUTE_HEADER)
        self.data[PRECOMPUTE_HEADER] = {}
        if type(precomp) == dict:
            for k,v in precomp.items():
                node = v.getAssignNode() # might need 
                if(node.type == ops.EQ):
                    self.indiv_precompute[ node.left ] = node.right
                    self.batch_precompute[ BinaryNode.copy(node.left) ] = BinaryNode.copy(node.right)
        return
    
    def __parseLatexAssign(self, assignInfoDict):
        latex = assignInfoDict.get(LATEX_HEADER)
        if type(latex) == dict:
            for k,v in latex.items():
                self.latex_symbols[k] = v.getLineStrValue() # get second item
        return
      
    def __parseVerifyEq(self, assignInfoDict):
        non_funcDict = assignInfoDict.get(NONE_FUNC_NAME)
        if non_funcDict:
            if non_funcDict.get(VERIFY): #  and hasattr(non_funcDict[VERIFY], 'getAssignNode'):
                eq = non_funcDict[VERIFY].getAssignNode() # assumes VarInfo object
                if self.debug: print("Found verify eq: ", eq)
                self.verifyEqList.append(eq)
            else:
                for k in non_funcDict.items():
                    if VERIFY in k:# and hasattr(non_funcDict[k], 'getAssignNode'):
                        self.verifyEqList.append(non_funcDict[k].getAssignNode()) # assumes VarInfo object
        return
    
    def getVerifyEq(self):
        return self.verifyEqList

    def __parseTypes(self, assignInfoDict, varTypeDict):
        for key in varTypeDict.keys():
            # save types
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
                if values.type == ops.LIST:
                    self.data[key].extend(values.getListNodesList())
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
                return True
        else:
            return False

    def getTypes(self):
        return self.varTypes

    def getNumSignatures(self):
        return self.varTypes[NUM_SIGNATURES]
    
    def getConstantVars(self):
        return self.data[CONST]

    def getPublicVars(self):
        return self.data[PUBLIC]
    
    def getMessageVars(self):
        return self.data[MESSAGE]
    
    def getSignatureVars(self):
        return self.data[SIGNATURE]
    
    def getLatexVars(self):
        return self.latex_symbols
    
    def getPrecomputeVars(self):
        return self.indiv_precompute, self.batch_precompute

    def getTransformList(self):
        return self.data[TRANSFORM]
    
    def getBatchCount(self):
        return self.data[COUNT_HEADER]
    
    def getVerifyInputArgs(self):
        return self.data[BATCH_VERIFY]
    
    def getVerifyInputArgsMap(self):
        return self.data[BATCH_VERIFY_MAP]
    