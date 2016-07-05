from charm.toolbox.schemebase import *


class ABEncMultiAuth(SchemeBase):
    """
    Base class for attribute-based encryption multi-authority

     Notes: This class implements an interface for a standard attribute-based encryption scheme.

    A public key attribute-based encryption scheme consists of four algorithms:
    (setup, authsetup, keygen, encrypt, decrypt).
    """

    def __init__(self):
        SchemeBase.__init__(self)
        SchemeBase._setProperty(self, scheme='ABEncMultiAuth')
        self.baseSecDefs = None

    def setup(self):
        """
        Setup this multi-authority attribute based encryption scheme.
        :return: The result of the central setup, for example some global parameters.
        """
        raise NotImplementedError

    def authsetup(self, gp, object):
        """
        Setup an authority.
        :param gp: The global parameters of the scheme.
        :param object: Additional required arguments, for example a list of attributes or a name.
        :return: The result of the authority setup.
        """
        raise NotImplementedError

    def keygen(self, gp, sk, gid, object):
        """
        Generate user secret keys for attributes from a single authority.
        :param gp: The global parameters of the scheme.
        :param sk: The secret keys of the attribute authority.
        :param gid: Global identifier for the user.
        :param object: An attribute, list of attributes or access structure, depending on the scheme.
        :return: The secret keys for the user for the given attributes/access structure.
        """
        raise NotImplementedError

    def encrypt(self, gp, pk, m, object):
        """
        Encrypt a message.
        :param gp: The global parameters of the scheme.
        :param pk: The public keys of all relevant authorities.
        :param m: The message to encrypt.
        :param object: An access policy or a set of attributes to use.
        :return: The encrypted message.
        """
        raise NotImplementedError

    def decrypt(self, gp, sk, ct):
        """
        Decrypt a ciphertext.
        :param gp: The global parameters of the scheme.
        :param sk: The secret keys of the user.
        :param ct: The ciphertext to decrypt.
        :return: The plaintext.
        :raise Exception: Raised when the attributes do not satisfy the access policy.
        """
        raise NotImplementedError
