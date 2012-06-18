from userFuncs_BSW import *

g1a = {}
g2 = {}
g1 = {}
g2alph = {}
Y = {}
g2a = {}
attrs = {}
sh = {}
coeff = {}
Cn = {}
Dn = {}
Kl = {}
KlBlinded = {}

def setup():
	global g1a
	global g2
	global g1
	global g2alph
	global g2a

	input = None
	g1 = group.random(G1)
	g2 = group.random(G2)
	alpha = group.random(ZR)
	a = group.random(ZR)
	egg = (pair(g1, g2) ** alpha)
	g1alph = (g1 ** alpha)
	g2alph = (g2 ** alpha)
	g1a = (g1 ** a)
	g2a = (g2 ** a)
	msk = [g1alph, g2alph]
	pk = [g1, g2, egg, g1a, g2a]
	output = (msk, pk)
	return output

def keygen(pk, msk, S):
	global Y
	global Kl
	global KlBlinded

	input = [pk, msk, S]
	SBlinded = S
	zz = group.random(ZR)
	g1, g2, egg, g1a, g2a = pk
	g1alph, g2alph = msk
	t = group.random(ZR)
	K = (g2alph * (g2a ** t))
	KBlinded = (K ** (1 / zz))
	L = (g2 ** t)
	LBlinded = (L ** (1 / zz))
	Y = len(S)
	for y in range(0, Y):
		z = S[y]
		Kl[z] = (group.hash(z, G1) ** t)
	for y in Kl:
		KlBlinded[y] = (Kl[y] ** (1 / zz))
	sk = [SBlinded, KBlinded, LBlinded, KlBlinded]
	skBlinded = [SBlinded, KBlinded, LBlinded, KlBlinded]
	output = (zz, skBlinded)
	return output

def encrypt(pk, M, policy_str):
	global Y
	global attrs
	global sh
	global Cn
	global Dn

	input = [pk, M, policy_str]
	g1, g2, egg, g1a, g2a = pk
	policy = createPolicy(policy_str)
	attrs = getAttributeList(policy)
	R = group.random(GT)
	hashRandM = [R, M]
	s = group.hash(hashRandM, ZR)
	s_sesskey = DeriveKey(R)
	C = (R * (egg ** s))
	sh = calculateSharesList(s, policy)
	Y = len(sh)
	Cpr = (g1 ** s)
	for y in range(0, Y):
		r = group.random(ZR)
		k = attrs[y]
		x = sh[y]
		Cn[k] = ((g1a ** x[1]) * (group.hash(k, G1) ** -r))
		Dn[k] = (g2 ** r)
		T1 = SymEnc(s_sesskey, M)
	ct = [policy_str, C, Cpr, Cn, Dn, T1]
	output = ct
	return output

if __name__ == "__main__":
	global group
	group = PairingGroup(MNT160)

	S = ['ONE', 'TWO', 'THREE']
	M = "balls on fire345"
	policy_str = '((four or three) and (two or one))'

	(msk, pk) = setup()
	(zz, skBlinded) = keygen(pk, msk, S)
	(ct) = encrypt(pk, M, policy_str)

	f_ct_BSW = open('ct_BSW.charmPickle', 'wb')
	pick_ct_BSW = objectToBytes(ct, group)
	f_ct_BSW.write(pick_ct_BSW)
	f_ct_BSW.close()

	f_pk_BSW = open('pk_BSW.charmPickle', 'wb')
	pick_pk_BSW = objectToBytes(pk, group)
	f_pk_BSW.write(pick_pk_BSW)
	f_pk_BSW.close()

	f_skBlinded_BSW = open('skBlinded_BSW.charmPickle', 'wb')
	pick_skBlinded_BSW = objectToBytes(skBlinded, group)
	f_skBlinded_BSW.write(pick_skBlinded_BSW)
	f_skBlinded_BSW.close()

	keys = {'sk':zz, 'pk':pk[2]}
	writeToFile('keys_BSW_.txt', objectOut(group, keys))

