from toolbox.PKSig import PKSig
from toolbox.iterate import dotprod
from toolbox.pairinggroup import PairingGroup,G1,G2,GT,ZR,pair
import sys

group = None
debug = None
H1 = None
H2 = None
lam_func = None
bodyKey = 'Body'


def __init__( groupObj ) : 
	global group , debug 
	group = groupObj 
	debug = False 

def concat( L_id ) : 
	result = "" 
	for i in L_id : 
		result + = ":" + i 
	return result 

