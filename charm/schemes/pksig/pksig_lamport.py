'''
Lamport's One-time Signature

| From: "L. Lamport. Constructing Digital Signatures from One Way Function"
| Published in: 1979
| Available: http://lamport.azurewebsites.net/pubs/dig-sig.pdf

*type:      signature(public key)

:Authors:   Jonas Thuresson & Martin Örndahl
:Date       03/2018
'''
from charm.toolbox.PKSig import PKSig
from hashlib import sha256
import os

byte_masks = [2 ** b for b in range(8)]
byte_masks.reverse()


def _h(x):
    return sha256(x).digest()


def _bytes_to_booleans(x):
    return [byte & mask != 0 for byte in x for mask in byte_masks]


class Lamport(PKSig):
    '''
    >>> sig = Lamport()
    >>> pk, sk = sig.keygen()
    >>> msg = 'hello'.encode('utf-8')
    >>> s = sig.sign(None, sk, msg)
    >>> assert sig.verify(pk, msg, s), "Signature could not be verified"
    '''

    def __init__(self):
        super().__init__()

    def keygen(self, securityparam=256):
        nbr_bytes = securityparam // 8
        sk = [(os.urandom(nbr_bytes), os.urandom(nbr_bytes)) for _ in range(securityparam)]
        pk = [(_h(i), _h(j)) for i, j in sk]
        return pk, sk

    def sign(self, pk, sk, message):
        msg_hash = _h(message)
        return [sk1 if not b else sk2 for ((sk1, sk2), b) in zip(sk, _bytes_to_booleans(msg_hash))]

    def verify(self, pk, message, sig):
        msg_hash = _h(message)
        expected = [pk1 if not b else pk2 for ((pk1, pk2), b) in zip(pk, _bytes_to_booleans(msg_hash))]
        return all([_h(s) == p for (s, p) in zip(sig, expected)])
