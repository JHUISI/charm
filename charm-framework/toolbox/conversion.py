'''
:Date: Jul 5, 2011
:Authors: Gary Belvin

This class facilitates conversion between domain spaces
'''
from charm.core.math.integer import integer
from charm.toolbox.bitstring import Bytes,py3
import math

class Conversion(object):
    '''
    The goal is to convert arbitrarily between any of the following types
    
    Input types:
    
    * bytes
    * Bytes
    * int
    * Integer Element
    * Modular Integer Element
    
    Output types:
    
    * int
    * Group element
    * Integer element
    * Integer element mod N
    '''

    @classmethod
    def bytes2element(self, bytestr):
        '''Converts a byte string to a group element'''
        pass
    @classmethod
    def bytes2integer(self, bytestr):
        '''Converts a bytes string to an integer object'''
        return integer(bytestr)
    @classmethod
    def str2bytes(self, strobj):
        return Bytes(strobj, 'utf-8')
    @classmethod
    def bytes2str(self, byteobj):
        return Bytes.decode(byteobj, 'utf-8')
    
    @classmethod
    def int2bin(self, intobj):
        _str = bin(int(intobj))
        _array = []
        for i in range(2, len(_str)):
            _array.append(int(_str[i])) 
        return _array
        
    @classmethod    
    def OS2IP(self, bytestr, element = False):
        '''
        :Return: A python ``int`` if element is False. An ``integer.Element`` if element is True
        
        Converts a byte string to an integer
        '''
        val = 0 
        for i in range(len(bytestr)):
            byt = bytestr[len(bytestr)-1-i]
            if not py3: byt = ord(byt)
            val += byt << (8 *i)

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
        '''
        :Parameters:
          - ``number``: is a normal integer, not modular
          - ``xLen``: is the intended length of the resulting octet string
        
        Converts an integer into a byte string'''
        
        ba = bytearray()
        x = 0
        if type(number) == integer:
            x = int(number)
        elif type(number) == int:
            x = number
        elif not py3 and type(number) == long:
            x = number  

        if xLen == None:
            xLen = int(math.ceil(math.log(x, 2) / 8.0))
            
        for i in range(xLen):
            ba.append(x % 256)
            x = x >> 8
        ba.reverse()
        return Bytes(ba)
