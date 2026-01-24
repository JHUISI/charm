# Skip fuzzing files from pytest collection
# These require atheris to be installed and are meant to be run directly

collect_ignore = ["fuzz_policy_parser.py", "fuzz_serialization.py"]

