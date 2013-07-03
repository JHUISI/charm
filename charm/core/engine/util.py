from __future__ import print_function
import io, pickle
import json, zlib
from base64 import *
import types

def serializeDict(Object, group):
    bytes_object = {}
    if not hasattr(group, 'serialize'):
        return None
    if isinstance(Object, dict):
        for i in Object.keys():
            # check the type of the object[i]
            #if type(Object[i]) in [str, int]:
            #    bytes_object[i] = Object[i] # don't convert to bytes, if string
            #elif type(Object[i]) == dict:
            #    bytes_object[i] = serializeDict(Object[i], group) #; print("dict found in ser => '%s'" % i); 
            #elif type(Object[i]) == list:
            #    bytes_object[i] = serializeList(Object[i], group)                           
            #elif type(Object[i]) == bytes:
            #    tmp = b'bytes'+Object[i]
            #    bytes_object[i] = tmp

            # check the type of the object[i]
            if type(Object[i]) in [str, int]:
                if(type(Object[i]) == str):
                    temp = 'str'+Object[i]
                    bytes_object[i] = temp
                else:
                    bytes_object[i] = Object[i] # don't convert to bytes, if string
            elif type(Object[i]) == unicode:
                bytes_object[i] = Object[i]
            elif type(Object[i]) == dict:
                bytes_object[i] = serializeDict(Object[i], group) #; print("dict found in ser => '%s'" % i);
            elif type(Object[i]) == list:
                bytes_object[i] = serializeList(Object[i], group)
            else: # typically group object
               #print("DEBUG = k: %s, v: %s" % (i, object[i]))
                bytes_object[i] = group.serialize(Object[i])
        return bytes_object
    else:
        # just one bytes object and it's a string
        #if type(Object) == str: return Object
        #else: return group.serialize(Object)
        if type(Object) == str: 
           return b'str:' + Object
        elif type(Object) == unicode:
           return b'uni:' + Object 
        else: return group.serialize(Object)

def serializeList(Object, group):
    bytes_object_ = []
    if not hasattr(group, 'serialize'):
        return None
    
    if type(Object) == list:
        for i in Object:
            # check the type of the Object[i]
            if type(i) in [str, int]:
                if(type(i) == str):
                    temp = 'str'+i
                    bytes_object_.append(temp) # don't convert to bytes, if string
                else:
                    bytes_object_.append(i)
            elif type(i) == unicode:
                bytes_object_.append(i)
            elif type(i) == dict:
                bytes_object_.append(serializeDict(i, group)) #; print("dict found in ser => '%s'" % i);
            elif type(i) == list:
                bytes_object_.append(serializeList(i, group))
            else: # typically group object
               #print("DEBUG = k: %s, v: %s" % (i, object[i]))
                bytes_object_.append(group.serialize(i))
        return bytes_object_
    elif type(Object) == tuple:
        for i in Object:
            # check the type of the Object[i]
            if type(i) in [str, int]:
                if(type(i) == str):
                    temp = 'str'+i
                    bytes_object_.append(temp) # don't convert to bytes, if string
                else:
                    bytes_object_.append(i)
            elif type(i) == unicode:
                bytes_object_.append(i)
            elif type(i) == dict:
                bytes_object_.append(serializeDict(i, group)) #; print("dict found in ser => '%s'" % i);
            elif type(i) == list:
                bytes_object_.append(serializeList(i, group))
            else: # typically group object
               #print("DEBUG = k: %s, v: %s" % (i, object[i]))
                bytes_object_.append(group.serialize(i))
        return tuple(bytes_object_)
    else:
        # just one bytes object and it's a string
        if type(Object) == str: 
           return b'str:' + Object
        elif type(Object) == unicode:
           return b'uni:' + Object 
        else: return group.serialize(Object)

def serializeObject(Objects, group):
    if type(Objects) == dict: 
       return serializeDict(Objects, group)
    # handles lists, tuples, sets, and even individual elements
    else: 
       return serializeList(Objects, group)


def deserializeDict(Object, group):
    bytes_object = {}
    if not hasattr(group, 'deserialize'):
       return None

    if type(Object) == dict:    
        for i in Object.keys():
            _type = type(Object[i])
            if _type == bytes:
               if(Object[i][:3] == 'str'):
                   bytes_object[i] = Object[i][3:]
               else:
                    bytes_object[i] = group.deserialize(Object[i])
            elif _type == dict:
                bytes_object[i] = deserializeDict(Object[i], group) # ; print("dict found in des => '%s'" % i);
            elif _type == list:
                bytes_object[i] = deserializeList(Object[i], group)
            elif _type == str:
                bytes_object[i] = Object[i]
            elif _type == int:
                bytes_object[i] = Object[i]
            elif _type == unicode:
               bytes_object[i] = unicode(Object[i])
        return bytes_object
    #elif type(Object) == bytes:
    #    return group.deserialize(Object)
    #else:
        # just one bytes Object
    #    return Object
    else:
        delim = b':'
        if type(Object) == str and Object.split(delim)[0] == b'str':
            return Object.split(delim)[1]
        elif type(Object) == unicode and Object.split(delim)[0] == b'uni':
            return unicode(Object.split(delim)[1]) # keep as a byte Object
        # just one bytes Object
        return group.deserialize(Object)
        # return object
    
def deserializeList(Object, group):
    _bytes_object = []
    if not hasattr(group, 'deserialize'):
       return None

    if type(Object) == list:
        for i in Object:
            _typeL = type(i)
            if _typeL == bytes:
               if(i[:3] == 'str'):
                   _bytes_object.append(i[3:])
               else:
                   _bytes_object.append(group.deserialize(i))
            elif _typeL == dict:
                _bytes_object.append(deserializeDict(i, group)) # ; print("dict found in des => '%s'" % i);
            elif _typeL == list:
                _bytes_object.append(deserializeList(i, group))
            elif _typeL == str:
                _bytes_object.append(i)
            elif _typeL == int:
                _bytes_object.append(i)
            elif _typeL == unicode:
               _bytes_object.append(unicode(i))
        return _bytes_object
    elif type(Object) == tuple:
        for i in Object:
            _typeL = type(i)
            if _typeL == bytes:
               if(i[:3] == 'str'):
                   _bytes_object.append(i[3:])
               else:
                   _bytes_object.append(group.deserialize(i))
            elif _typeL == dict:
                _bytes_object.append(deserializeDict(i, group)) # ; print("dict found in des => '%s'" % i);
            elif _typeL == list:
                _bytes_object.append(deserializeList(i, group))
            elif _typeL == str:
                _bytes_object.append(i)
            elif _typeL == int:
                _bytes_object.append(i)
            elif _typeL == unicode:
               _bytes_object.append(unicode(i))
        return tuple(_bytes_object)
    else:
        delim = b':'
        if type(Object) == str and Object.split(delim)[0] == b'str':
            return Object.split(delim)[1]
        elif type(Object) == unicode and Object.split(delim)[0] == b'uni':
            return unicode(Object.split(delim)[1]) # keep as a byte Object
        # just one bytes Object
        return group.deserialize(Object)
        # return object

def deserializeObject(Objects, group):
    if type(Objects) == dict: return deserializeDict(Objects, group)
    else: return deserializeList(Objects, group)
    
def pickleObject(Object):
    valid_types = [bytes, dict, list, str, int, unicode]    
    file = io.BytesIO()
    # check that dictionary is all bytes (if not, return None)
    if isinstance(Object, dict):
        for k in Object.keys():
            _type = type(Object[k])
            if not _type in valid_types:
               print("DEBUG: pickleObject Error!!! only bytes or dictionaries of bytes accepted."); print("invalid type =>", type(Object[k]))
               return None
    pickle.dump(Object, file, pickle.HIGHEST_PROTOCOL)
    result = file.getvalue()
    encoded = b64encode(result)
    file.close()
    return encoded

def unpickleObject(Object):
    if type(Object) == str:
       byte_object = Object
    elif type(Object) == unicode:
       byte_object = unicode(Object)
    else:
       return None
    decoded = b64decode(byte_object)
    if type(decoded) == bytes and len(decoded) > 0:
        return pickle.loads(decoded)
    return None

# Two new API calls to simplify serializing to a blob of bytes
# objectToBytes() and bytesToObject()
def objectToBytes(Object, group):
    object_ser = serializeObject(Object, group)
    return pickleObject(object_ser)
    
def bytesToObject(byteobject, group):
    unwrap_object = unpickleObject(byteobject)
    return deserializeObject(unwrap_object, group)
    
"""
    Using serialization tools with our cryptographic schemes 
    requires that the group object is initialized 
    
    data = { 'test1':b"hello", 'test2':b"world", }
    
    dataBytes = objectToBytes(data, group)
    
    dataRec   = bytesToObject(dataBytes, group)

    assert data == dataRec, 'Error during deserialization.'    
"""

if __name__ == "__main__":
    data = { 'a':b"hello", 'b':"world", 'c':[1, 2, 3], 'd':unicode('this is a test')}
  
    #packer = getPackerObject(data)    
    #print("packed => ", packer.pack())
    result = pickleObject(data)

    data2 = unpickleObject(result)
    
    print("data2 => ", data2)
