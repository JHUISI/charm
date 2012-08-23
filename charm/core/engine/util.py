from __future__ import print_function
import io, pickle
import json, zlib
from base64 import *
import types

def serializeDict(object, group):
    bytes_object = {}
    if not hasattr(group, 'serialize'):
        return None
    if isinstance(object, dict):
        for i in object.keys():
            # check the type of the object[i]
            if type(object[i]) in [str, int]:
                if(type(object[i]) == str):
                    temp = 'str'+object[i]
                    bytes_object[i] = temp
                else:
                    bytes_object[i] = object[i] # don't convert to bytes, if string
            elif type(object[i]) == unicode:
                bytes_object[i] = object[i]
            elif type(object[i]) == dict:
                bytes_object[i] = serializeDict(object[i], group) #; print("dict found in ser => '%s'" % i);
            elif type(object[i]) == list:
                bytes_object[i] = serializeList(object[i], group)
            else: # typically group object
               #print("DEBUG = k: %s, v: %s" % (i, object[i]))
                bytes_object[i] = group.serialize(object[i])
        return bytes_object
    else:
        # just one bytes object and it's a string
        if type(object) == str: return bytes(object, 'utf8')
        else: return group.serialize(object)

def serializeList(object, group):
    bytes_object_ = []
    if not hasattr(group, 'serialize'):
        return None
    
    if type(object) == list:
        for i in object:
            # check the type of the object[i]
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
    elif type(object) == tuple:
        for i in object:
            # check the type of the object[i]
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
        if type(object) == str:
            return bytes(object, 'utf8')
        else: return group.serialize(object)

def serializeObject(objects, group):
    if type(objects) == dict: 
       return serializeDict(objects, group)
    # handles lists, tuples, sets, and even individual elements
    else: 
       return serializeList(objects, group)


def deserializeDict(object, group):
    bytes_object = {}
    if not hasattr(group, 'deserialize'):
       return None

    if type(object) == dict:
        for i in object.keys():
            _type = type(object[i])
            if _type == bytes:
               if(object[i][:3] == 'str'):
                   bytes_object[i] = object[i][3:]
               else:
                   bytes_object[i] = group.deserialize(object[i])
            elif _type == dict:
                bytes_object[i] = deserializeDict(object[i], group) # ; print("dict found in des => '%s'" % i);
            elif _type == list:
                bytes_object[i] = deserializeList(object[i], group)
            elif _type == str:
                bytes_object[i] = object[i]
            elif _type == int:
                bytes_object[i] = object[i]
            elif _type == unicode:
               bytes_object[i] = unicode(object[i])
        return bytes_object
    elif type(object) == bytes:
        return group.deserialize(object)
    else:
        # just one bytes object
        return object
    
def deserializeList(object, group):
    _bytes_object = []
    if not hasattr(group, 'deserialize'):
       return None

    if type(object) == list:
        for i in object:
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
    elif type(object) == tuple:
        for i in object:
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
        # just one bytes object
        return group.deserialize(object)
        # return object

def deserializeObject(objects, group):
    if type(objects) == dict: return deserializeDict(objects, group)
    else: return deserializeList(objects, group)
    
def pickleObject(object):
    valid_types = [bytes, dict, list, str, int, unicode]    
    file = io.BytesIO()
    # check that dictionary is all bytes (if not, return None)
    if isinstance(object, dict):
        for k in object.keys():
            _type = type(object[k])
            if not _type in valid_types:
               print("DEBUG: pickleObject Error!!! only bytes or dictionaries of bytes accepted."); print("invalid type =>", type(object[k]))
               return None
    pickle.dump(object, file, pickle.HIGHEST_PROTOCOL)
    result = file.getvalue()
    encoded = b64encode(result)
    file.close()
    return encoded

def unpickleObject(byte_object):
    #    print("bytes_object =>", byte_object)
    decoded = b64decode(byte_object)
    if type(decoded) == bytes and len(decoded) > 0:
        return pickle.loads(decoded)
    return None

# Two new API calls to simplify serializing to a blob of bytes
# objectToBytes() and bytesToObject()
def objectToBytes(object, group):
    object_ser = serializeObject(object, group)
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
    data = { 'a':b"hello", 'b':b"world" }
  
    #packer = getPackerObject(data)    
    #print("packed => ", packer.pack())
    result = pickleObject(data)

    data2 = unpickleObject(result)
    
    print("data2 => ", data2)
