import sys

from charm.core.engine.util import objectToBytes
from charm.schemes.abenc.abenc_yllc15 import YLLC15
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.toolbox.policy_expression_spec import policy_expressions
from charm.toolbox.secretutil import SecretUtil


def run_keygen_encrypt_proxy_decrypt_decrypt_round_trip(policy_str):
    group = PairingGroup('SS512')
    abe = YLLC15(group)
    (params, msk) = abe.setup()
    pkcs, skcs = abe.ukgen(params)
    pku, sku = abe.ukgen(params)

    attrs = extract_attributes(group, policy_str)
    random_key_elem = abe.group.random(GT)

    start_bench(group)
    proxy_key_user = abe.proxy_keygen(params, msk, pkcs, pku, attrs)
    n = len(attrs)
    proxy_keygen_exec_time = end_bench(group, "proxy_keygen", n)
    proxy_key_size = len(objectToBytes(proxy_key_user, group))

    start_bench(group)
    ciphertext = abe.encrypt(params, random_key_elem, policy_str)
    encrypt_exec_time = end_bench(group, "encrypt", n)
    ciphertext_size = len(objectToBytes(ciphertext, group))

    start_bench(group)
    intermediate_value = abe.proxy_decrypt(skcs, proxy_key_user, ciphertext)
    proxy_decrypt_exec_time = end_bench(group, "proxy_decrypt", n)

    start_bench(group)
    recovered_key_elem = abe.decrypt(params, sku, intermediate_value)
    decrypt_exec_time = end_bench(group, "decrypt", n)

    assert random_key_elem == recovered_key_elem

    return {'policy_str': policy_str,
            'attrs': attrs,
            'attrs_vs_proxy_key_size': "# attributes(n) vs proxy key size(B),%d,%d" % (n, proxy_key_size),
            'policy_leave_vs_ciphertext_size': "# Policy leaf nodes (n) vs Ciphertext size (B),%d,%d" %
                                               (n, ciphertext_size),
            'proxy_keygen_exec_time': proxy_keygen_exec_time,
            'encrypt_exec_time': encrypt_exec_time,
            'proxy_decrypt_exec_time': proxy_decrypt_exec_time,
            'decrypt_exec_time': decrypt_exec_time
            }


def extract_attributes(group, policy_str):
    util = SecretUtil(group)
    policy = util.createPolicy(policy_str)
    return [util.strip_index(policy_attr) for policy_attr in util.getAttributeList(policy)]


def end_bench(group, operation, n):
    group.EndBenchmark()
    benchmarks = group.GetGeneralBenchmarks()
    cpu_time = benchmarks['CpuTime']
    real_time = benchmarks['RealTime']
    return "%s,%d,%f,%f" % (operation, n, cpu_time, real_time)


def start_bench(group):
    group.InitBenchmark()
    group.StartBenchmark(["RealTime", "CpuTime"])


if __name__ == '__main__':
    """
    Performance test for YLLC15
     
    :arg n: the input size n. Number of attributes or leaf nodes in policy tree.
    
    Example invocation:
    `$ python charm/test/benchmark/abenc_yllc15_bench.py 5`
    
    The technique:
    + uses an input generator to model the expected input data.
    + successively calls the algorithm under test with sample input data size 
      growing up n.
    + measures and returns performance stats.
    + prints the results in a "grep-able" format.
    """
    for n in range(1, int(sys.argv[1])):
        policy_str = policy_expressions(min_leaves=n, max_leaves=n).example()
        result = run_keygen_encrypt_proxy_decrypt_decrypt_round_trip(policy_str)
        print("function,n,CpuTime,RealTime")
        [print(v) for v in result.values()]
