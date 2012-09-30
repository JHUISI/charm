from userFuncs_LW import *

def transform(gpk, skBlinded, ct):
    input = [gpk, skBlinded, ct]
    g, g_2 = gpk
    policy_str, C0, C1, C2, C3 = ct
    gid, userS, K, deleteMeVar = skBlinded
    policy = createPolicy(policy_str)
    attrs = prune(policy, userS)
    coeff = getCoefficients(policy)
    h_gid = group.hash(gid, G1)
    Y = len(attrs)
    T0 = C0
    T2 = A
    partCT = {"T0":T0, "T1":T1, "T2":T2}
    output = partCT
    return output

if __name__ == "__main__":
    global group
    group = PairingGroup(MNT160)

    gpk_File = open('gpk_LW.charmPickle', 'rb').read()
    gpk = bytesToObject(gpk_File, group)

    skBlinded_File = open('skBlinded_LW.charmPickle', 'rb').read()
    skBlinded = bytesToObject(skBlinded_File, group)

    ct_File = open('ct_LW.charmPickle', 'rb').read()
    ct = bytesToObject(ct_File, group)

    (partCT) = transform(gpk, skBlinded, ct)

    writeToFile('partCT_LW_.txt', objectOut(group, partCT))
