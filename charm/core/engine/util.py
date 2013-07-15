from __future__ import print_function
import io, pickle
import json, zlib
from base64 import *
from charm.toolbox.bitstring import *

def serializeDict(Object, group):
    bytes_object = {}
    if not hasattr(group, 'serialize'):
        return None
    if isinstance(Object, dict):
        for i in Object.keys():
            bytes_object[i]=serializeObject(Object[i],group)
        return bytes_object

def serializeList(Object, group):
    bytes_object_ = []
    for i in Object:
        bytes_object_.append(serializeObject(i,group))
    return bytes_object_

def serializeTuple(Object, group):
    bytes_object_ = []
    for i in Object:
        bytes_object_.append(serializeObject(i,group))
    return tuple(bytes_object_)


def serializeObject(Objects, group):
    if type(Objects) == dict: 
       return serializeDict(Objects, group)
    elif type(Objects) == list:
        return serializeList(Objects, group)
    elif type(Objects) == tuple:
        return serializeTuple(Objects, group)
    elif type(Objects) == str:
        return 'str:'+Objects
    elif type(Objects) == unicode:
        return 'uni:'+Objects
    elif type(Objects) in [bytes,str,unicode,int,float]: 
       return Objects
    else:
        return group.serialize(Objects)


def deserializeDict(Object, group):
    bytes_object = {}
    if not hasattr(group, 'deserialize'):
       return None

    for i in Object.keys():
        bytes_object[i] = deserializeObject(Object[i], group)
    return bytes_object
    
def deserializeList(Object, group):
    _bytes_object = []
    for i in Object:
        _bytes_object.append(deserializeObject(i, group))
    return _bytes_object

def deserializeTuple(Object, group):
    _bytes_object = []
    for i in Object:
        _bytes_object.append(deserializeObject(i, group))
    return tuple(_bytes_object)

def deserializeObject(Objects, group):
    if type(Objects) == dict: 
       return deserializeDict(Objects, group)
    elif type(Objects) == list:
        return deserializeList(Objects, group)
    elif type(Objects) == tuple:
        return deserializeTuple(Objects, group)
    elif type(Objects) in [str,unicode]:
        tmp=Objects.split(':',1)
        (t,obj)=(tmp[0],tmp[1])
        if t=='str':
            return str(obj)
        elif t=='uni':
            return unicode(obj)
        else:
            return group.deserialize(bytes(Objects))
    else:
        return Objects
    
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

# JSON does not support 'bytes' objects, so these from/to_json 
# functions handle protecting the 
def to_json(object):
    if isinstance(object, bytes):
        return {'__class__': 'bytes', '__value__': list(object) }
    return TypeError(repr(python_ob) + " is not JSON serializable")

def from_json(json_object):
    if '__class__' in json_object:
        if json_object['__class__'] == 'bytes':
            return bytes(json_object['__value__'])
    return json_object

# Two new API calls to simplify serializing to a blob of bytes
# objectToBytes() and bytesToObject()
def objectToBytes(object, group):
    object_ser = serializeObject(object, group)
    #result = pickleObject(object_ser)
    result = getBytes(json.dumps(object_ser, default=to_json))
    return b64encode(zlib.compress(result))
    
def bytesToObject(byteobject, group):
    #unwrap_object = unpickleObject(byteobject)
    decoded = bytes.decode(zlib.decompress(b64decode(byteobject)))
    unwrap_object = json.loads(decoded, object_hook=from_json)
    return deserializeObject(unwrap_object, group)

# Note: included for backwards compatibility with older versions. 
# Will be removed completely in future versions.
def objectToBytesWithPickle(Object, group):
    object_ser = serializeObject(Object, group)
    return pickleObject(object_ser)
    
def bytesToObjectWithPickle(byteobject, group):
    print("SecurityWarning: do not unpickle data received from an untrusted source. Bad things WILL happen!")
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
