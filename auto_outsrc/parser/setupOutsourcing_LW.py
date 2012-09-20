from userFuncs_LW import *

attrs = {}
policy = {}
C1 = {}
C0 = {}
K = {}
g_2 = {}
C3 = {}
Y = {}
C2 = {}
g = {}
y = {}
z = {}
s_sh = {}
w_sh = {}
coeff = {}

def setup():
	global g_2
	global g

	input = None
	g = group.random(G1)
	g_2 = group.random(G2)
	gpk = [g, g_2]
	output = gpk
	return output

def authsetup(gpk, authS):
	global Y
	global y
	global z

	msk = {}
	pk = {}

	input = [gpk, authS]
	g, g_2 = gpk
	Y = len(authS)
	for i in range(0, Y):
		alpha = group.random(ZR)
		y = group.random(ZR)
		z = authS[i]
		eggalph = (pair(g, g_2) ** alpha)
		g2y = (g_2 ** y)
		msk[z] = [alpha, y]
		pk[z] = [eggalph, g2y]
	output = (msk, pk)
	return output

def keygen(gpk, msk, gid, userS):
	global K
	global Y
	global z

	input = [gpk, msk, gid, userS]
	g, g_2 = gpk
	h = group.hash(gid, G1)
	deleteMeVar = msk[0][0]
	Y = len(userS)
	for i in range(0, Y):
		z = userS[i]
		K[z] = ((g ** msk[z][0]) * (h ** msk[z][1]))
	sk = [gid, userS, K, deleteMeVar]
	output = sk
	return output

def encrypt(pk, gpk, M, policy_str):
	global attrs
	global policy
	global C1
	global C0
	global C3
	global Y
	global C2
	global s_sh
	global w_sh

	input = [pk, gpk, M, policy_str]
	g, g_2 = gpk
	policy = createPolicy(policy_str)
	attrs = getAttributeList(policy)
	s = group.random(ZR)
	w = 0
	s_sh = calculateSharesDict(s, policy)
	w_sh = calculateSharesDict(w, policy)
	Y = len(s_sh)
	egg = pair(g, g_2)
	C0 = (M * (egg ** s))
	for y in range(0, Y):
		r = group.random(ZR)
		k = attrs[y]
		C1[k] = ((egg ** s_sh[k]) * (pk[k][0] ** r))
		C2[k] = (g_2 ** r)
		C3[k] = ((pk[k][1] ** r) * (g_2 ** w_sh[k]))
	ct = [policy_str, C0, C1, C2, C3]
	output = ct
	return output

def decrypt(gpk, sk, ct):
	global attrs
	global policy
	global Y
	global coeff

	input = [gpk, sk, ct]
	g, g_2 = gpk
	policy_str, C0, C1, C2, C3 = ct
	gid, userS, K, deleteMeVar = sk
	policy = createPolicy(policy_str)
	attrs = prune(policy, userS)
	coeff = getCoefficients(policy)
	h_gid = group.hash(gid, G1)
	Y = len(attrs)
	A = dotprod2(range(0, Y), lam_func1, attrs, C1, h_gid, C3, K, C2, coeff)
	M = (C0 / A)
	output = M
	return output

