from toolbox.Commit import *
from toolbox.ecgroup import *

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

if __name__ == "__main__":
   groupObj = ECGroup(410)
   
   cm = CM_Ped92(groupObj)
   
   pk = cm.setup()
   
   m = groupObj.random()
   print("Commiting to =>", m)
   (c, d) = cm.commit(pk, m)

   if cm.decommit(pk, c, d, m):
      print("Successful and Verified decommitment!!!")
   else:
      print("FAILED to decommit") 
