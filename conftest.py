import sys

collect_ignore = []
if sys.version_info < (3, 4):
    collect_ignore.append("charm/toolbox/policy_expression_spec.py")
    collect_ignore.append("charm/test/toolbox/test_policy_expression.py")
    collect_ignore.append("charm/test/benchmark/abenc_yllc15_bench.py")