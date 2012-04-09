from userFuncs import *
from charm import *
from toolbox import *
from toolbox.pairinggroup import *
from toolbox.secretutil import SecretUtil
from schemes import *
from math import *
from charm.pairing import hash as SHA1

def transform(pk, sk, ct):
	input = [pk, sk, ct]
	policy_str, Ctl, C, Cr, Cpr, T1 = ct
	S, D, Dj, Djp = sk
	policy = createPolicy(policy_str)
	attrs = prune(policy, S)
	coeff = getCoefficients(policy)
	Y = len(attrs)
	lam_func1 = lambda a,b,c,d,e,f: (pair((b[a] ** c[a]), d[a]) * pair((e[a] ** c[a]), f[a]))
	A = dotprod2(range(attrs[1],Y), lam_func1, y, Cr, coeff, Dj, Djp, Cpr)
	result0 = (pair(C, D) * A)
	T0 = Ctl
	T2 = result0
	partCT = [T0, T1, T2]
	output = partCT
	return output

if __name__ == "__main__":
	global groupObj
	groupObj = PairingGroup('SS512')

	(partCT) = transform(sys.argv[1], sys.argv[2], sys.argv[3])
