import sys

collect_ignore = []
if sys.version_info < (3, 4):
    collect_ignore.append("charm/toolbox/policy_expression_spec.py")
    collect_ignore.append("charm/toolbox/test_policy_expression.py")