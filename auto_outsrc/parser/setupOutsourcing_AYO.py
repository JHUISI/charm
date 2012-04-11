from userFuncs import *
from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.iterate import dotprod2
from charm.pairing import hash as SHA1

tau1b = {}
tau1 = {}
ga2 = {}
ga1 = {}
gb = {}
gba1 = {}
gba2 = {}
tau2 = {}
msk = {}
mpk = {}
v1 = {}
v2 = {}
egga = {}
alpha = {}
g = {}
h = {}
galpha_a1 = {}
u = {}
w = {}
v = {}
tau2b = {}
C = {}
D = {}
sk = {}
#ct = {}

def setup():
	global tau1b
	global tau1
	global ga2
	global ga1
	global gb
	global gba1
	global gba2
	global tau2
	global msk
	global mpk
	global v1
	global v2
	global egga
	global alpha
	global g
	global h
	global galpha_a1
	global u
	global w
	global v
	global tau2b

	input = None
	g = groupObj.random(G1)
	w = groupObj.random(G1)
	u = groupObj.random(G1)
	h = groupObj.random(G1)
	v = groupObj.random(G1)
	v1 = groupObj.random(G1)
	v2 = groupObj.random(G1)
	a1 = groupObj.random(ZR)
	a2 = groupObj.random(ZR)
	b = groupObj.random(ZR)
	alpha = groupObj.random(ZR)
	gb = (g ** b)
	ga1 = (g ** a1)
	ga2 = (g ** a2)
	gba1 = (gb ** a1)
	gba2 = (gb ** a2)
	tau1 = (v * (v1 ** a1))
	tau2 = (v * (v2 ** a2))
	tau1b = (tau1 ** b)
	tau2b = (tau2 ** b)
	egga = (pair(g, g) ** (alpha * (a1 * b)))
	galpha = (g ** alpha)
	galpha_a1 = (galpha ** a1)
	mpk = [g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga]
	msk = [galpha, galpha_a1, v, v1, v2, alpha]
	output = (mpk, msk)

def keygen(id):
	global D
	global sk

	input = [mpk, msk, id]
	g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga = mpk
	galpha, galpha_a1, v, v1, v2, alpha = msk
	r1 = groupObj.random(ZR)
	r2 = groupObj.random(ZR)
	z1 = groupObj.random(ZR)
	z2 = groupObj.random(ZR)
	tag_k = groupObj.random(ZR)
	r = (r1 + r2)
	id_hash = groupObj.hash(id, ZR)
	zz = groupObj.random(ZR)
	tag_kBlinded = tag_k * (1 / zz)
	D[1] = (galpha_a1 * (v ** r)) ** (1/zz)
	D[2] = ((g ** -alpha) * ((v1 ** r) * (g ** z1))) ** (1/zz) 
	D[3] = (gb ** -z1) ** (1/zz)
	D[4] = ((v2 ** r) * (g ** z2)) ** (1/zz)
	D[5] = (gb ** -z2) ** (1/zz)
	D[6] = (gb ** r2) ** (1/zz)
	D[7] = (g ** r1) ** (1/zz)
	K = ((((u ** id_hash) * (w ** tag_kBlinded)) * h) ** r1)
	sk = [id, D, K, tag_k]
	idBlinded = id
	DBlinded = D
	KBlinded = (K ** (1 / zz))
	skBlinded = [idBlinded, DBlinded, KBlinded, tag_kBlinded]
	output = (zz, skBlinded)
	return output

def encrypt(M, id):
	global C
	#global ct

	input = [mpk, M, id]
	g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, egga = mpk
	s1 = groupObj.random(ZR)
	s2 = groupObj.random(ZR)
	t = groupObj.random(ZR)
	tag_c = groupObj.random(ZR)
	s = (s1 + s2)
	id_hash2 = groupObj.hash(id, ZR)
	C[0] = (M * (egga ** s2))
	C[1] = (gb ** s)
	C[2] = (gba1 ** s1)
	C[3] = (ga1 ** s1)
	C[4] = (gba2 ** s2)
	C[5] = (ga2 ** s2)
	C[6] = ((tau1 ** s1) * (tau2 ** s2))
	C[7] = (((tau1b ** s1) * (tau2b ** s2)) * (w ** -t))
	E1 = ((((u ** id_hash2) * (w ** tag_c)) * h) ** t)
	E2 = (g ** t)
	ct = [C, E1, E2, tag_c]
	print("ct :=>", ct)
	output = ct
	return output

def transform(ct, sk):
	input = [ct, sk]
	id, D, K, tag_k = sk
	C, E1, E2, tag_c = ct
	tag = (1 / (tag_c - tag_k))
	A1 = (pair(C[1], D[1]) * (pair(C[2], D[2]) * (pair(C[3], D[3]) * (pair(C[4], D[4]) * pair(C[5], D[5])))))
	A2 = (pair(C[6], D[6]) * pair(C[7], D[7]))
	A3 = (A1 / A2)
	A4 = (pair((E1 ** tag), D[7]) * pair((E2 ** -tag), K))
	T2 = (A3 / A4)
	T0 = C[0]
	T1 = None
	partCT = [T0, T1, T2]
	output = partCT
	return output

def decout(partCT, zz):
	T0, T1, T2 = partCT
	return T0 / (T2 ** zz)

if __name__ == "__main__":
	global groupObj
	groupObj = PairingGroup('SS512')

	setup()
	id = "user@blah.com"
	M = groupObj.random(GT)
	(zz, skBlinded) = keygen(id)
	ct = encrypt(M, id)
	partCT = transform(ct, skBlinded)

	orig_M = decout(partCT, zz)
	assert M == orig_M, "no balls on fire!!!!"
	print("Successful Decryption!")

