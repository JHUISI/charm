from userFuncs_BSW import *

def transform(skBlinded, ct):
	input = [skBlinded, ct]
	id, d = skBlinded
	c, c_pr, T1 = ct
	result = (pair(c[0], d[0]) * (pair(c[1], d[1]) * (pair(c[2], d[2]) * (pair(c[3], d[3]) * pair(c[4], d[4])))))
	T0 = c_pr
	T2 = result
	partCT = {"T0":T0, "T1":T1, "T2":T2}
	output = partCT
	return output

if __name__ == "__main__":
	global group
	group = PairingGroup(MNT160)

	skBlinded_File = open('skBlinded_BSW.charmPickle', 'rb').read()
	skBlinded = bytesToObject(skBlinded_File, group)

	ct_File = open('ct_BSW.charmPickle', 'rb').read()
	ct = bytesToObject(ct_File, group)

	(partCT) = transform(skBlinded, ct)

	writeToFile('partCT_BSW_.txt', objectOut(group, partCT))
