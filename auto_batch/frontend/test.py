from charm.pairing import *
#from toolbox.PKSig import PKSig
group = pairing('/Users/matt/Documents/charm/param/a.param')
H1 = lambda x: group.H(('1', str(x)), G1)
ID = "bob"
msk = group.random(ZR)
sk = H1(ID) ** msk
(IDs, IDpk, IDsk) = sk
