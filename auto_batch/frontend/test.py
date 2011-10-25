from charm.pairing import *
from toolbox.PKSig import PKSig
group = pairing('/Users/matt/Documents/Charm_From_Git/charm/param/a.param')
H2 = lambda x,y: group.H((x,y), ZR)
s = group.random(ZR)
pk = group.random(G1)
S1 = pk ** s
M = "string"
a = H2(M, S1)
