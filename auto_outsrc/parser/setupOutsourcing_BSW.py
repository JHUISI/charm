from userFuncs_BSW import *

Y = {}
g = {}
h = {}
attrs = {}
sh = {}
coeff = {}
share = {}
Dj = {}
Djp = {}
Cr = {}
Cpr = {}
DjBlinded = {}

def setup():
	global g
	global h

	input = None
	g = group.random(G1)
	g2 = group.random(G2)
	alpha = group.random(ZR)
	beta = group.random(ZR)
	h = (g ** beta)
	f = (g ** (1 / beta))
	i = (g2 ** alpha)
	egg = (pair(g, g2) ** alpha)
	mk = [beta, i]
	pk = [g, g2, h, f, egg]
	output = (mk, pk)
	return output

def keygen(pk, mk, S):
	global Y
	global Dj
	global Djp
	global DjBlinded

	blindingFactor_DjBlinded = {}

	input = [pk, mk, S]
	SBlinded = S
	zz = group.random(ZR)
	r = group.random(ZR)
	p0 = (pk[1] ** r)
	D = ((mk[1] * p0) ** (1 / mk[0]))
	blindingFactor_DBlinded = group.random(ZR)
	DBlinded = (D ** (1 / blindingFactor_DBlinded))
	Y = len(S)
	for y in range(0, Y):
		s_y = group.random(ZR)
		y0 = S[y]
		Dj[y0] = (p0 * ((group.hash(y0, G2) ** s_y) * mk[1]))
		Djp[y0] = (g ** s_y)
	DjpBlinded = Djp
	for y in Dj:
		blindingFactor_DjBlinded[y] = group.random(ZR)
		DjBlinded[y] = (Dj[y] ** (1 / blindingFactor_DjBlinded[y]))
	sk = [SBlinded, DBlinded, DjBlinded, DjpBlinded]
	skBlinded = [SBlinded, DBlinded, DjBlinded, DjpBlinded]
	output = (blindingFactor_DBlinded, blindingFactor_DjBlinded, skBlinded)
	return output

def encrypt(pk, M, policy_str):
	global Y
	global attrs
	global sh
	global share
	global Cr
	global Cpr

	input = [pk, M, policy_str]
	g, g2, h, f, egg = pk
	policy = createPolicy(policy_str)
	attrs = getAttributeList(policy)
	R = group.random(GT)
	hashRandM = [R, M]
	s = group.hash(hashRandM, ZR)
	s_sesskey = DeriveKey(R)
	Ctl = (R * (egg ** s))
	sh = calculateSharesDict(s, policy)
	Y = len(sh)
	C = (h ** s)
	for y in range(0, Y):
		y1 = attrs[y]
		share[y1] = sh[y1]
		Cr[y1] = (g ** share[y1])
		Cpr[y1] = (group.hash(y1, G2) ** share[y1])
		T1 = SymEnc(s_sesskey, M)
	ct = [policy_str, Ctl, C, Cr, Cpr, T1]
	output = ct
	return output

if __name__ == "__main__":
	global group
	group = PairingGroup(MNT160)

	S = ['ONE', 'TWO', 'THREE']
	M = "balls on fire345"
	policy_str = '((four or three) and (two or one))'

	(mk, pk) = setup()
	(blindingFactor_DBlinded, blindingFactor_DjBlinded, skBlinded) = keygen(pk, mk, S)
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

	keys = {'sk':zz, 'pk':pk[4]}
	writeToFile('keys_BSW_.txt', objectOut(group, keys))

