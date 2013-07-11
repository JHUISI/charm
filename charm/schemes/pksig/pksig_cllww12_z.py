'''
Shorter IBE and Signatures via Asymmetric Pairings
  
| From: "J. Chen, H. Lim, S. Ling, H. Wang, H. Wee Shorter IBE and Signatures via Asymmetric Pairings", Section 5.
| Published in: Pairing 2012
| Available from: http://eprint.iacr.org/2012/224
| Notes: This is a shorter IBE construction based on SXDH construction.

* type:           signature (identity-based)
* setting:        bilinear groups (asymmetric)

:Improved by: Fan Zhang(zfwise@gwu.edu), supported by GWU computer science department
:Date: 	      3/2013
:Notes:
1. We swapped g1 and g2 to make signature faster.
2. Change all the pair($params_1$, $params_2$) to pair($params_2$, $params_1$) is required.
3.The code is similar with the encryption scheme, especially in setup() function.
4. Same trick in the encryption scheme applied here.
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.crypto.cryptobase import *
from charm.toolbox.PKSig import PKSig
from charm.toolbox.matrixops import *

debug = False
class Sign_Chen12_z(PKSig):
    """
    >>> from charm.toolbox.pairinggroup import PairingGroup
    >>> groupObj = PairingGroup('MNT224')
    >>> m = "plese sign this message!!!!"
    >>> cllww = Sign_Chen12_z(groupObj)
    >>> (pk, sk) = cllww.keygen()
    >>> signature = cllww.sign(pk, sk, m)
    >>> cllww.verify(pk, signature, m) 
    True
    """
    def __init__(self, groupObj):
        PKSig.__init__(self)
        #IBEnc.setProperty(self, message_space=[GT, 'KEM'], secdef='IND_sID_CPA', assumption='DBDH', secmodel='ROM', other={'id':ZR})
        global group
        group = groupObj
        
    def keygen(self):
        g2 = group.random(G1)
        g1 = group.random(G2)
        alpha = group.random(ZR)

        #generate the 4*4 dual pairing vector spaces.
        d11, d12, d13, d14 = group.random(ZR),group.random(ZR),group.random(ZR),group.random(ZR)
        d21, d22, d23, d24 = group.random(ZR),group.random(ZR),group.random(ZR),group.random(ZR)
        d31, d32, d33, d34 = group.random(ZR),group.random(ZR),group.random(ZR),group.random(ZR)
        d41, d42, d43, d44 = group.random(ZR),group.random(ZR),group.random(ZR),group.random(ZR)
        D11, D12, D13, D14 = group.init(ZR),group.init(ZR),group.init(ZR),group.init(ZR)
        D21, D22, D23, D24 = group.init(ZR),group.init(ZR),group.init(ZR),group.init(ZR)
        D31, D32, D33, D34 = group.init(ZR),group.init(ZR),group.init(ZR),group.init(ZR)
        D41, D42, D43, D44 = group.init(ZR),group.init(ZR),group.init(ZR),group.init(ZR)

        one = group.random(ZR)
        
        [D11, D12, D13, D14] = GaussEliminationinGroups([[d11, d12, d13, d14, one],
                                        [d21, d22, d23, d24, group.init(ZR, 0)],
                                        [d31, d32, d33, d34, group.init(ZR, 0)],
                                        [d41, d42, d43, d44, group.init(ZR, 0)]])
        [D21, D22, D23, D24] = GaussEliminationinGroups([[d11, d12, d13, d14, group.init(ZR, 0)],
                                        [d21, d22, d23, d24, one],
                                        [d31, d32, d33, d34, group.init(ZR, 0)],
                                        [d41, d42, d43, d44, group.init(ZR, 0)]])
        [D31, D32, D33, D34] = GaussEliminationinGroups([[d11, d12, d13, d14, group.init(ZR, 0)],
                                        [d21, d22, d23, d24, group.init(ZR, 0)],
                                        [d31, d32, d33, d34, one],
                                        [d41, d42, d43, d44, group.init(ZR, 0)]])
        [D41, D42, D43, D44] = GaussEliminationinGroups([[d11, d12, d13, d14, group.init(ZR, 0)],
                                        [d21, d22, d23, d24, group.init(ZR, 0)],
                                        [d31, d32, d33, d34, group.init(ZR, 0)],
                                        [d41, d42, d43, d44, one]])
        

        #generate public parameters.
        #PP2 = (pair(g1, g2))**(alpha*one)
        PP2 = (pair(g2, g1))**(alpha*one)
        gd11 = g1**d11
        gd12 = g1**d12
        gd13 = g1**d13
        gd14 = g1**d14
        gd21 = g1**d21
        gd22 = g1**d22
        gd23 = g1**d23
        gd24 = g1**d24
        pk = { 'PP2':PP2, 'gd11':gd11, 'gd12':gd12, 'gd13':gd13, 'gd14':gd14,
               'gd21':gd21, 'gd22':gd22, 'gd23':gd23, 'gd24':gd24 }
        #generate private parameters

        sk = {'alpha': alpha, 'g2':g2,
               'D11':D11, 'D12':D12, 'D13':D13, 'D14':D14,
               'D21':D21, 'D22':D22, 'D23':D23, 'D24':D24}

        if(debug):
            print("Public parameters...")
            group.debug(pk)
            print("Secret parameters...")
            group.debug(sk)
        return (pk, sk)

    def sign(self, pk, sk, m):
        r = group.random(ZR)
        M = group.hash(m)
        s1 = sk['g2']**((sk['alpha']+ r * M) * sk['D11'] - r * sk['D21'])
        s2 = sk['g2']**((sk['alpha']+ r * M) * sk['D12'] - r * sk['D22'])
        s3 = sk['g2']**((sk['alpha']+ r * M) * sk['D13'] - r * sk['D23'])
        s4 = sk['g2']**((sk['alpha']+ r * M) * sk['D14'] - r * sk['D24'])
        
        signature = { 's1':s1, 's2':s2, 's3':s3, 's4':s4 }
        return signature
        
    def verify(self, pk, sig, m):
        M = group.hash(m)
        if pk['PP2'] == (pair(sig['s1'],pk['gd11']*(pk['gd21']**M)) *
                         pair(sig['s2'],pk['gd12']*(pk['gd22']**M)) *
                         pair(sig['s3'],pk['gd13']*(pk['gd23']**M)) *
                         pair(sig['s4'],pk['gd14']*(pk['gd24']**M)) ):
            return True
        return False
    

def main():
    groupObj = PairingGroup('MNT224')
    m = "plese sign this message!!!!"
    cllww = Sign_Chen12_z(groupObj)
    (pk, sk) = cllww.keygen()
    signature = cllww.sign(pk, sk, m)
    
    if debug: print("Signature :=", signature)

    assert cllww.verify(pk, signature, m), "Invalid Verification!!!!"
    if debug: print("Successful Individual Verification!")
    
if __name__ == "__main__":
    debug = True
    main()
