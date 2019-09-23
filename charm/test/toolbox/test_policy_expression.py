import unittest

from hypothesis import given

from charm.toolbox.policy_expression_spec import policy_expressions, assert_valid, alland_policy_expressions


class TestPolicyExpressionSpec(unittest.TestCase):

    @given(policy_expressions())
    def test_policy_expression_spec(self, policy_expression):
        assert_valid(policy_expression)

    @given(alland_policy_expressions())
    def test_allAND_policy_expressions(self, policy_expression):
        assert_valid(policy_expression)
