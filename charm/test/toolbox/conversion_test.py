'''
:Date: Jul 5, 2011
:Authors: Gary Belvin
'''
from charm.toolbox.conversion import Conversion
import unittest


class ConversionTest(unittest.TestCase):


    def testOS2IP(self):
        #9,202,000 = (0x)8c 69 50. 
        i = Conversion.OS2IP(b'\x8c\x69\x50')
        self.assertEqual(i, 9202000)
        
    def testIP2OS(self):
        #9,202,000 = (0x)8c 69 50. 
        os = Conversion.IP2OS(9202000)
        self.assertEqual(os, b'\x8c\x69\x50')
    
    def testIP2OSLen(self):
        i = 9202000
        os = Conversion.IP2OS(i, 200)
        i2 = Conversion.OS2IP(os)
        self.assertEqual(i, i2)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testOS2IP']
    unittest.main()
