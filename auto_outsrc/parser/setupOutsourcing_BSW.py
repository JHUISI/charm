from userFuncs_BSW import *

t3 = {}
t1 = {}
gl = {}
v1 = {}
v2 = {}
v3 = {}
v4 = {}
hl = {}
alpha = {}
h = {}
t4 = {}
t2 = {}
sk = {}
c = {}
d = {}
z = {}
dBlinded = {}

def setup(n, l):
	global t3
	global t1
	global gl
	global v1
	global v2
	global v3
	global v4
	global hl
	global alpha
	global h
	global t4
	global t2
	global z

	input = [n, l]
	alpha = group.random(ZR)
	t1 = group.random(ZR)
	t2 = group.random(ZR)
	t3 = group.random(ZR)
	t4 = group.random(ZR)
	g = group.random(G1)
	h = group.random(G2)
	omega = (pair(g, h) ** (t1 * (t2 * alpha)))
	for y in range(0, n):
		z[y] = group.random(ZR)
		gl[y] = (g ** z[y])
		hl[y] = (h ** z[y])
	v1 = (g ** t1)
	v2 = (g ** t2)
	v3 = (g ** t3)
	v4 = (g ** t4)
	mpk = [omega, g, h, gl, hl, v1, v2, v3, v4, n, l]
	msk = [alpha, t1, t2, t3, t4]
	output = (mpk, msk)
	return output

def extract(mpk, msk, id):
	global sk
	global d
	global dBlinded

	input = [mpk, msk, id]
	idBlinded = id
	zz = group.random(ZR)
	omega, g, h, gl, hl, v1, v2, v3, v4, n, l = mpk
	alpha, t1, t2, t3, t4 = msk
	r1 = group.random(ZR)
	r2 = group.random(ZR)
	hID = strToId(mpk, id)
	hashIDDotProd = dotprod2(range(0,n), lam_func1, hl, hID)
	hashID = (hl[0] * hashIDDotProd)
	d[0] = (h ** ((r1 * (t1 * t2)) + (r2 * (t3 * t4))))
	halpha = (h ** -alpha)
	hashID2r1 = (hashID ** -r1)
	d[1] = ((halpha ** t2) * (hashID2r1 ** t2))
	d[2] = ((halpha ** t1) * (hashID2r1 ** t1))
	hashID2r2 = (hashID ** -r2)
	d[3] = (hashID2r2 ** t4)
	d[4] = (hashID2r2 ** t3)
	for y in d:
		dBlinded[y] = (d[y] ** (1 / zz))
	sk = [idBlinded, dBlinded]
	skBlinded = [idBlinded, dBlinded]
	output = (zz, skBlinded)
	return output

def encrypt(mpk, M, id):
	global c

	input = [mpk, M, id]
	omega, g, h, gl, hl, v1, v2, v3, v4, n, l = mpk
	R = group.random(GT)
	hashRandM = [R, M]
	s = group.hash(hashRandM, ZR)
	s_sesskey = DeriveKey(R)
	c_pr = ((omega ** s) * R)
	s1 = group.random(ZR)
	s2 = group.random(ZR)
	hID1 = strToId(mpk, id)
	hashID1DotProd = dotprod2(range(0,n), lam_func2, gl, hID1)
	hashID1 = (gl[0] * hashID1DotProd)
	c[0] = (hashID1 ** s)
	c[1] = (v1 ** (s - s1))
	c[2] = (v2 ** s1)
	c[3] = (v3 ** (s - s2))
	T1 = SymEnc(s_sesskey, M)
	c[4] = (v4 ** s2)
	ct = [c, c_pr, T1]
	output = ct
	return output

if __name__ == "__main__":
	global group
	group = PairingGroup(MNT160)

	S = ['ONE', 'TWO', 'THREE']
	M = "balls on fire345"
	policy_str = '((four or three) and (two or one))'
	n = 10
	l = 5
	id = 'example@email.com'

	(mpk, msk) = setup(n, l)
	(zz, skBlinded) = extract(mpk, msk, id)
	(ct) = encrypt(mpk, M, id)

	f_ct_BSW = open('ct_BSW.charmPickle', 'wb')
	pick_ct_BSW = objectToBytes(ct, group)
	f_ct_BSW.write(pick_ct_BSW)
	f_ct_BSW.close()

	f_skBlinded_BSW = open('skBlinded_BSW.charmPickle', 'wb')
	pick_skBlinded_BSW = objectToBytes(skBlinded, group)
	f_skBlinded_BSW.write(pick_skBlinded_BSW)
	f_skBlinded_BSW.close()

	keys = {'sk':zz, 'pk':mpk[0]}
	writeToFile('keys_BSW_.txt', objectOut(group, keys))

