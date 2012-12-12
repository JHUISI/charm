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

    def setup(self, n):
        g1 = group.random(G1)
        msk = {'y':y, 't':t, 'v':v, 'r':r, 'm':m}
        return (pk, msk)

def main():
    grp = PairingGroup("MNT224")

    bgw05 = BGW05(grp)

if __name__ == "__main__":
    debug = True
    main()
