from userFuncs_LW import *

h = {}

def init():

    input = None
    tempVar = group.random(G2)
    output = None

def keygen():

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
    verify = ( (pair(h, pk)) == (pair(sig, g)) )
    output = verify
    return output

def main():

    input = None
    tempVar2 = group.random(ZR)
    output = None

