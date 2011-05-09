import struct
import io, pickle
from base64 import *

def serializeDict(object, group):
    bytes_object = {}
    if not hasattr(group, 'serialize'):
        return None
    if isinstance(object, dict):
        for i in object.keys():
            # check the type of the object[i]
            if type(object[i]) == str:
                bytes_object[i] = object[i] # don't convert to bytes, if string
            elif type(object[i]) == dict:                
                bytes_object[i] = serializeDict(object[i], group) #; print("dict found in ser => '%s'" % i); 
            else: # typically group object
#               print("DEBUG = k: %s, v: %s" % (i, object[i]))
               bytes_object[i] = group.serialize(object[i])
        return bytes_object
    else:
        # just one bytes object and it's a string
        if type(object) == str: return bytes(object, 'utf8')
        else: return group.serialize(object)

def deserializeDict(object, group):
    bytes_object = {}
    if not hasattr(group, 'deserialize'):
       return None

    if type(object) == dict:    
        for i in object.keys():
            _type = type(object[i])
            if _type == bytes:
               bytes_object[i] = group.deserialize(object[i])
            elif _type == dict:
               bytes_object[i] = deserializeDict(object[i], group) # ; print("dict found in des => '%s'" % i);
            elif _type == str:
               bytes_object[i] = object[i]
        return bytes_object
    else:
        # just one bytes object
        return object
    
def pickleObject(object):
    valid_types = [bytes, dict, str]    
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
#    print("before enc =>", len(result))
    encoded = b64encode(result)
#    print("Result enc =>", encoded)
#    print("len =>", len(encoded))
    file.close()
    return encoded

def unpickleObject(byte_object):
#    print("bytes_object =>", byte_object)
    decoded = b64decode(byte_object)
#    print("Result dec =>", decoded)
#    print("len =>", len(decoded))
    if type(decoded) == bytes and len(decoded) > 0:
        return pickle.loads(decoded)
    return None

if __name__ == "__main__":
    data = { 'a':b"hello", 'b':b"world" }
  
    #packer = getPackerObject(data)    
    #print("packed => ", packer.pack())
    result = pickleObject(data)
    
    data2 = unpickleObject(result)
    
    print("data2 => ", data2)
