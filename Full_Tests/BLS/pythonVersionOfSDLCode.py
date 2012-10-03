from charm.toolbox.pairinggroup import *
from charm.core.engine.util import *
from delIND import *

group = None

h = {}

def __init__():

    input = None
    output = None

def keygen(secParam):

    input = None
    g = group.random(G2)
    x = group.random(ZR)
    pk = (g ** x)
    sk = x
    output = (pk, sk, g)
    return output

def sign(sk, M):

    input = [sk, M]
    sig = (group.hash(M, G1) ** sk)
    output = sig
    return output

def verify(pk, M, sig, g):
    global h

    input = [pk, M, sig, g]
    h = group.hash(M, G1)
    if ( ( (pair(h, pk)) == (pair(sig, g)) ) ):
        output = True
    else:
        output = False
    return output

def main():

    input = None
    output = None

    global group
    group = PairingGroup(80)

    (pk, sk, g) = keygen(80)
    sig = sign(sk, "test")
    print(verify(pk, "test2", sig, g))

if __name__ == '__main__':
    main()
