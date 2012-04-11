from userFuncs import *
from toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from toolbox.secretutil import SecretUtil
from toolbox.symcrypto import AuthenticatedCryptoAbstraction
from toolbox.iterate import dotprod2
from charm.pairing import hash as SHA1

tau1b = {}
ga2 = {}
ga1 = {}
gb = {}
gba1 = {}
gba2 = {}
id = {}
tau2 = {}
tau1 = {}
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
ct = {}

def setup():
