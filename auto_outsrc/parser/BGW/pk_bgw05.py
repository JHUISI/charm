'''
Dan Boneh, Craig Gentry, and Brent Waters (Pairing-based)
 
| From: "Collusion Resistant Broadcast Encryption with Short Ciphertexts and Private Keys"
| Published in: CRYPTO '05
| Available from: http://dl.acm.org/citation.cfm?id=2153435
| Notes: 

* type:        broadcast encryption (public key)
* setting:     Pairing

:Authors:    Matthew W. Pagano
:Date:       12/2012
'''
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair

debug = True
class BGW05:
    def __init__(self, groupObj):
        global group
        group = groupObj

        n = None
        g = None

    def setup(self, nParam):
        global n, g

        n = nParam
        g = group.random(G1)
        alpha = group.random(ZR)
        giValues = {}
        for i in range(1, n):
            giValues[i] = g ^ (alpha ^ i)

        endIndexOfSecondList = (2 * n) + 1
        for i in range(n, endIndexOfSecondList, 2):
            giValues[i] = g ^ (alpha ^ i)

        gamma = group.random(ZR)
        v = g ^ gamma

        pk = {'giValues':giValues, 'v':v}
        sk = {}

        for i in range(1, (n + 1)):
            sk[i] = (giValues[i]) ^ gamma

        return (pk, sk)

    def encrypt(self, S, pk):
        giValues, v = pk

        t = group.random(ZR)

        K = (pair(giValues[n+1], g)) ^ t

        dotProd = group.init(G1)
        for j in S:
            dotProd *= giValues[n + 1 - j]

        Hdr2 = (v * dotProd) ^ t
        Hdr = ((g ^ t), Hdr2)

        return (Hdr, K)

    def decrypt(self, S, i, di, Hdr, pk):
        C0, C1 = Hdr
        giValues, v = pk

        numerator = pair(giValues[i], C1)

        dotProd = group.init(G1)
        for j in S:
            if (j == i):
                continue

            dotProd *= giValues[n + 1 - j + i]

        denominator = pair(di * dotProd, C0)

        K = numerator / denominator

        return K

def main():
    grp = PairingGroup("SS512")

    bgw05 = BGW05(grp)
    (pk, sk) = bgw05.setup(15)
    S = [1, 3, 5, 12, 14]
    (Hdr, K) = bgw05.encrypt(S, pk)
    print("K:  ", K)
    i = 1
    di = sk[i]
    Krecovered = bgw05.decrypt(S, i, di, Hdr, pk)
    print("Recovered K = ", Krecovered)
    if (K == Krecovered):
        print("Successful")
    else:
        print("Failed")

if __name__ == "__main__":
    debug = True
    main()
