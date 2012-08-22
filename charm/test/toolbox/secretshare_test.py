from charm.toolbox.secretshare import SecretShare
from charm.toolbox.pairinggroup import PairingGroup,ZR
import unittest

debug=False

class SecretShareTest(unittest.TestCase):
    def testSecretShare(self):
        # Testing Secret sharing python API
          k = 3
          n = 4
          group = PairingGroup('SS512')

          s = SecretShare(group, False)
          sec = group.random(ZR)
          shares = s.genShares(sec, k, n)

          K = shares[0]
          if debug: print('\nOriginal secret: %s' % K)
          y = {group.init(ZR, 1):shares[1], group.init(ZR, 2):shares[2], group.init(ZR, 3):shares[3]}

          secret = s.recoverSecret(y)

          assert K == secret, "Could not recover the secret!"
          if debug: print("Successfully recovered secret: ", secret)

if __name__ == "__main__":
    unittest.main()
