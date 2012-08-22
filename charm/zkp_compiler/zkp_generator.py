# Implements the proof-of-concept ZK proof compiler
# This compiler takes as input a set of public and secret inputs as well as a
# statement to be proved/verified.  It outputs the  

from pyparsing import *
from charm.zkp_compiler.zkparser import *
from charm.core.engine.protocol import *
from charm.core.engine.util import *
#from charm.core.math.pairing import *

int_default = True

def newStateFunction(func_name, args=True):
    if args:
        return """\
    def %s(self, input):\n""" % func_name
    else:
        return """\
    def %s(self):\n""" % func_name

def addToCode(lines):
    stmts = "        " # 8 spaces
    for stmt in lines:
        if type(stmt) == str:
#            print("Adding =>", stmt)
            stmts += stmt + "; "
    return stmts + "\n"

PROVER, VERIFIER = 1,2
# Handle a Schnorr HVZK proof-of-knowledge of a discrete logarithm
def KoDLFixedBase(publicDict, secretDict, baseVarKey, expVarKey, statesCode, interactive):
    if type(publicDict) != dict or type(secretDict) != dict: 
        print("Type Error!"); return None
    
    # First move of protocol: prover picks random integer "k", store k as a secret, output g^k
    stateDef = newStateFunction("prover_state1", False)
 #   stateDef += addToCode(["print('State PROVER 1:')"]) # DEBUG
    stateDef += addToCode(["pk = Protocol.get(self, "+str(list(publicDict.keys()))+", dict)"])
    prov_keys, obj_ret, ver_keys2, ver_keys4 = "","", "", []
    rand_elems,dl_elems,store_elems,non_int_def2 = [],[],[],""
    for i in range(len(expVarKey)):
        k = 'k' + str(i)
        prov_keys += expVarKey[i]+","
        rand_elems.append(k + " = self.group.random(ZR)")
        dl_elems.append("val_"+ k + " = pk['" + baseVarKey + "'] ** " + k)
        store_elems.append("Protocol.store(self, ('"+k+"',"+k+"), ('"+expVarKey[i]+"',"+expVarKey[i]+") )")
        obj_ret += "'val_"+k+"':val_"+k+", "
        ver_keys2 += ", ('val_"+k+"', input['val_"+k+"'])"
        four = 'val_'+k
        ver_keys4.append('%s' % four) # used in verify_state4
        non_int_def2 += "input['%s']," % four # used for non-interactive in state def2   
    stateDef += addToCode(["("+prov_keys+") = Protocol.get(self, "+str(list(expVarKey))+")"])
    stateDef += addToCode(rand_elems)
    stateDef += addToCode(dl_elems)
    stateDef += addToCode(store_elems)
    stateDef += addToCode(["Protocol.setState(self, 3)","return {"+obj_ret+"'pk':pk }"])
    statesCode += stateDef + "\n"

    # Second move of protocol: verifier computes random challenge c, outputs c
    stateDef2 = newStateFunction("verifier_state2")
    c = 'c'
 #   stateDef2 += addToCode(["print('State VERIFIER 2:')"]) # DEBUG
    if interactive == True:
       stateDef2 += addToCode(["c = self.group.random(ZR)"])
    else:
       stateDef2 += addToCode(["c = self.group.hash(("+str(non_int_def2)+"), ZR)"])
    stateDef2 += addToCode(["Protocol.store(self, ('c',c), ('pk',input['pk'])"+ ver_keys2 +" )", 
                            "Protocol.setState(self, 4)", "return {'c':c}"])
    statesCode += stateDef2 + "\n"
    
    stateDef3 = newStateFunction("prover_state3")
#    stateDef3 += addToCode(["print('State PROVER 3:')"]) # DEBUG
    stateDef3 += addToCode(["c = input['c']"])
    getVals, test_elems = "", ""
    compute, ver_inputs = [],[]
    prf_stmt = []
    for i in range(len(expVarKey)):
        z,k = 'z' + str(i),'k' + str(i)
        getVals += "'"+ expVarKey[i] +"','"+k+"',"
        compute.append(z + " = val['"+expVarKey[i]+"'] * c + val['"+k+"']")
        test_elems += "'"+z+"':"+z+","
        ver_inputs.append(z + " = input['"+z+"']")
        prf_stmt.append("val['pk']['"+baseVarKey+"'] ** "+z) # used in verify_state4
        
    stateDef3 += addToCode(["val = Protocol.get(self, ["+getVals+"], dict)"])
    stateDef3 += addToCode(compute)
    stateDef3 += addToCode(["Protocol.setState(self, 5)", "return {"+test_elems+"}"])
    statesCode += stateDef3 + "\n"
    
    stateDef4 = newStateFunction("verifier_state4")
#    stateDef4 += addToCode(["print('State VERIFIER 4:')"]) # DEBUG    
    stateDef4 += addToCode(ver_inputs)
    pk = ['pk']
    pk.extend(ver_keys4); pk.append('c')

    stateDef4 += addToCode(["val = Protocol.get(self, "+ str(pk) +", dict)"])
    # need to compute g^z =?= g^k (val_k) * (pubkey)^c
    verify4_stmt = []
    for i in range(len(expVarKey)):
        pub_key = secretDict[ expVarKey[i] ] # get pubkey for secret
        verify4_stmt.append("\n        if ("+ prf_stmt[i] + ") == " + "((val['pk']['"+pub_key+"'] ** val['c']) * val['"+ver_keys4[i]+"'] ): result = 'OK'\n        else: result = 'FAIL'")
#        verify4_stmt.append("print(val['pk']['g']); result = 'OK'")    
    stateDef4 += addToCode(verify4_stmt)
    stateDef4 += addToCode(["Protocol.setState(self, 6)", "Protocol.setErrorCode(self, result)"] )
    stateDef4 += addToCode(["print('Result => ',result); return result"])  
    statesCode += stateDef4 + "\n"

    stateDef5 = newStateFunction("prover_state5")
#    stateDef5 += addToCode(["print('State PROVER 5:')"]) # DEBUG
    stateDef5 += addToCode(["Protocol.setState(self, None)", "Protocol.setErrorCode(self, input); return None"])
    statesCode += stateDef5 + "\n"
    
    stateDef6 = newStateFunction("verifier_state6")
#    stateDef6 += addToCode(["print('State VERIFIER 6:')"]) # DEBUG    
    stateDef6 += addToCode(["Protocol.setState(self, None)", "return None"])
    statesCode += stateDef6 + "\n"
    
#    print("Finishing state 1 =>", statesCode)    
    f = open('tmpGenCode.py', 'w')
    f.write(statesCode)
    f.close()

    return statesCode


# Return a fixed preamble for an interactive ZK proof protocol.
def genIZKPreamble():
    return """\
\nfrom charm.engine.protocol import *
from charm.engine.util import *
from socket import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair

class %s(Protocol):
    def __init__(self, groupObj, common_input=None):
        Protocol.__init__(self, None)
        PROVER,VERIFIER = %s,%s
        prover_states = { 1:self.prover_state1, 3:self.prover_state3, 5:self.prover_state5 }
        verifier_states = { 2:self.verifier_state2, 4:self.verifier_state4, 6:self.verifier_state6 }
        prover_trans = { 1:3, 3:5 }
        verifier_trans = { 2:4, 4:6 }
        # describe the parties involved and the valid transitions
        Protocol.addPartyType(self, VERIFIER, verifier_states, verifier_trans)
        Protocol.addPartyType(self, PROVER, prover_states, prover_trans, True)

        # must pass in a group object parameter (allows us to operate in any setting)
        self.group = groupObj

        if common_input == None: # generate common parameters to P and V
           db = {}
           self.__gen_setup = True
        else: # can be used as a sub-protocol if common_input is specified by caller
           db = common_input
           self.__gen_setup = False
        self.PROVER, self.VERIFIER = PROVER, VERIFIER
        Protocol.setSubclassVars(self, self.group, db)\n"""

# public contains a dictionary of the public group elements (keys appropriately labeled)
# secret contains a dictionary of the secret elements (keys must be appropriately labeled)
# statement is the statement for which we would like to prove via ZK and thus code 
# we need to generate to prove the statement.
def parseAndGenerateCode(public, secretDict, statement, party_ID, interactive):
    # parse the statement such that we know the baseVar, expName (secret)
    output = genIZKPreamble()
    output = output % ('ZKProof', PROVER, VERIFIER)

    parser = ZKParser()
    stmt_object = parser.parse(statement)
    pk, sk = [], []
    gen, sec = [], {}
    extract(stmt_object, pk, sk, sec, gen)
    # Get the preamble (including class definition and __init__ routine
#    print("Public params...", pk)
#    print("Secret keys...", sk)
#    print("Secret key =>", sec)

    baseVar = gen.pop() # NOTE: we only support one generator for now (i.e. 'g'), for more advanced
    expSecret = sk # e.g. ['x', 'y',...]
    secret = sec # mapping of secret to public key (e.g. {'x':'h', 'y':'j'}
    
#    print("Input public =>", public)
#    print("Input private =>", secret)

    final_src = KoDLFixedBase(public, secret, baseVar, expSecret, output, interactive)
    return final_src
    
def extract(node, pk, sk, sk_pk_map, gen):
    if node.type == node.EXP:
#        print("public =>", node.getLeft(), "in pk?")
#        print("secret =>", node.getRight(), "in sk?")
        if not node.getLeft() in pk:
            pk.append(node.getLeft())
        if not node.getLeft() in gen:
            gen.append(node.getLeft())  # ONLY SUPPORT 1 generator (may need to re-arch generator to support multiple gens)    
        sk.append(node.getRight())
            
    elif node.type == node.EQ:
#        print("public =>", node.getLeft(), "in pk?")
        extract(node.getRight(), pk, sk, sk_pk_map, gen)        
        sec_key = sk.pop()
        sk_pk_map[sec_key] = node.getLeft()
        sk.append(sec_key)
        if not node.getLeft() in pk:
            pk.append(node.getLeft())
    elif node.type == node.AND:
        extract(node.getLeft(), pk, sk, sk_pk_map, gen)
        extract(node.getRight(), pk, sk, sk_pk_map, gen)
    else:
        return None
    return None

# does tyep checking on the parsed statement object to determine 
# 1) all the public keys (in stmt) appear in pk
# 2) all the secret keys (in stmt) appear in sk
def dict_check(node, pk, sk):
    if node.type == node.EXP:
       if not node.getLeft() in pk: return False
       if not node.getRight() in sk: return False
    elif node.type == node.EQ:
        if not node.getLeft() in pk: return False
        return dict_check(node.getRight(), pk, sk)
    elif node.type == node.AND:
        if dict_check(node.getLeft(), pk, sk) == False: return False
        if dict_check(node.getRight(), pk, sk) == False: return False
    elif node.type == node.OR:
        if dict_check(node.getLeft(), pk, sk) or dict_check(node.getLeft(), pk, sk): return True
        else: return False
    return True

def write_out(name, prefix, value):
    f = open(name, 'a')
    f.write(str(prefix) + " => " + str(value) + "\n")
    f.close()


# Generate an interactive ZK proof from a statement and variables.  The output
# of this function is a subclass of Protocol.  To execute the proof, first
# set it up using the Protocol API and run Execute().
def executeIntZKProof(public, secret, statement, party_info, interactive=int_default):
    print("Executing Interactive ZK proof...")
    # verify that party_info contains wellformed dictionary
    party_keys = set(['party', 'setting', 'socket'])
    if not party_keys.issubset(set(party_info.keys())):
        missing_keys = party_keys.difference_update(set(party_info_keys()))
        print("Required key/values missing: '%s'" % missing_keys)
        return None
    
    p_name, p_socket, groupObj = party_info['party'], party_info['socket'], party_info['setting']
    if p_name.upper() == 'PROVER': partyID = PROVER
    elif p_name.upper() == 'VERIFIER': partyID = VERIFIER
    else: print("Unrecognized party!"); return None

    # Parse through the statement and insert code into each state of the prover and/or verifier
    ZKClass = parseAndGenerateCode(public, secret, statement, partyID, interactive)    
    dummy_class = '<string>'
    proof_code = compile(ZKClass, dummy_class, 'exec')
    print("Proof code object =>", proof_code)    
#    return proof_code
    ns = {} 
    exec(proof_code, globals(), ns)    
    ZKProof = ns['ZKProof']

    prov_db = None
    if(partyID == PROVER):
        prov_db = {}; prov_db.update(public); prov_db.update(secret)
    zkp = ZKProof(groupObj, prov_db)
    zkp.setup( {'name':p_name.lower(), 'type':partyID, 'socket':p_socket}) 
    # is there a way to check type of socket?
    zkp.execute(partyID)
    return zkp.result

def executeNonIntZKProof(public, secret, statement, party_info):
    print("Executing Non-interactive ZK proof...")
    return executeIntZKProof(public, secret, statement, party_info, interactive=False)
    
