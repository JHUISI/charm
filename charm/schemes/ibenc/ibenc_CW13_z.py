"""
| From:  J.Chen and H. Wee, Dual System Groups and its Applications, A Compact HIBE and More, Manuscript.
| Published in: Manuscript
| Available from: Manuscript
| Notes: 

* type:           encryption (identity-based)
* setting:        bilinear groups (asymmetric)

:Authors:    Fan Zhang(zfwise@gwu.edu), supported by GWU computer science department
:Date:       5/2013
:Note:  The paper is not published yet. One has to notice that the implementation is different with the paper. 
The code is designed to optimize the performance by reducing Exponentiation and Multiplication operations as much as possible.
"""
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.crypto.cryptobase import *
from charm.toolbox.IBEnc import IBEnc
from charm.toolbox.matrixops import *

debug = False
class IBE_CW13(IBEnc):
    """
    >>> group = PairingGroup('MNT224', secparam=1024)    
    >>> ibe = IBE_CW13(group)
    >>> (master_public_key, master_secret_key) = ibe.setup()
    >>> ID = 'user@email.com'
    >>> private_key = ibe.extract(master_public_key, master_secret_key, ID)
    >>> msg = group.random(GT)
    >>> cipher_text = ibe.encrypt(master_public_key, ID, msg)
    >>> decryptedMSG = ibe.decrypt(master_public_key, private_key, cipher_text)
    >>> print (decryptedMSG==msg)
    True
    """
    def __init__(self, groupObj):
        IBEnc.__init__(self)
        #IBEnc.setProperty(self, message_space=[GT, 'KEM'], secdef='IND_sID_CPA', assumption='DBDH', secmodel='ROM', other={'id':ZR})
        global group
        group = groupObj
        
    def setup(self):
        g1 = group.random(G1)   #generator in G1
        g2 = group.random(G2)   #generator in G2
        
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
        
        #The following code differs from the paper. 
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
        egg = (pair(g1, g2)) ** (k[0]*b0[0] + k[1]*b0[1])

        mpk = {'g1':g1, 'g2':g2, 'g1b0':g1b0, 'g1b1':g1b1, 'g1b2': g1b2, 'egg':egg}
        
        #generate private parameters
        msk = { 'k':k, 'b0s':b0s, 'b1s':b1s,'b2s':b2s}
        
        if(debug):
            print("Public parameters...")
            group.debug(mpk)
            print("Secret parameters...")
            group.debug(msk)
        return (mpk, msk)

    def extract(self, mpk, msk, ID):
        #_ID is an element in ZR, r is an random number in ZR
        _ID = group.hash(ID, ZR)
        r = group.random(ZR)
        
        sk_id = {'K0': [mpk['g2']**(msk['b0s'][0]*r),
                        mpk['g2']**(msk['b0s'][1]*r)],
                 'K1': [mpk['g2']**(msk['k'][0] + (msk['b2s'][0]+_ID*msk['b1s'][0])*r),
                        mpk['g2']**(msk['k'][1] + (msk['b2s'][1]+_ID*msk['b1s'][1])*r)]}

        if(debug):
            print("Generate User SK...")
            group.debug(sk_id)
        return sk_id
        
    
    def encrypt(self, mpk, ID, M):
        #_ID is an element in ZR, s is an random number in ZR
        s = group.random(ZR)
        _ID = group.hash(ID,ZR)
        #M is an element in GT
        C0 = [mpk['g1b0'][0]**s, mpk['g1b0'][1]**s]
        C1 = [(mpk['g1b2'][0]*(mpk['g1b1'][0]**_ID))**s,
              (mpk['g1b2'][1]*(mpk['g1b1'][1]**_ID))**s]
        C2 = (mpk['egg']**s) * M

        ct_id = { 'C0':C0, 'C1':C1, 'C2':C2}
        
        if(debug):
            print('\nEncrypt...')
            group.debug(ct_id)
        return ct_id
    
    def decrypt(self, mpk, sk_id, ct_id):
        
        mask = self.vpair(ct_id['C0'], sk_id['K1']) / self.vpair(ct_id['C1'], sk_id['K0'])
        Mprime = ct_id['C2']/mask
        if(debug):
            print('\nDecrypt....')
        return Mprime

    def vpair(self, g1v, g2v):
        return pair(g1v[0],g2v[0]) * pair(g1v[1],g2v[1])
    
def main():

    group = PairingGroup('MNT224', secparam=1024)    
    ibe = IBE_CW13(group)
    (master_public_key, master_secret_key) = ibe.setup()
    ID = 'user@email.com'
    private_key = ibe.extract(master_public_key, master_secret_key, ID)
    msg = group.random(GT)
    cipher_text = ibe.encrypt(master_public_key, ID, msg)
    decryptedMSG = ibe.decrypt(master_public_key, private_key, cipher_text)
    print (decryptedMSG==msg)
    
if __name__ == '__main__':
    debug = True
    main()   

