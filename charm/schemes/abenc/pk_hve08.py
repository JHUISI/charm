'''
Vincenzo Iovino, Giuseppe Persiano (Pairing-based)
 
| From: "Hidden-Vector Encryption with Groups of Prime Order"
| Published in: Pairing 2008
| Available from: http://dl.acm.org/citation.cfm?id=1431889
| Notes: 

* type:        predicate encryption (public key)
* setting:     Pairing

:Authors:    Matthew W. Pagano
:Date:       12/2012
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair

debug = True
class HVE08:
    def __init__(self, groupObj):
        global group
        group = groupObj

    def setup(self, n):
        g1 = group.random(G1)
        g2 = group.random(G2)
        y = group.random(ZR)
        Y = pair(g1, g2) ** y

        T = {}; t = {}; V = {}; v = {}; R = {}
        r = {}; M = {}; m = {}

        for i in range(0, n):
            t[i] = group.random(ZR)
            v[i] = group.random(ZR)
            r[i] = group.random(ZR)
            m[i] = group.random(ZR)

            T[i] = g1 ** t[i]
            V[i] = g1 ** v[i]
            R[i] = g1 ** r[i]
            M[i] = g1 ** m[i]

        pk = {'g1':g1, 'g2':g2, 'n':n, 'Y':Y, 'T':T, 'V':V, 'R':R, 'M':M}
        msk = {'y':y, 't':t, 'v':v, 'r':r, 'm':m}
        return (pk, msk)

    def keygen(self, pk, msk, yVector):
        """yVector: expects binary attributes of 0 or 1 and "dont care" attribute is represented by the value 2.
        """
        g1 = pk['g1']
        g2 = pk['g2']
        n = pk['n']
        y = msk['y']

        yVectorLen = len(yVector)
        assert (n == yVectorLen),"pk_hve08.py: length of yVector passed in to keygen is unequal to n passed in to setup."

        numNonDontCares = 0
        for i in range(0, yVectorLen):
            if (yVector[i] != 2):
                numNonDontCares += 1

        if (numNonDontCares == 0):
            sk = g2 ** y
            return sk

        a = {}
        sum_ais_soFar = 0

        for i in range(0, (numNonDontCares - 1)):
            a[i] = group.random(ZR)
            sum_ais_soFar += a[i]

        a[(numNonDontCares - 1)] = y - sum_ais_soFar
        
        YVector = {}
        LVector = {}
        current_a_index = 0

        for i in range(0, yVectorLen):
            if (yVector[i] == 0):
                YVector[i] = g2 ** (a[current_a_index] / msk['r'][i])
                LVector[i] = g2 ** (a[current_a_index] / msk['m'][i])
                current_a_index += 1
            elif (yVector[i] == 1):
                YVector[i] = g2 ** (a[current_a_index] / msk['t'][i])
                LVector[i] = g2 ** (a[current_a_index] / msk['v'][i])
                current_a_index += 1
            elif (yVector[i] == 2): # dont care attribute
                YVector[i] = group.init(G2)
                LVector[i] = group.init(G2)
            else:
                assert False,"pk_hve08.py:  one of the yVector elements is not 0, 1, or 2 (only allowable values)."

        sk = (YVector, LVector)
        return sk

    def encrypt(self, M, xVector, pk):
        g1 = pk['g1']
        n = pk['n']
        Y = pk['Y']

        s = group.random(ZR)
        
        xVectorLen = len(xVector)
        assert (n == xVectorLen),"pk_hve08.py:  the length of the xVector passed in to encrypt is unequal to the n value passed in to setup."

        s_i = {}

        for i in range(0, n):
            s_i[i] = group.random(ZR)

        omega = M * (Y ** (-s))
        C0 = g1 ** s

        XVector = {}
        WVector = {}

        for i in range(0, n):
            if (xVector[i] == 0):
                XVector[i] = pk['R'][i] ** (s - s_i[i])
                WVector[i] = pk['M'][i] ** (s_i[i])
            elif (xVector[i] == 1):
                XVector[i] = pk['T'][i] ** (s - s_i[i])
                WVector[i] = pk['V'][i] ** (s_i[i])
            else:
                assert False,"pk_hve08.py:  one of the xVector elements passed into encrypt is not either 0 or 1 (only allowable values)."

        CT = (omega, C0, XVector, WVector)
        return CT

    def decrypt(self, CT, sk):
        (omega, C0, XVector, WVector) = CT

        try:
            (YVector, LVector) = sk
        except:
            M = omega * pair(C0, sk)
            return M

        dotProd = 1

        n = len(YVector)
        if ( (n != len(LVector)) or (n != len(XVector)) or (n != len(WVector)) ):
            assert False, "pk_hve08.py:  lengths of the vectors passed to decrypt are unequal in at least one case."
        for i in range(0, n):
            if ( (YVector[i] != group.init(G2)) and (LVector[i] != group.init(G2)) ):
                dotProd *= ( pair(XVector[i], YVector[i]) * pair(WVector[i], LVector[i]) )

        M = omega * dotProd
        return M

def main():
    grp = PairingGroup("MNT224")

    hve08 = HVE08(grp)
    (pk, msk) = hve08.setup(4)
    sk = hve08.keygen(pk, msk, [0, 1, 0, 0])
    M = group.random(GT)
    print(M)
    print("\n\n")
    CT = hve08.encrypt(M, [0, 1, 0, 0], pk)
    M2 = hve08.decrypt(CT, sk)
    print(M2)
    if (M == M2):
        print("success")
    else:
        print("failed")

if __name__ == "__main__":
    debug = True
    main()
