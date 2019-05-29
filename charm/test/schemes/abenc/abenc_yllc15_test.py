import sys
import unittest

import pytest

from charm.toolbox.secretutil import SecretUtil

settings = pytest.importorskip("hypothesis").settings
given = pytest.importorskip("hypothesis").given
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
        (public_key, secret_key) = self.abe.ukgen(self.params)

    @pytest.mark.skipif(sys.version_info < (3, 4),
                        reason="requires python3.4 or higher")
    @given(attrs=lists(attributes(), min_size=1))
    @settings(deadline=300, max_examples=50)
    def test_proxy_key_gen_deduplicates_and_uppercases_attributes(self, attrs):
        pkcs, skcs = self.abe.ukgen(self.params)
        pku, sku = self.abe.ukgen(self.params)
        proxy_key_user = self.abe.proxy_keygen(self.params, self.msk, pkcs, pku, attrs)
        self.assertEqual({ attr.upper() for attr in set(attrs) }, proxy_key_user['k_attrs'].keys())

    @settings(deadline=500, max_examples=50)
    @given(policy_str=policy_expressions())
    def test_encrypt_proxy_decrypt_decrypt_round_trip(self, policy_str):
        pkcs, skcs = self.abe.ukgen(self.params)
        pku, sku = self.abe.ukgen(self.params)
        attrs = self.extract_attributes(policy_str)
        random_key_elem = self.abe.group.random(GT)

        proxy_key_user = self.abe.proxy_keygen(self.params, self.msk, pkcs, pku, attrs)
        ciphertext = self.abe.encrypt(self.params, random_key_elem, policy_str)
        intermediate_value = self.abe.proxy_decrypt(skcs, proxy_key_user, ciphertext)
        recovered_key_elem = self.abe.decrypt(None, sku, intermediate_value)
        self.assertEqual(random_key_elem, recovered_key_elem)

    def extract_attributes(self, policy_str):
        util = SecretUtil(self.abe.group)
        policy = util.createPolicy(policy_str)
        return [util.strip_index(policy_attr) for policy_attr in util.getAttributeList(policy)]

    @pytest.mark.skipif(sys.version_info < (3, 4),
                        reason="requires python3.4 or higher")
    @settings(deadline=400, max_examples=50)
    @given(policy=policy_expressions())
    def test_policy_not_satisfied(self, policy):
        pkcs, skcs = self.abe.ukgen(self.params)
        pku, sku = self.abe.ukgen(self.params)
        attribute_list = ["UNLIKELY_ATTRIBUTE_NAME"]
        proxy_key_user = self.abe.proxy_keygen(self.params, self.msk, pkcs, pku, attribute_list)

        random_key_elem = self.abe.group.random(GT)
        ciphertext = self.abe.encrypt(self.params, random_key_elem, policy)

        result = self.abe.proxy_decrypt(skcs, proxy_key_user, ciphertext)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()