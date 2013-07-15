from charm.core.engine.util import objectToBytes,bytesToObject
from charm.toolbox.integergroup import IntegerGroup, integer
from charm.toolbox.pairinggroup import PairingGroup
from charm.toolbox.ecgroup import ECGroup
from charm.toolbox.eccurve import prime192v1
import unittest

debug = False

class SerializeTest(unittest.TestCase):
    def testIntegerGroup(self):    
        self.maxDiff=None
        groupObj = IntegerGroup()
        p = integer(148829018183496626261556856344710600327516732500226144177322012998064772051982752493460332138204351040296264880017943408846937646702376203733370973197019636813306480144595809796154634625021213611577190781215296823124523899584781302512549499802030946698512327294159881907114777803654670044046376468983244647367)
        data={'p':p,'String':"foo",'list':[p,{},1,1.7, b'dfa']}

        x=objectToBytes(data,groupObj)
        data2=bytesToObject(x,groupObj)
        self.assertEqual(data,data2)
    
    def testPairingGroup(self):    
        groupobj = PairingGroup('SS512')
        p=groupobj.random()
        data={'p':p,'String':"foo",'list':[p,{},1,1.7, b'dfa',]}

        x=objectToBytes(data,groupobj)
        data2=bytesToObject(x,groupobj)
        self.assertEqual(data,data2)
        
    def testECGroup(self):    
        groupObj = ECGroup(prime192v1)
        p=groupObj.random()
        data={'p':p,'String':"foo",'list':[p,{},1,1.7, b'dfa',]}

        x=objectToBytes(data,groupObj)
        data2=bytesToObject(x,groupObj)
        self.assertEqual(data,data2)
    
if __name__ == "__main__":
    unittest.main()
