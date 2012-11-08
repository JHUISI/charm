from userFuncs_BSW import *

def transform(pk, sk, c0, c1, c2, c3):
    input = [pk, sk, c0, c1, c2, c3]
    d = sk
    transformOutputList[0] = (pair(c1, d) * (pair(c2, d) * pair(c3, d)))
    output = transformOutputList
    return output

if __name__ == "__main__":
    global group
    group = PairingGroup(MNT160)

    pk_File = open('pk_BSW.charmPickle', 'rb').read()
    pk = bytesToObject(pk_File, group)

    sk_File = open('sk_BSW.charmPickle', 'rb').read()
    sk = bytesToObject(sk_File, group)

    c0_File = open('c0_BSW.charmPickle', 'rb').read()
    c0 = bytesToObject(c0_File, group)

    c1_File = open('c1_BSW.charmPickle', 'rb').read()
    c1 = bytesToObject(c1_File, group)

    c2_File = open('c2_BSW.charmPickle', 'rb').read()
    c2 = bytesToObject(c2_File, group)

    c3_File = open('c3_BSW.charmPickle', 'rb').read()
    c3 = bytesToObject(c3_File, group)

    (transformOutputList) = transform(pk, sk, c0, c1, c2, c3)

    writeToFile('transformOutputList_BSW_.txt', objectOut(group, transformOutputList))
