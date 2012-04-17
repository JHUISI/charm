from userFuncs_BSW import *
from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.iterate import dotprod2
from charm.pairing import hash as SHA1

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
DjpBlinded = {}

def setup():
	global g
	global h

	input = None
	g = groupObj.random(G1)
	g2 = groupObj.random(G2)
	alpha = groupObj.random(ZR)
	beta = groupObj.random(ZR)
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
	global DjpBlinded

	input = [pk, mk, S]
	SBlinded = S
	zz = groupObj.random(ZR)
	r = groupObj.random(ZR)
	p0 = (pk[1] ** r)
	D = ((mk[1] * p0) ** (1 / mk[0]))
	DBlinded = (D ** (1 / zz))
	Y = len(S)
	for y in range(0, Y):
		s_y = groupObj.random(ZR)
		y0 = S[y]
		Dj[y0] = (p0 * (groupObj.hash(y0, G2) ** s_y))
		for y in Dj:
			DjBlinded[y] = (Dj[y] ** (1 / zz))
		Djp[y0] = (g ** s_y)
		for y in Djp:
			DjpBlinded[y] = (Djp[y] ** (1 / zz))
	sk = [SBlinded, DBlinded, DjBlinded, DjpBlinded]
	skBlinded = [SBlinded, DBlinded, DjBlinded, DjpBlinded]
	output = (zz, skBlinded)
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
	R = groupObj.random(GT)
	s = groupObj.hash([R, M], ZR)
	s_sesskey = DeriveKey(R)
	Ctl = (R * (egg ** s))
	sh = calculateSharesDict(s, policy)
	Y = len(sh)
	C = (h ** s)
	for y in range(0, Y):
		y1 = attrs[y]
		share[y1] = sh[y1]
		Cr[y1] = (g ** share[y1])
		Cpr[y1] = (groupObj.hash(y1, G2) ** share[y1])
	T1 = SymEnc(s_sesskey, M)
	ct = [policy_str, Ctl, C, Cr, Cpr, T1]
	output = ct
	return output

if __name__ == "__main__":
	global groupObj
	groupObj = PairingGroup('SS512')

	(mk, pk) = setup()
	(zz, skBlinded) = keygen(pk, mk, S)
	(ct) = encrypt(pk, M, policy_str)
