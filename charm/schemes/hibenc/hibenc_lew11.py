'''
Unbounded HIBE and Attribute-Based Encryption

| Original scheme: "A. Lewko, B. Waters Unbounded HIBE and Attribute-Based Encryption"
| Published in: Advances in Cryptology - EUROCRYPT 2011, Springer Berlin/Heidelberg, 2011
| Available from: http://eprint.iacr.org/2011/049
| Modified scheme for prime order groups: "A. Lewko Tools for Simulating Features of Composite Order Bilinear Groups in the Prime Order Setting" Section B.3
| Published in: Advances in Cryptology - EUROCRYPT 2012, Springer Berlin/Heidelberg, 2012
| Available from: http://eprint.iacr.org/2011/490

* type:           identity based encryption
* setting:        bilinear groups (symmetric)

:Authors:    N. Fotiou
:Date:       6/2014
'''
from charm.toolbox.pairinggroup import ZR,G1,G2,GT,pair
from charm.core.math.integer import integer,bitsize
from charm.toolbox.matrixops import *

debug = False
class HIBE_LW11:
    """
    >>> from charm.toolbox.pairinggroup import GT,PairingGroup
    >>> group = PairingGroup('SS512', secparam=512)
    >>> msg = group.random(GT)
    >>> #print("Message to encrypt:")
    >>> #print (msg)
    >>> I = [".gr.edu.mmlab"]
    >>> I2 = [".gr.edu.mmlab","mail"]
    >>> I3 = [".gr.edu.mmlab","mail", "fotiou"]
    >>> hibe  = HIBE_LW11(group)
    >>> (MSK,PP) = hibe.setup()
    >>> CT = hibe.encrypt(msg,I3,PP)
    >>> SK = hibe.keyGen(I,MSK,PP)
    >>> SK2 = hibe.delegate(PP,SK, I2)
    >>> SK3 = hibe.delegate(PP,SK2, I3)
    >>> M = hibe.decrypt(CT, SK3)
    >>> M == msg
    True
    >>> M = hibe.decrypt(CT, SK2)
    >>> M == msg
    True
    >>> M = hibe.decrypt(CT, SK)
    >>> M == msg
    True
    """
    def __init__(self, groupObj):
        global group
        group = groupObj
        group._verbose = True
        return

    def setup(self):
        d = [0 for x in range(10)]
        D = [0 for x in range(10)]
        gauss = [0 for x in range(10)]
        g = [0 for x in range(6)]
        G = [0 for x in range(8)]
        one = group.random(ZR)
        g_r = group.random(G1)
        for x in range(10):
            d[x] = [group.random(ZR) for y in range(10)]
        for x in range(10):
            for y in range(10):
                gauss[y] = d[y]+[group.init(ZR, 0)]
            gauss[x] = d[x] +[one]
            D[x] = GaussEliminationinGroups(gauss)
        a1, a2, theta, sigma, gamma, ksi = group.random(ZR),group.random(ZR),group.random(ZR),group.random(ZR),group.random(ZR), group.random(ZR)
        for x in range(6):
            g[x] = [g_r**d[x][y] for y in range(10)]
        G[0] = [g_r**D[0][y] for y in range(10)]
        G[1] = [g_r**D[1][y] for y in range(10)]
        G[2] = [g_r**(D[0][y]*gamma) for y in range(10)]
        G[3] = [g_r**(D[1][y]*ksi) for y in range(10)]
        G[4] = [g_r**(D[2][y]*theta) for y in range(10)]
        G[5] = [g_r**(D[3][y]*theta) for y in range(10)]
        G[6] = [g_r**(D[4][y]*sigma) for y in range(10)]
        G[7] = [g_r**(D[5][y]*sigma) for y in range(10)]
        PP = { 'e1':pair(g_r,g_r)**(a1*one), 'e2':pair(g_r,g_r)**(a2*one), 'g':g}
        MSK = {'a1':a1, 'a2':a2, 'g':G}
        if(debug):
            print("Public parameters:")
            group.debug(PP)
            print("Master Secret Key:")
            group.debug(MSK)
        return (MSK,PP)

    def keyGen(self, I, MSK, PP):
        r1,r2,y,w = [],[],[],[]
        for i in range(len(I)):
            r1.append(group.random(ZR))
            r2.append(group.random(ZR))
        for i in range(len(I)-1):
            y.append(group.random(ZR))
            w.append(group.random(ZR))
        y.append(MSK['a1'] - sum(y))
        w.append(MSK['a2'] - sum(w))
        K = [0 for x in range(len(I))]
        g = [0 for x in range(6)]
        for i in range(len(I)):
            g[0] = [MSK['g'][0][x]**y[i] for x in range(10)]
            g[1] = [MSK['g'][1][x]**w[i] for x in range(10)]
            g[2] = [MSK['g'][4][x]**(r1[i]* group.hash(I[i], ZR)) for x in range(10)]
            g[3] = [MSK['g'][5][x]**(-r1[i]) for x in range(10)]
            g[4] = [MSK['g'][6][x]**(r2[i]* group.hash(I[i], ZR)) for x in range(10)]
            g[5] = [MSK['g'][7][x]**(-r2[i]) for x in range(10)]
            K[i] = [g[0][x]*g[1][x]*g[2][x]*g[3][x]*g[4][x]*g[5][x]  for x in range(10)]
        g = []
        g.append(MSK['g'][2])
        g.append(MSK['g'][3])
        g.append(MSK['g'][4])
        g.append(MSK['g'][5])
        g.append(MSK['g'][6])
        g.append(MSK['g'][7])
        SK = {'g':g,'K':K}
        if(debug):
            print("Secret key:")
            group.debug(SK)
        return SK

    def delegate (self, PP, SK, I):
        y,w,w1, w2 = [],[],[],[]
        for i in range(len(I) -1):
            w1.append(group.random(ZR))
            w2.append(group.random(ZR))
            y.append(group.random(ZR))
            w.append(group.random(ZR))
        w1.append(group.random(ZR))
        w2.append(group.random(ZR))
        y.append (0 - sum(y))
        w.append (0 - sum(w))
        K = [0 for x in range(len(I))]
        g = [0 for x in range(6)]
        for i in range(len(I)-1):
            g[0] = [SK['g'][0][x]**y[i] for x in range(10)]
            g[1] = [SK['g'][1][x]**w[i] for x in range(10)]
            g[2] = [SK['g'][2][x]**(w1[i]* group.hash(I[i], ZR)) for x in range(10)]
            g[3] = [SK['g'][3][x]**(-w1[i]) for x in range(10)]
            g[4] = [SK['g'][4][x]**(w2[i]* group.hash(I[i], ZR)) for x in range(10)]
            g[5] = [SK['g'][5][x]**(-w2[i]) for x in range(10)]
            K[i] = [SK['K'][i][x]*g[0][x]*g[1][x]*g[2][x]*g[3][x]*g[4][x]*g[5][x]  for x in range(10)]
        i = len(I)-1
        g[0] = [SK['g'][0][x]**y[i] for x in range(10)]
        g[1] = [SK['g'][1][x]**w[i] for x in range(10)]
        g[2] = [SK['g'][2][x]**(w1[i]* group.hash(I[i], ZR)) for x in range(10)]
        g[3] = [SK['g'][3][x]**(-w1[i]) for x in range(10)]
        g[4] = [SK['g'][4][x]**(w2[i]* group.hash(I[i], ZR)) for x in range(10)]
        g[5] = [SK['g'][5][x]**(-w2[i]) for x in range(10)]
        K[i] = [g[0][x]*g[1][x]*g[2][x]*g[3][x]*g[4][x]*g[5][x]  for x in range(10)]
        SK = {'g':SK['g'],'K':K}
        if(debug):
            print("Secret key:")
            group.debug(SK)
        return SK
    
    def encrypt(self, M, I, PP):
        s1, s2 = group.random(ZR), group.random(ZR)
        t1, t2 = [],[]
        for i in range(len(I)):
            t1.append(group.random(ZR))
            t2.append(group.random(ZR))
        C0 =  M*(PP['e1']**s1)*(PP['e2']**s2)
        C = [0 for x in range(len(I))]
        g = [0 for x in range(6)]
        g[0] = [PP['g'][0][x]**s1 for x in range(10)]
        g[1] = [PP['g'][1][x]**s2 for x in range(10)]
        for i in range(len(I)):
            g[2] = [PP['g'][2][x]**t1[i] for x in range(10)]
            g[3] = [PP['g'][3][x]**(t1[i]*group.hash(I[i], ZR)) for x in range(10)]
            g[4] = [PP['g'][4][x]**t2[i] for x in range(10)]
            g[5] = [PP['g'][5][x]**(t2[i]*group.hash(I[i], ZR)) for x in range(10)]
            C[i] = [g[0][x]*g[1][x]*g[2][x]*g[3][x]*g[4][x]*g[5][x]  for x in range(10)]
        CT = {'C0':C0, 'C':C}
        if(debug):
            print("CipherText:")
            group.debug(CT)
        return CT

    def decrypt(self, CT, SK):
        B = 1
        for i in range(len(SK['K'])):
            for x in range(10):
                B*= pair(CT['C'][i][x], SK['K'][i][x])
        M = CT['C0']/ B
        return M
