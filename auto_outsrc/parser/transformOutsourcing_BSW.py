from userFuncs_BSW import *

def transform(sk, ct):
    input = [sk, ct]
    id, d0, d1, d2, d3, d4 = sk
    c0, c1, c2, c3, c4, cpr = ct
    transformOutputList[0] = pair(c0, d0)
    transformOutputList[1] = pair(c1, d1)
    transformOutputList[2] = pair(c2, d2)
    transformOutputList[3] = pair(c3, d3)
    transformOutputList[4] = pair(c4, d4)
    output = transformOutputList
    return output

if __name__ == "__main__":
    global group
    group = PairingGroup(MNT160)

    sk_File = open('sk_BSW.charmPickle', 'rb').read()
    sk = bytesToObject(sk_File, group)

    ct_File = open('ct_BSW.charmPickle', 'rb').read()
    ct = bytesToObject(ct_File, group)

    (transformOutputList) = transform(sk, ct)

    writeToFile('transformOutputList_BSW_.txt', objectOut(group, transformOutputList))
