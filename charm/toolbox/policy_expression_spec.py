from hypothesis.strategies import text, composite, sampled_from, characters, one_of, integers


def policy_expressions(min_leaves=1, max_leaves=25):
    return integers(min_leaves, max_leaves).flatmap(policy_expressions_of_size)


def policy_expressions_of_size(num_leaves):
    if num_leaves == 1:
        return one_of(attributes(), inequalities())
    else:
        return policy_expression(num_leaves)


@composite
def policy_expression(draw, num_leaves):
    left_leaves = draw(integers(min_value=1, max_value=num_leaves - 1))
    right_leaves = num_leaves - left_leaves
    left = draw(policy_expressions_of_size(left_leaves))
    right = draw(policy_expressions_of_size(right_leaves))
    gate = draw(gates())
    return u'(' + u' '.join((left, gate, right)) + u')'


def attributes():
    return text(min_size=1, alphabet=characters(whitelist_categories='L', max_codepoint=0x7e))


@composite
def inequalities(draw):
    attr = draw(attributes())
    oper = draw(inequality_operators())
    numb = draw(integers(min_value=1))
    return u' '.join((attr, oper, str(numb)))


def inequality_operators():
    return sampled_from((u'<', u'>', u'<=', u'>='))


def gates():
    return sampled_from((u'or', u'and'))


def assert_valid(policy_expression):
    assert policy_expression  # not empty
    assert policy_expression.count(u'(') == policy_expression.count(u')')
