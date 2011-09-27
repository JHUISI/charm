'''A collection of redundancy schemes'''
from toolbox.bitstring import Bytes,py3
from toolbox.securerandom import SecureRandomFactory
import charm.cryptobase
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
        #print("In redundancy encoding...")
        str_message = message.decode("utf-8")
        #print(type(str_message))
        #print(str_message)
        #print(str_message[-8:].encode("utf-8"))
        str_message += str_message[-8:]

        return str_message.encode("utf-8")
    
    def decode(self, encMessage):
        #print("In redundancy decoding...")
        byte_message = bytearray(encMessage)

        if(byte_message[-8:] ==  byte_message[-16:-8]):
            return (True,bytes(byte_message[:-8]))
        else:
            return (False,bytes(byte_message[:-8]))

class ExtraBitsRedundancy:
    '''
    :Authors: Christina Garman
    
    OAEPEncryptionPadding
    
    Implements the OAEP padding scheme.  Appropriate for RSA-OAEP encryption.
    Implemented according to PKCS#1 v2.1 Section 7 ftp://ftp.rsasecurity.com/pub/pkcs/pkcs-1/pkcs-1v2-1.pdf
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
    
    OAEPEncryptionPadding
    
    Implements the OAEP padding scheme.  Appropriate for RSA-OAEP encryption.
    Implemented according to PKCS#1 v2.1 Section 7 ftp://ftp.rsasecurity.com/pub/pkcs/pkcs-1/pkcs-1v2-1.pdf
    '''
    def __init__(self):
        pass        

    def encode(self, message):
             
        return Bytes(b'\x00') + maskedSeed + maskedDB
    
    def decode(self, encMessage, label=""):

        return M
