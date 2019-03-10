# TODO: provide a transition checker that prevents a feedback loop, inconsistent state.
# in user db that way user can eliminate store step on the receive side.

from charm.core.engine.util import *
from charm.toolbox.enum import Enum
from math import log, ceil

debug = False
# standardize responses between client and server
# code = Enum('Success', 'Fail', 'Repeat', 'StartSubprotocol', 'EndSubprotocol')
class Protocol:
    def __init__(self, error_states, max_size=2048): # any init information?
        global error
        self.p_ID = 0
        self.p_ctr = 0
        error = error_states
        # dictionary of party types (each type gets an identifier)
        self.partyTypes = {}
        self.party = {}
        self._serialize = False
        self.db = {} # initialize the database
        self.max_size = max_size
        self.prefix_size = ceil(log(max_size, 256))
        
    def setup(self, *args):
        # handles the hookup between parties involved
        Error = True
        for arg in args:
            if isinstance(arg, dict):
               print("Setup of: ", arg['name'])
               if not self.addInstance(arg): Error = False
            else:
               print(type(arg))
        return Error

    def addInstance(self, obj):
        p_ctr = self.p_ctr
        for i in self.partyTypes.keys():
            if i == obj['type']: # we find the party type
               self.party[p_ctr] = {}
               self.party[p_ctr]['name'], self.party[p_ctr]['socket'] = obj['name'], obj['socket']
               self.party[p_ctr]['type'], self.party[p_ctr]['states'] = obj['type'], self.partyTypes[i]['states']
               self.party[p_ctr]['init'] = self.partyTypes[i]['init']
               self.p_ctr += 1
               print("Adding party instance w/ id: ", p_ctr)
               return True
        return None

    def addPartyType(self, type, state_map, trans_map, init_state=False):
        ExistingTypeFound = False
        # see if type already exists. break and return if so
        for i in self.partyTypes.keys():
            if self.partyTypes[i]['type'] == type:
                ExistingTypeFound = True
                break
        # means we are adding a new type    
        if not ExistingTypeFound:
           p_ID = self.p_ID
           party = {'type':type, 'id':p_ID }
           if(isinstance(state_map, dict)):
              party['states'] = state_map # function pointers for state functions...
           if(isinstance(trans_map, dict)):
              party['transitions'] = trans_map          
           party['init'] = init_state  # which state initializes the protocol
           self.partyTypes[type] = party  # makes sure
           self.p_ID += 1
           return True
        return False
#    
#    def addValidTransitions(self, trans_map):
#        if isinstance(trans_map, dict):    
#            self.trans_map = trans_map
   
    def listStates(self, partyID):
        # check if a member parameter is defined
        if partyID < self.p_ctr:
            return self.party[partyID]['states']
        return None
    
    def listParties(self):
        return list(self.party.keys())

    def listParyTypes(self):
        return list(self.partyTypes.keys())

    def getInitState(self, _type):
        for i in self.listParties():
            if self.party[i]['type'] == _type: 
                self._socket = self.party[i]['socket'] 
                if self.party[i]['init']:
                    # set current trans starting point
                    self.cur_state = 1
                    return (True, self.listStates(i)[1])
                else:
                    self.cur_state = 2
                    return (False, self.listStates(i)[2])
        print("Returning junk!")
        return (False, None)
    
    def setState(self, state_num):
        # find the corresponding call back based on current party id
        self.nextCall = None        
        if state_num == None: return None   
        nextPossibleState = self._cur_trans.get(self.cur_state)
        if type(nextPossibleState) == list and not state_num in nextPossibleState:
           print("Invalid State Transition! Error!")
           print("\tCurrent state: ", self.cur_state)
           print("\tNext state: ", state_num)
           print("Allowed states: ", nextPossibleState)        
        elif type(nextPossibleState) != list and nextPossibleState != state_num: 
           print("Invalid State Transition! Error!")
           print("\tCurrent state: ", self.cur_state)
           print("\tNext state not allowed: ", state_num)
           # do not make the transition
           return None
            
        for i in self.listParties():
            states = self.listStates(i)
            if states.get(state_num) != None: 
               self.nextCall = states.get(state_num)
               # preparing for state transition here.
               self.cur_state = state_num
               break
        return None
    
    def send_msg(self, object):
        # use socket to send message (check if serializaton is required)
        if self._socket != None:
            if self._serialize:
                result = self._user_serialize(object)
            else:
                result = self.serialize(object)
                #print("DEBUG: send_msg : result =>", result)
            if len(result) > self.max_size:
                print("Message too long! max_size="+str(self.max_size))
                return None
            result = len(result).to_bytes(length=self.prefix_size, byteorder='big') + result
            self._socket.send(result)
        return None

    # receives exactly n bytes
    def recv_all(self, n):
        recvd = 0
        res = b''
        while recvd < n:
            res = res + self._socket.recv(n-recvd)
            recvd = len(res)
        return res

    def recv_msg(self):
        # read the socket and return the received message (check if deserialization)
        # is necessary
        if self._socket != None:
            # block until data is available or remote host closes connection
            msglen = int.from_bytes(self.recv_all(self.prefix_size), byteorder='big')
            result = self.recv_all(msglen)

            if result == '': return None
            else: 
                if self._serialize:
                    return self._user_deserialize(result)
                else: # default serialize call
                    return self.deserialize(result)
        return None
    
#    # serialize an object
#    def serialize(self, object):
#        if type(object) == str:
#            return bytes(object, 'utf8')
#        return object
#    
#    def deserialize(self, object):
#        if type(object) == bytes:
#            return object.decode('utf8')
#        return object
    def setSubclassVars(self, group, state=None):
        if hasattr(group, 'serialize') and hasattr(group, 'deserialize'):
            self.group = group
        if state != None:
            if type(state) == dict:
                self.db = state
        
    def get(self, keys, _type=tuple):
        if not type(keys) == list: return
        if _type == tuple:
            ret = []
        else: ret = {}
        # get the data 
        for i in keys:
            if _type == tuple:
                ret.append(self.db[i])
            else: # dict
                ret[ i ] = self.db[i]            
        # return data
        if _type == tuple:                
            return tuple(ret)
        return ret
    
    def store(self, *args):
        for i in args:
            if isinstance(i, tuple):
                self.db[ i[0] ] = i[1]
        return None
    
    def serialize(self, object):
#        print("input object... => ", object)
        if type(object) == dict:
            bytes_object = serializeDict(object, self.group)
            return pickleObject(bytes_object)
        elif type(object) == str:
            return pickleObject(object)
        else:
#            print("serialize: just =>", object)
            return object
    
    def deserialize(self, bytes_object):
#        print("deserialize input =>", bytes_object)
        if type(bytes_object) == bytes:
            object = unpickleObject(bytes_object)
            if isinstance(object, dict):
                return deserializeDict(object, self.group)            
                
            return object
    # OPTIONAL
    # derived class must call this function in order to 
    def setSerializers(self, serial, deserial):
        self._serialize = True
        self._user_serialize = serial
        self._user_deserialize = deserial
        return None
        
    # records the final state of a protocol execution
    def setErrorCode(self, value):
        self.result = value
        
    # executes state machine from the 'party_type' perspective 
    def execute(self, party_type, close_sock=True):
        print("Party Descriptions:")
        print(self.listParyTypes(), "\n")
#        print("Executing protocol engine...")
        # assume there are two parties: support more in the future.
#        if len(self.listParties()) == 2:
#            p1, p2 = self.listParties()
#        print(self.listParties())
            
        # main loop
#        Timeout = False
        (start, func) = self.getInitState(party_type)
        self._cur_trans = self.partyTypes[party_type]['transitions'] 
        #print("Possible transitions: ", self._cur_trans)
        print("Starting Point => ", func.__name__)
        if start == True:
            # call the first state for party1, then send msg
            output = func.__call__()
            if type(output) == dict: self.db.update(output)
            self.send_msg(output)
        else:
            # first receive message, call state function
            # then send call response
            input = self.recv_msg()
            if type(input) == dict:
#                print("input db :=>", input)
                self.db.update(input)
            output = func.__call__(input)
            if isinstance(output, dict):
#                print("output db :=>", output)
                self.db.update(output)
            self.send_msg(output)
        # take output and send back to other party via socket

        while self.nextCall != None: 
             input = self.recv_msg()
             if isinstance(input, dict): self.db.update(input)
             output = self.nextCall.__call__(input)
             if output != None: 
                 if isinstance(output, dict): self.db.update(output)
                 self.send_msg(output)
        if close_sock:
           self.clean()
        return output
    
    def check(self):
        # cycle through parties, make sure they are differntly typed?
        # p_ID must be at least 2
        # ...
        pass
    
    def clean(self):
        if debug: print("Cleaning database...")
        self._socket.close()
        self.db.clear()
        print("PROTOCOL COMPLETE!")
        return None
