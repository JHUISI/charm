'''
Cramer-Shoup Public Key Encryption Scheme (Decisional Diffie-Hellman Assumption in groups of prime order)
 
| From: "R. Cramer, V. Shoup: A practical public key cryptosystem provably secure against adaptive chosen ciphertext attack"
| Published in: CRYPTO 1998
| Available from: http://knot.kaist.ac.kr/seminar/archive/46/46.pdf
| Notes: 

* type:			encryption (public key)
* setting:		DDH-hard EC groups of prime order (F_p) or Integer Groups
* assumption:	DDH
* Name:         PKEnc_DDH_CCA_CS98

:Authors:	Matthew Green
:Date:			1/2011


'''
from charm.toolbox.ecgroup import G
from charm.toolbox.PKEnc import PKEnc

# type definitions
#pk_t = { 'g1' : G, 'g2' : G, 'c' : G, 'd' : G, 'h' : G }
#sk_t = { 'x1' : ZR, 'x2' : ZR, 'y1' : ZR, 'y2' : ZR, 'z' : ZR }
#c_t = { 'u1' : G, 'u2' : G, 'e' : G, 'v' : G }
#str_t = str

debug = False
class CS98(PKEnc):	
    """
    >>> from charm.toolbox.eccurve import prime192v1
    >>> from charm.toolbox.ecgroup import ECGroup
    >>> groupObj = ECGroup(prime192v1)
    >>> pkenc = CS98(groupObj)
    >>> (public_key, secret_key) = pkenc.keygen()
    >>> msg = b"hello world!!!123456"
    >>> cipher_text = pkenc.encrypt(public_key, msg)
    >>> decrypted_msg = pkenc.decrypt(public_key, secret_key, cipher_text)
    >>> decrypted_msg == msg
    True
    >>> from charm.toolbox.integergroup import IntegerGroup, integer
    >>> p = integer(156053402631691285300957066846581395905893621007563090607988086498527791650834395958624527746916581251903190331297268907675919283232442999706619659475326192111220545726433895802392432934926242553363253333261282122117343404703514696108330984423475697798156574052962658373571332699002716083130212467463571362679)
    >>> q = integer(78026701315845642650478533423290697952946810503781545303994043249263895825417197979312263873458290625951595165648634453837959641616221499853309829737663096055610272863216947901196216467463121276681626666630641061058671702351757348054165492211737848899078287026481329186785666349501358041565106233731785681339)
    >>> groupObj = IntegerGroup()
    >>> pkenc = CS98(groupObj, p, q)
    >>> (public_key, secret_key) = pkenc.keygen(1024)
    >>> msg = b"hello world. test message"
    >>> cipher_text = pkenc.encrypt(public_key, msg)
    >>> decrypted_msg = pkenc.decrypt(public_key, secret_key, cipher_text)
    >>> decrypted_msg == msg
    True
    """
    def __init__(self, groupObj, p=0, q=0):
        PKEnc.__init__(self)
        global group
        group = groupObj
        if group.groupSetting() == 'integer':
            group.p, group.q, group.r = p, q, 2

#    @output(pk_t, sk_t)
    def keygen(self, secparam=0):
        if group.groupSetting() == 'integer':
            if group.p == 0 or group.q == 0:
                group.paramgen(secparam)
            p = group.p
            g1, g2 = group.randomGen(), group.randomGen()
        elif group.groupSetting() == 'elliptic_curve':
            group.paramgen(secparam)
            g1, g2 = group.random(G), group.random(G)
        
        x1, x2, y1, y2, z = group.random(), group.random(), group.random(), group.random(), group.random()		
        c = ((g1 ** x1) * (g2 ** x2))
        d = ((g1 ** y1) * (g2 ** y2)) 
        h = (g1 ** z)
		
        pk = { 'g1' : g1, 'g2' : g2, 'c' : c, 'd' : d, 'h' : h }
        sk = { 'x1' : x1, 'x2' : x2, 'y1' : y1, 'y2' : y2, 'z' : z }
        return (pk, sk)

#    @input(pk_t, bytes)
#    @output(c_t)
    def encrypt(self, pk, M):
        r     = group.random()
        u1    = (pk['g1'] ** r)
        u2    = (pk['g2'] ** r)
        e     = group.encode(M) * (pk['h'] ** r)
        alpha = group.hash((u1, u2, e))
        v     = (pk['c'] ** r) * (pk['d'] ** (r * alpha))		
		# Assemble the ciphertext
                
        c = { 'u1' : u1, 'u2' : u2, 'e' : e, 'v' : v }
        return c
    
#    @input(pk_t, sk_t, c_t)
#    @output(bytes)
    def decrypt(self, pk, sk, c):
        alpha = group.hash((c['u1'], c['u2'], c['e']))
        v_prime = (c['u1'] ** (sk['x1'] + (sk['y1'] * alpha))) * (c['u2'] ** (sk['x2'] + (sk['y2'] * alpha)))
        if (c['v'] != v_prime):
            return 'ERROR' 

        if debug: print("c['v'] => %s" % c['v'])
        if debug: print("v' => %s" % v_prime)
        return group.decode(c['e'] / (c['u1'] ** sk['z']))

