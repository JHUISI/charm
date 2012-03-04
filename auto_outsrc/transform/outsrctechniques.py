from toolbox.pairinggroup import pair


"""
A and B :- an array of group elements in G1 and G2 respectively
a and b :- array of group elements in ZR
"""
def pairing_product(A, a, B, b):
    assert len(A) == len(B), "arrays must be of equal length! Check size of 'A' or 'B'"
    assert type(a) == dict and type(b) == dict, "exponent list should be of type 'dict'"
    default_exp = 1
    
    for i in range(len(A)):
        if a.get(i) == None: a[i] = default_exp
        if b.get(i) == None: b[i] = default_exp
    
    prod_result = 1
    for i in range(len(A)):
        prod_result *= pair(A[i] ** a[i], B[i] ** b[i])
    
    return prod_result