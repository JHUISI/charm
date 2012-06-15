'''A collection of redundancy schemes'''
from charm.toolbox.bitstring import Bytes,py3
from charm.toolbox.securerandom import SecureRandomFactory
import charm.core.crypto.cryptobase
import hashlib
import math
import struct
import sys

debug = False


class InMessageRedundancy:
    '''
    :Authors: Christina Garman
    '''
    def __init__(self):
        pass        

    def encode(self, message):
        str_message = message.decode("utf-8")
        str_message += str_message[-8:]

        return str_message.encode("utf-8")
    
    def decode(self, encMessage):
        byte_message = bytearray(encMessage)

        if(byte_message[-8:] ==  byte_message[-16:-8]):
            return (True,bytes(byte_message[:-8]))
        else:
            return (False,bytes(byte_message[:-8]))

class ExtraBitsRedundancy:
    '''
    :Authors: Christina Garman
    
    TODO    
    '''
    def __init__(self):
        pass        

    def encode(self, message):
             
        return Bytes(b'\x00') + maskedSeed + maskedDB
    
    def decode(self, encMessage, label=""):

        return M
class WilliamsRedundancy:
    '''
    :Authors: Christina Garman

    TODO    
    '''
    def __init__(self):
        pass        

    def encode(self, message):
             
        return Bytes(b'\x00') + maskedSeed + maskedDB
    
    def decode(self, encMessage, label=""):

        return M
