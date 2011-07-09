'''
This class facilitates conversion between domain spaces
Created on Jul 5, 2011
@author: Gary Belvin
'''
from charm.integer import *
import charm.integer
from toolbox.bitstring import Bytes
import math

class Conversion(object):
    '''
    Input types:
        bytes
        Bytes
        int
        Integer Element
        Modular Integer Element
    
    Output types:
        int
        Group element
        Integer element
        Integer element mod N
    '''
    
    @classmethod
    def bytes2element(self, bytestr):
        '''Converts a byte string to a group element'''
        pass
   
    @classmethod
    def bytes2integer(self, bytestr):
        '''Converts a bytes string to an int of a particular bit-length?'''
        pass
   
    @classmethod
    def str2bytes(self, str):
        return Bytes(str, 'utf-8')
     
    @classmethod    
    def OS2IP(self, bytestr, element = False):
        '''Converts a byte string to an integer'''
        '''Returns a python int if element is False.
           Returns a integer.Element if element is True'''
        
        val = 0 
        for i in range(len(bytestr)):
            val += bytestr[len(bytestr)-1-i] << (8 *i)
        #These lines convert val into a binary string of 1's and 0's 
        #bstr = bin(val)[2:]   #cut out the 0b header
        #val = int(bstr, 2)
        
        #return val
        if element:
            return integer(val)
        else:
            return val
    
    @classmethod    
    def IP2OS(self, number, xLen=None):
        '''integer is a normal integer - not modular'''
        '''xLen is the intended length of the resulting octet string'''
        '''Converts an integer into a byte string'''
        ba = bytearray()
        
        if xLen == None:
            xLen = math.ceil(math.log(number, 2) / 8)
        

        if type(number) == integer:
            x = int(number)
        elif type(number) == int:
            x = number
        
        for i in range(xLen):
            ba.append(x % 256)
            x = x >> 8
        ba.reverse()
        return Bytes(ba)