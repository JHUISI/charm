'''
Dan Boneh, Craig Gentry and Brent Waters (Pairing-based)
 
| From: "Collusion Resistant Broadcast Encryption With Short Ciphertexts and Private Keys"
| Published in: ePrint
| Available from: http://eprint.iacr.org/2005/018.pdf
| Notes: section 3.1 on page 6

* type:           broadcast encryption (public key)
* setting:        Pairing

:Authors:    J Ayo Akinyele
:Date:       1/2012
'''
from toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair

class BGW05:
    def __init__(self, groupObj):
        global group
        group = groupObj
    
    def setup(self, n):
        g1, g2 = group.random(G1), group.random(G2)
        alpha, gamma = group.random(ZR), group.random(ZR)        
        g1_l = [g1 ** alpha]; g2_l = [g2 ** alpha] 
        for i in range(1, 2 * n):
            g1_l.append(g1_l[i-1] ** alpha)
            g2_l.append(g2_l[i-1] ** alpha)
        print("Deleting element: ", n+1)
#        print("pair of e(g_n+1,g) =>", pair(g1_l[n+1], g2))
        e_gg = pair(g1_l[n+1], g2)
        # pair(mpk['g1_i'][n], mpk['g2_i'][0])
        del g1_l[n+1], g2_l[n+1]                
        v1 = g1 ** gamma; # v2 = g2 ** gamma
        
        mpk = { 'g1':g1, 'g2':g2, 'v1':v1,'g1_i':g1_l, 'g2_i':g2_l, 
                'e(gg)':e_gg, 'n':n }
        msk = { 'alpha':alpha, 'gamma':gamma }
        return (mpk, msk)
    
    def keygen(self, mpk, msk, index):
        """assume one indexed"""
        if index < 1 or index > mpk['n']:
            return "Invalid index: range[1,",mpk['n'],"]"
        i = index-1
        d1 = mpk['g1_i'][i] ** msk['gamma'] # OK
        sk = { 'i':i,'d1':d1 }
        return sk
        
    def encrypt(self, S, mpk, M):
        n = mpk['n']
        t = group.random(ZR)
        K = mpk['e(gg)'] ** t # OK: use K to protect message. e.g., M * (egg ** t)
        # print("e(g_n, g_1) :=", K)
#        print("encrypt..\ncalc K :=", K)
        C0 = mpk['g2'] ** t # OK
        dotprod = 1
        for j in S:            
            tmp = (n + 1) - j
            print("encrypt index: ", tmp)
            dotprod *= mpk['g1_i'][tmp]
    
        C1 = (mpk['v1'] * dotprod) ** t # OK
        Hdr = {'C0':C0, 'C1':C1}
        return (Hdr, K)
    
    def decrypt(self, S, mpk, sk, ct):
        n,index,d1 = mpk['n'], sk['i'], sk['d1']; (Hdr, K_ct) = ct
        C0, C1 = Hdr['C0'], Hdr['C1']; dotprod = 1
        for j in S:
            #j = j_index - 1
            for i in range(n):
                if j != i: # skip receiver index
                    tmp = (n+1)-(j+i)
                    print("decrypt index: ", tmp)
                    dotprod *= mpk['g1_i'][tmp]
                    
        K = pair(C1, mpk['g2_i'][index]) / pair(d1 * dotprod, C0)
        assert K_ct == K, "Invalid decryption. K := '%s'" % K
        print("SUCCESSFUL rec K :=", K)
        return None

def main():
    grp = PairingGroup('../param/a.param')
    S = [1]
    N = 8
    bgw = BGW05(grp)
    
    (mpk, msk) = bgw.setup(N)
    
    index = 1
    sk_1 = bgw.keygen(mpk, msk, index)

    msg = grp.random(GT)
    ct  = bgw.encrypt(S, mpk, msg)

    rec_msg = bgw.decrypt(S, mpk, sk_1, ct)
    #assert msg == rec_msg, "Invalid Decryption!!!"
    #print("SUCCESSFUL DECRYPTION!!!")

if __name__ == "__main__":
    main()
    
    
# for example, i=1 and j=2 => g_1+2
    
