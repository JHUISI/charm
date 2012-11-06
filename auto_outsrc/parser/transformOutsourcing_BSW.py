from userFuncs_BSW import *

def transform(sk, ct):
    input = [sk, ct]
    id, d0, d1, d2, d3, d4 = sk
    c, c_pr = ct
    transformOutputList[0] = (d0 * d1)
    transformOutputList[1] = pair(c[0], d0)
    transformOutputList[2] = pair(c[1], d1)
    transformOutputList[3] = (pair(c[2], d2) * (pair(c[3], d3) * pair(c[4], d4)))
    output = transformOutputList
    return output

