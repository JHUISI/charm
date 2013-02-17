#BGW
mskVars =  ['gamma']
rndVars =  []
sk  =  {'root': ['LEAF0'], 'LEAF0': ['gamma']}
skComplete  =  ['sk']

#BSW
mskVars =  ['beta', 'alpha']
rndVars =  ['r', 'sUSy']
sk  =  ['D', 'Djp', 'Dj']
Djp  =  {'root': ['LEAF0'], 'LEAF0': ['sUSy']}
Dj  =  {'root': ['ADD0'], 'ADD0': ['r', 'sUSy']}
D  =  {'MUL0': ['MUL1', 'ADD0'], 'MUL1': ['1', 'beta'], 'root': ['MUL0'], 'ADD0': ['alpha', 'r']}

#CKRS

#DFA

#DSE

#HIBE

#HVE

#LW

#SW05

#WATERS
