"""Regression coverage for the policy/parser and decorator reports in bugs/."""
import pytest
from pyparsing import ParseBaseException

from charm.toolbox.policytree import PolicyParser
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.msp import MSP
from charm.toolbox.schemebase import Input
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.schemes.abenc.abenc_yllc15 import YLLC15


@pytest.mark.parametrize('policy', ['A and B)', 'A and', 'and B', 'A and and B',
                                    'A or', 'or A', '(A', '', 'A B', 'A or or B'])
def test_reject_incomplete_policy(policy):
    with pytest.raises(ParseBaseException):
        PolicyParser().parse(policy)
    # A failed parse must not poison the next call.
    assert str(PolicyParser().parse('A and B')) == '(A and B)'


@pytest.mark.parametrize('attribute', ['attr_x', 'team_role_admin', 'attr_12_name'])
def test_underscore_attribute_roundtrip(attribute):
    group = PairingGroup('BN254')
    for utility in (SecretUtil(group), MSP(group)):
        tree = utility.createPolicy(f'{attribute} and {attribute}')
        labels = utility.getAttributeList(tree)
        assert labels == [attribute.upper() + '_0', attribute.upper() + '_1']
        assert [utility.strip_index(label) for label in labels] == [attribute.upper()] * 2
    scheme = CPabe_BSW07(group)
    pk, mk = scheme.setup()
    sk = scheme.keygen(pk, mk, [attribute.upper()])
    message = group.random(GT)
    ct = scheme.encrypt(pk, message, f'{attribute} and {attribute}')
    assert scheme.decrypt(pk, sk, ct) == message


@pytest.mark.parametrize('error', [ValueError('hi'), TimeoutError({1: 2}),
                                   KeyError('missing'), TypeError('inside function')])
def test_input_propagates_function_errors(error, capsys):
    @Input()
    def throw(exc):
        raise exc
    with pytest.raises(type(error)) as caught:
        throw(error)
    assert caught.value is error
    assert capsys.readouterr().out == ''


def test_input_validates_keywords_and_preserves_metadata():
    class Scheme:
        @Input(int)
        def method(self, number=1):
            """A typed method."""
            return number
    assert Scheme().method(number=3) == 3
    assert Scheme().method() == 1
    assert Scheme.method.__name__ == 'method'
    with pytest.raises(TypeError):
        Scheme().method(number='wrong')


@pytest.mark.parametrize('scheme_type', [CPabe_BSW07, YLLC15])
def test_decorated_encrypt_reports_parse_error(scheme_type):
    group = PairingGroup('BN254')
    scheme = scheme_type(group)
    pk, _ = scheme.setup()
    with pytest.raises(ParseBaseException):
        scheme.encrypt(pk, group.random(GT), 'A and')


@pytest.mark.parametrize('attribute', ['AND-role', 'OR.name', 'anderson', 'origin'])
def test_operator_prefix_is_valid_attribute(attribute):
    assert PolicyParser().parse(attribute).getAttribute() == attribute.upper()


def test_policy_tree_type_tag_does_not_change_plain_strings():
    from charm.core.engine.util import objectToBytes, bytesToObject
    group = PairingGroup('BN254')
    value = {'text': 'policy:A and B',
             'tree': PolicyParser().parse('A_0 and (!B or A_1)')}
    restored = bytesToObject(objectToBytes(value, group), group)
    assert restored['text'] == value['text']
    assert str(restored['tree']) == str(value['tree'])
    assert restored['tree'].getLeft().index == 0
    assert restored['tree'].getRight().getLeft().negated
