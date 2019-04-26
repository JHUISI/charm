"""
The serialization API supports the following datatypes: dict, list, str, bytes, int, float, and whatever is supported by group.serialize and group.deserialize

"""

from __future__ import print_function
import io, pickle
import json, zlib
from base64 import *
from charm.toolbox.bitstring import *

def serializeDict(Object, group):
    return {
        k: serializeObject(o, group)
        for k, o in Object.items()
    }

def serializeList(Object, group):
    return [
        serializeObject(o, group)
        for o in Object
    ]

serializers = {
    dict: serializeDict,
    list: serializeList,
    tuple: serializeList,
    str: lambda obj, g: 'str:' + obj,
    bytes: lambda obj, g: 'bytes:' + obj.decode('UTF-8'),
    int: lambda obj, g: obj,
    float: lambda obj, g: obj,
}

def serializeObject(Objects, group):
    assert hasattr(group, 'serialize'), "group does not have serialize method"

    try:
        serializer = serializers[type(Objects)]
    except KeyError:
        return group.serialize(Objects)

    return serializer(Objects, group)


def deserializeDict(Object, group):
    return {
        k: deserializeObject(o, group)
        for k, o in Object.items()
    }


def deserializeList(Object, group):
    return [
        deserializeObject(o, group)
        for o in Object
    ]


def deserializeTuple(Object, group):
    return tuple(deserializeList(Object, group))


def deserializeStr(object, group):
    typ, obj = object.split(':', 1)

    if typ == 'str':
        return str(obj)
    elif typ == 'bytes':
        return getBytes(obj)

deserializers = {
    dict: deserializeDict,
    list: deserializeList,
    tuple: deserializeTuple,
    str: deserializeStr,
    bytes: lambda obj, group: group.deserialize(obj)
}

def deserializeObject(Objects, group):
    assert hasattr(group, 'deserialize'), "group does not have deserialize method"

    try:
        deserializer = deserializers[type(Objects)]
    except KeyError:
        return Objects

    return deserializer(Objects, group)
    
def pickleObject(Object):
    valid_types = [bytes, dict, list, str, int]    
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
    if type(Object) == str or type(Object) == bytes:
       byte_object = Object
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
    elif isinstance(object, tuple):
        return {'__class__': 'tuple', '__value__': list(object) }
    return TypeError(repr(object) + " is not JSON serializable")

def from_json(json_object):
    if '__class__' in json_object:
        if json_object['__class__'] == 'bytes':
            return bytes(json_object['__value__'])
        elif json_object['__class__'] == 'tuple':
            return tuple(json_object['__value__'])
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
