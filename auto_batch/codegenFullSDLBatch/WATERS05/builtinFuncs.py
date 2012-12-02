from charm.core.math.pairing import ZR
from charm.core.math.integer import randomBits
from charm.toolbox.bitstring import Bytes
from charm.toolbox.conversion import Conversion
import math
import hashlib

def stringToInt(group, strID, zz, ll):
    '''Hash the identity string and break it up in to l bit pieces'''
    h = hashlib.new('sha1')
    h.update(bytes(strID, 'utf-8'))
    _hash = Bytes(h.digest())
    val = Conversion.OS2IP(_hash) #Convert to integer format
    bstr = bin(val)[2:]   #cut out the 0b header

    v=[]
    for i in range(zz):  #z must be greater than or equal to 1
        binsubstr = bstr[ll*i : ll*(i+1)]
        intval = int(binsubstr, 2)
        intelement = group.init(ZR, intval)
        v.append(intelement)
    return v

def ceillog(group, base, value):
    return group.init(ZR, math.ceil(math.log(value, base)))
