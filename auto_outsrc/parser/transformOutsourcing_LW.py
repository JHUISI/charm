from userFuncs_LW import *

def transform(gpk, skBlinded, ct):
    input = [gpk, skBlinded, ct]
    g, g_2 = gpk
    policy_str, C0, C1, C2, C3, T1 = ct
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

