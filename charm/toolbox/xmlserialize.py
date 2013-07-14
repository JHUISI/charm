from charm.toolbox.pairinggroup import PairingGroup
from charm.toolbox.ecgroup import ECGroup
from charm.toolbox.integergroup import IntegerGroup
from charm.core.engine.util import bytesToObject,objectToBytes
from xml.dom.minidom import *

def writeToXML(object, groupObj, name=None):
    """ Output
<?xml version="1.0" ?>
<charm>
  <group param="SS512" setting="pairing">
    <object>
      This is a test!
    </object>
  </group>
</charm>
    """    
    # Create the minidom document
    doc = Document()

    # Create the <wml> base element
    charm = doc.createElement("charm")
    doc.appendChild(charm)

    # Create the main <card> element
    maingroup = doc.createElement("group")
    # make this programmatic
    setting = groupObj.groupSetting()
    param = groupObj.groupType()
    
    maingroup.setAttribute("setting", setting)
    maingroup.setAttribute("param", param)
    charm.appendChild(maingroup)

    # Create a <p> element
    if name:
        paragraph0 = doc.createElement("name")
        paragraph0.setAttribute("id", name)
        maingroup.appendChild(paragraph0)
        
    paragraph1 = doc.createElement("object")
    maingroup.appendChild(paragraph1)

    # Give the <p> elemenet some text
#    ptext = doc.createTextNode("This is a test!")
    serializedObject = objectToBytes(object, groupObj)
    ptext = doc.createTextNode(bytes.decode(serializedObject, 'utf8'))
    paragraph1.appendChild(ptext)
    
    # Print our newly created XML
    print(doc.toprettyxml(indent="  "))
    return doc.toprettyxml(indent="  ")

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    result = ''.join(rc)
    return bytes(result, 'utf8')

def parseFromXML(xmlObjectString, group=None):
    assert type(xmlObjectString) == str, "Invalid type for XML object"
    dom = parseString(xmlObjectString)
    assert dom.documentElement.tagName == "charm", "Not a Charm element"    
#    print(dom.toprettyxml(indent="  "))

    groupObj = dom.getElementsByTagName("group")
    assert groupObj != None, "Error: could not find group tag."
    groupObj = groupObj[0]
    charmObj1 = dom.getElementsByTagName("object")
    assert charmObj1 != None, "Error: could not find object tag."
    charmObj1 = charmObj1[0]
    
    structure = {}       
    setting = groupObj.getAttribute("setting")
    param = groupObj.getAttribute("param")
    
    charmObj2 = dom.getElementsByTagName("name")
    structure['name'] = None
    if charmObj2 != None: 
        charmObj2 = charmObj2[0] # what is this useful for?
        structure['name'] = charmObj2.getAttribute("id")
    
    bytesObj = getText(charmObj1.childNodes).strip()
    
    if setting == 'pairing' and group == None:
        group = PairingGroup(param)
    elif structure['setting'] == 'elliptic_curve' and group == None:
        group = ECGroup(param)
    elif structure['setting'] == 'integer':
        # TODO: this is a special case
        pass 
    return bytesToObject(bytesObj, group)
