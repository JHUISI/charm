from charm.toolbox.ecgroup import ECGroup,ZR,G
from charm.toolbox.Commit import Commitment

debug = False
class CM_Ped92(Commitment):
    """
    >>> group = ECGroup(410)    
    >>> alg = CM_Ped92(group)
    >>> public_key = alg.setup()
    >>> msg = group.random(ZR)
    >>> (commit, decommit) = alg.commit(public_key, msg)
    >>> alg.decommit(public_key, commit, decommit, msg)
    True
    """
    def __init__(self, groupObj):
        Commitment.__init__(self)
        global group
        group = groupObj

    def setup(self, secparam=None):
        return {'g': group.random(G), 'h':group.random(G)}

    def commit(self, pk, msg):
        r = group.random(ZR)
        c = (pk['g'] ** msg) * (pk['h'] ** r)
        d = r
        return (c,d)

    def decommit(self, pk, c, d, msg):
        return c == (pk['g'] ** msg) * (pk['h'] ** d)

