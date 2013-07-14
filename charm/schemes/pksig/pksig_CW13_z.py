'''
| From:  J.Chen and H. Wee, Dual System Groups and its Applications - Compact HIBE and More, Manuscript.
| Published in: Manuscript
| Available from: Manuscript
| Notes: 

* type: signature (identity-based)
* setting: bilinear groups (asymmetric)

:Authors:    Fan Zhang(zfwise@gwu.edu) and Hoeteck Wee, supported by GWU computer science department
:Date:       5/2013
:Note:  The paper is not published yet. One has to notice that the implementation is different with the
paper. The code is designed to optimize the performance by reducing Exponentional operation and Multiplication
operation as much as possible.
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.crypto.cryptobase import *
from charm.toolbox.PKSig import PKSig
from charm.toolbox.matrixops import *

debug = False
class Sign_CW13(PKSig):
    def __init__(self, groupObj):
        PKSig.__init__(self)
        global group
        group = groupObj
        
    def keygen(self):
        g2 = group.random(G1)   #generator in G1
        g1 = group.random(G2)   #generator in G2
        
        #generate B and B*
        B = [[group.random(ZR), group.random(ZR)],[group.random(ZR), group.random(ZR)]]
       
        Bt = MatrixTransGroups(B)
        Bstar= [GaussEliminationinGroups([[Bt[0][0], Bt[0][1], group.init(ZR, 1)],
                                                  [Bt[1][0], Bt[1][1], group.init(ZR, 0)]]),
                GaussEliminationinGroups([[Bt[0][0], Bt[0][1], group.init(ZR, 0)],
                                                  [Bt[1][0], Bt[1][1], group.init(ZR, 1)]])]
        Bstar = MatrixTransGroups(Bstar)


        ## checks Bt * Bstar = identity matrix
#         for i in self.MatrixMulGroups(Bt, Bstar):
#             print("[%s,%s]"%(i[0],i[1]))
            
        #generate R
        R = [[group.random(ZR), group.init(ZR, 0)],
            [group.init(ZR, 0), group.init(ZR, 1)]]
        
        #generate A1 and A2
        A1 =[[group.random(ZR), group.random(ZR)],
             [group.random(ZR), group.random(ZR)]]
        A2 =[[group.random(ZR), group.random(ZR)],
             [group.random(ZR), group.random(ZR)]]
        k = [group.random(ZR),group.random(ZR)]    #k is a 2 dimentional vector
        
        BA1 = MatrixMulGroups(B,A1)
        BA2 = MatrixMulGroups(B,A2)
        BsR = MatrixMulGroups(Bstar,R)
        BsA1R = MatrixMulGroups(MatrixMulGroups(Bstar, MatrixTransGroups(A1)),R)
        BsA2R = MatrixMulGroups(MatrixMulGroups(Bstar, MatrixTransGroups(A2)),R)
        b0 = [B[0][0],B[1][0]]
        b1 = [BA1[0][0],BA1[1][0]]
        b2 = [BA2[0][0],BA2[1][0]]
        b0s = [BsR[0][0],BsR[1][0]]
        b1s = [BsA1R[0][0],BsA1R[1][0]]
        b2s = [BsA2R[0][0],BsA2R[1][0]]

        #generate the mpk
        g1b0 = [g1**b0[0], g1**b0[1]]
        g1b1 = [g1**b1[0], g1**b1[1]]
        g1b2 = [g1**b2[0], g1**b2[1]]
        egg = (pair(g2, g1)) ** (k[0]*b0[0] + k[1]*b0[1])

        pk = {'g1':g1, 'g2':g2, 'g1b0':g1b0, 'g1b1':g1b1, 'g1b2': g1b2, 'egg':egg}
        
        #generate private parameters
        sk = { 'k':k, 'b0s':b0s, 'b1s':b1s,'b2s':b2s}
        
        if(debug):
            print("Public parameters...")
            group.debug(pk)
            print("Secret parameters...")
            group.debug(sk)
        return (pk, sk)

    def sign(self, pk, sk, m):
        #_ID is an element in ZR, r is an random number in ZR
        M = group.hash(m, ZR)
        r = group.random(ZR)
        
        sig = {'K0': [pk['g2']**(sk['b0s'][0]*r),
                        pk['g2']**(sk['b0s'][1]*r)],
                 'K1': [pk['g2']**(sk['k'][0] + (sk['b2s'][0]+M*sk['b1s'][0])*r),
                        pk['g2']**(sk['k'][1] + (sk['b2s'][1]+M*sk['b1s'][1])*r)]}
        return sig
        
       
    def verify(self, pk, sig, m):
        
        M = group.hash(m,ZR)
        C0 = [pk['g1b0'][0], pk['g1b0'][1]]
        C1 = [(pk['g1b2'][0]*(pk['g1b1'][0]**M)),
              (pk['g1b2'][1]*(pk['g1b1'][1]**M))]
        C2 = (pk['egg'])

        mask = self.vpair(C0, sig['K1']) / self.vpair(C1, sig['K0'])
        return (C2 == mask)

    def vpair(self, g1v, g2v):
        return pair(g2v[0],g1v[0]) * pair(g2v[1],g1v[1])
    
def main():

    group = PairingGroup('MNT224', secparam=1024)    
    m = "plese sign this message!!!!"
    pksig = Sign_CW13(group)
    (pk, sk) = pksig.keygen()

    signature = pksig.sign(pk, sk, m)

    assert pksig.verify(pk, signature, m), "Invalid Verification!!!!"
    if debug: print("Successful Individual Verification!")
    
if __name__ == '__main__':
    debug = True
    main()   

