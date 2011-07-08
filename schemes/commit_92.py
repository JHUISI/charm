from toolbox.Commit import *
from toolbox.ecgroup import *

debug = False
class CM_Ped92(Commitment):
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

def main():
    groupObj = ECGroup(410)
    if debug: print("hello world!");
    
#    cm = CM_Ped92(groupObj)
   
#    pk = cm.setup()
#    print("Public parameters...")
#    print("pk =>", pk)
    
#   m = groupObj.random()
#    print("Commiting to =>", m)
#    (c, d) = cm.commit(pk, m)
    
#    assert cm.decommit(pk, c, d, m), "FAILED to decommit"
#    print("Successful and Verified decommitment!!!")
   
      
if __name__ == "__main__":
    debug = True
    main()
