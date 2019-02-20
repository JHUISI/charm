import sys
import unittest

import pytest
from hypothesis import given
from hypothesis.strategies import lists

from charm.schemes.abenc.abenc_yllc15 import YLLC15
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.toolbox.policy_expression_spec import attributes, policy_expressions


class YLLC15Test(unittest.TestCase):

    def setUp(self):
        group = PairingGroup('SS512')
        self.abe = YLLC15(group)
        (self.params, self.msk) = self.abe.setup()

    def test_ukgen(self, user_id='bob@example.com'):
        (public_key, secret_key) = self.abe.ukgen(self.params, user_id)

    @pytest.mark.skipif(sys.version_info < (3, 4),
                        reason="requires python3.4 or higher")
    @given(attrs=lists(attributes(), min_size=1))
    def test_proxy_key_gen(self, attrs):
        pkcs, skcs = self.abe.ukgen(self.params, "aws@amazonaws.com")
        pku, sku = self.abe.ukgen(self.params, "alice@example.com")
        proxy_key_user = self.abe.proxy_keygen(self.params, self.msk, pkcs, pku, attrs)
        self.assertEqual(set(attrs), proxy_key_user['k_attrs'].keys())

    def test_encrypt_proxy_decrypt_decrypt_round_trip(self):
        pkcs, skcs = self.abe.ukgen(self.params, "aws@amazonaws.com")
        pku, sku = self.abe.ukgen(self.params, "alice@example.com")
        attribute_list = ["A"]
        proxy_key_user = self.abe.proxy_keygen(self.params, self.msk, pkcs, pku, attribute_list)

        random_key_elem = self.abe.group.random(GT)
        pol = '(A)'
        ciphertext = self.abe.encrypt(self.params, random_key_elem, pol)

        intermediate_value = self.abe.proxy_decrypt(self.params, skcs, proxy_key_user, ciphertext)
        recovered_key_elem = self.abe.decrypt(self.params, sku, intermediate_value)
        self.assertEqual(random_key_elem, recovered_key_elem)

    @pytest.mark.skipif(sys.version_info < (3, 4),
                        reason="requires python3.4 or higher")
    @given(policy=policy_expressions())
    def test_policy_not_satisfied(self, policy):
        pkcs, skcs = self.abe.ukgen(self.params, "aws@amazonaws.com")
        pku, sku = self.abe.ukgen(self.params, "alice@example.com")
        attribute_list = ["UNLIKELY_ATTRIBUTE_NAME"]
        proxy_key_user = self.abe.proxy_keygen(self.params, self.msk, pkcs, pku, attribute_list)

        random_key_elem = self.abe.group.random(GT)
        ciphertext = self.abe.encrypt(self.params, random_key_elem, policy)

        result = self.abe.proxy_decrypt(self.params, skcs, proxy_key_user, ciphertext)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()