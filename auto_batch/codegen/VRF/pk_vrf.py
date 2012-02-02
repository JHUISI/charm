'''
Susan Hohenberger and Brent Waters (Pairing-based)
 
| From: "Constructing Verifiable Random Functions with Large Input Spaces"
| Published in: ePrint
| Available from: http://eprint.iacr.org/2010/102.pdf
| Notes: applications to resetable ZK proofs, micropayment schemes, updatable ZK DBs
        and verifiable transaction escrow schemes to name a few

* type:           verifiable random functions (family of pseudo random functions)
* setting:        Pairing

:Authors:    J Ayo Akinyele
:Date:       1/2012
'''
from toolbox.pairinggroup import *
from toolbox.iterate import dotprod 
from toolbox.PKSig import PKSig
from charm.engine.util import *
import sys, random, string

debug = False
class VRF10:
    """Definition in paper: behave as Pseudo Random Functions (PRFs) with an additional property that party
    holding the seed will publish a commitment to the function and is able to non-interactively convince
    a verifier that a given evaluation is correct (matches pub commitment) without sacrificing pseudo-
    randomness property on other inputs."""
    def __init__(self, groupObj):
        global group, lam_func, debug
        group = groupObj
        debug = False
        lam_func = lambda i,a,b: a[i] ** b[i]
        
    def setup(self, n):
        """n = bit length of inputs"""
        g1 = group.random(G1)
        g2, h = group.random(G2), group.random(G2)
        u_t = group.random(ZR)
        u = [group.random(ZR) for i in range(n+1)]
        U_t = g2 ** u_t
        U1 = [g1 ** u[i] for i in range(len(u))]
        U2 = [g2 ** u[i] for i in range(len(u))]
        
        pk = { 'U1':U1, 'U2':U2,'U_t':U_t, 'g1':g1, 'g2':g2, 'h':h,'n':n   }
        sk = { 'u':u, 'u_t':u_t, 'g1':g1, 'h':h,'n':n }
        return (pk, sk)
    
    def F(self, sk, x):
        result = dotprod(1, -1, sk['n'], lam_func, sk['u'], x) 
        return pair(sk['g1'] ** (sk['u_t'] * sk['u'][0] * result), sk['h'])
    
    def prove(self, sk, x):
        pi = [i for i in range(sk['n'])]
        for i in range(sk['n']):
            result = dotprod(1, -1, i+1, lam_func, sk['u'], x) 
            pi[i] = sk['g1'] ** (sk['u_t'] * result)
        
        result0 = dotprod(1, -1, sk['n'], lam_func, sk['u'], x)
        pi_0 = sk['g1'] ** (sk['u_t'] * sk['u'][0] * result0)
        y = self.F(sk, x)
        return { 'y':y, 'pi':pi, 'pi0':pi_0 }

    def verify(self, pk, x, st):
        n, y, pi, pi_0 = pk['n'], st['y'], st['pi'], st['pi0']
        # check first index 
        check1 = pair(pi[0], pk['g2'])
        if x[0] == 0 and check1 == pair(pk['g1'], pk['U_t']):
            if debug: print("Verify: check 0 successful!\t\tcase:", x[0])
        elif x[0] == 1 and check1 == pair(pk['U1'][0], pk['U_t']):
            if debug: print("Verify: check 0 successful!\t\tcase:", x[0])            
        else: 
            if debug: print("Verify: check 0 FAILURE!\t\tcase:", x[0])            
            return False
        
        for i in range(1, len(x)):
            check2 = pair(pi[i], pk['g2'])
            if x[i] == 0 and check2 == pair(pi[i-1], pk['g2']):
                if debug: print("Verify: check", i ,"successful!\t\tcase:", x[i])
            elif x[i] == 1 and check2 == pair(pi[i-1], pk['U2'][i]):
                if debug: print("Verify: check", i ,"successful!\t\tcase:", x[i])
            else:
                if debug: print("Verify: check", i ,"FAILURE!\t\tcase:", x[i])
                return False
        
#        if pair(pi_0, pk['g2']) == pair(pi[n-1], pk['U2'][0]) and pair(pi_0, pk['h']) == y:
        if pair(pi_0, pk['g2'] * pk['h']) == pair(pi[n-1], pk['U2'][0]) * y:
            if debug: print("Verify: all and final check successful!!!")
            return True
        else:
            return False
        
def main():
    #if ( (len(sys.argv) != 7) or (sys.argv[1] == "-help") or (sys.argv[1] == "--help") ):
        #sys.exit("Usage:  python " + sys.argv[0] + " [# of valid messages] [# of invalid messages] [size of each message] [prefix name of each message] [name of valid output dictionary] [name of invalid output dictionary]")

    grp = PairingGroup('/Users/matt/Documents/charm/param/d224.param')
    
    x = [1, 0, 1, 0, 1, 0, 1, 0]
    n = 8
    vrf = VRF10(grp)
    (pk, sk) = vrf.setup(n)
    st = vrf.prove(sk, x)
    assert vrf.verify(pk, x, st), "VRF failed verification"
    print("Success!!!")

    '''
    numValidMessages = int(sys.argv[1])
    numInvalidMessages = int(sys.argv[2])
    messageSize = int(sys.argv[3])
    prefixName = sys.argv[4]
    validOutputDictName = sys.argv[5]
    invalidOutputDictName = sys.argv[6]

    f_pk = open('pk.charmPickle', 'wb')
    pick_pk = objectToBytes(pk, grp)
    f_pk.write(pick_pk)
    f_pk.close()

    validOutputDict = {}
    validOutputDict[0] = {}
    validOutputDict[0]['pk'] = 'pk.charmPickle'

    invalidOutputDict = {}
    invalidOutputDict[0] = {}
    invalidOutputDict[0]['pk'] = 'pk.charmPickle'

    for index in range(0, numValidMessages):
        if (index != 0):
            validOutputDict[index] = {}
            validOutputDict[index]['pk'] = 'pk.charmPickle'

        x = []

        for randomBitIndex in range(0, n):
            randomBit = random.randint(0, 1)
            x.append(randomBit)

        st = vrf.prove(sk, x)
        assert vrf.verify(pk, x, st), "VRF failed verification"

        f_x = open(prefixName + str(index) + '_ValidMessage.pythonPickle', 'wb')
        validOutputDict[index]['x'] = prefixName + str(index) + '_ValidMessage.pythonPickle'

        f_st = open(prefixName + str(index) + '_ValidSignature.charmPickle', 'wb')
        validOutputDict[index]['st'] = prefixName + str(index) + '_ValidSignature.charmPickle'

        pickle.dump(x, f_x)     
        f_x.close()

        pick_st = objectToBytes(st, grp)

        f_st.write(pick_st)
        f_st.close()

    dict_pickle = objectToBytes(validOutputDict, grp)
    f = open(validOutputDictName, 'wb')
    f.write(dict_pickle)
    f.close()
    del dict_pickle
    del f

    for index in range(0, numInvalidMessages):
        if (index != 0):
            invalidOutputDict[index] = {}
            invalidOutputDict[index]['pk'] = 'pk.charmPickle'

        x = []

        for randomBitIndex in range(0, n):
            randomBit = random.randint(0, 1)
            x.append(randomBit)

        st = vrf.prove(sk, x)
        assert vrf.verify(pk, x, st), "VRF failed verification"

        randomBitToChange = random.randint(0, 7)
        print(x)
        if (x[randomBitToChange] == 0):
            x[randomBitToChange] = 1
        else:
            x[randomBitToChange] = 0
        print(x)
        print("\n\n")

        shouldBeFalse = vrf.verify(pk, x, st)
        if (shouldBeFalse == True):
            sys.exit("bit flip failed")

        f_x = open(prefixName + str(index) + '_InvalidMessage.pythonPickle', 'wb')
        invalidOutputDict[index]['x'] = prefixName + str(index) + '_InvalidMessage.pythonPickle'

        f_st = open(prefixName + str(index) + '_InvalidSignature.charmPickle', 'wb')
        invalidOutputDict[index]['st'] = prefixName + str(index) + '_InvalidSignature.charmPickle'

        pickle.dump(x, f_x)     
        f_x.close()

        pick_st = objectToBytes(st, grp)

        f_st.write(pick_st)
        f_st.close()

    dict_pickle = objectToBytes(invalidOutputDict, grp)
    f = open(invalidOutputDictName, 'wb')
    f.write(dict_pickle)
    f.close()
    del dict_pickle
    del f
    '''
 
if __name__ == "__main__":
    debug = False
    main()
    
