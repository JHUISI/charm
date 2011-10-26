from charm.pairing import *
from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
group = pairing('/Users/matt/Documents/charm/param/a.param')
L = [ "alice", "bob", "carlos", "dexter", "eddie"] 
num_signers = len(L)
u = [group.init(G1) for i in range(num_signers)]
