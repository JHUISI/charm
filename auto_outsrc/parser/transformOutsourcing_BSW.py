from userFuncs_BSW import *

def transform(pk, skBlinded, ct):
	input = [pk, skBlinded, ct]
	policy_str, C, Cpr, Cn, Dn, T1 = ct
	S, K, L, Kl = skBlinded
	policy = createPolicy(policy_str)
	attrs = prune(policy, S)
	coeff = getCoefficients(policy)
	Y = len(attrs)
	A = dotprod2(range(0, Y), lam_func1, attrs, Cn, coeff, L, Kl, Dn)
	result0 = (pair(Cpr, K) * A)
	T0 = C
	T2 = result0
	partCT = {"T0":T0, "T1":T1, "T2":T2}
	output = partCT
	return output

if __name__ == "__main__":
	global group
	group = PairingGroup(MNT160)

	pk_File = open('pk_BSW.charmPickle', 'rb').read()
	pk = bytesToObject(pk_File, group)

	skBlinded_File = open('skBlinded_BSW.charmPickle', 'rb').read()
	skBlinded = bytesToObject(skBlinded_File, group)

	ct_File = open('ct_BSW.charmPickle', 'rb').read()
	ct = bytesToObject(ct_File, group)

	(partCT) = transform(pk, skBlinded, ct)

	writeToFile('partCT_BSW_.txt', objectOut(group, partCT))
