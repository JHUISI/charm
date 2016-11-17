#!/usr/bin/env python

# This build_config.py was adapted from a testing script in the RELIC source (tools/test_all.py)

import subprocess
import sys
import traceback
import os
import multiprocessing
import argparse

configurations = []
debug = True

# Building functions
def prepare_configuration(build_dir):
    if subprocess.call(["mkdir", "-p", build_dir]):
        raise ValueError("Preparation of build folder failed.")
    os.chdir(build_dir)

def config_configuration(config, build_dir, relic_target):
    args = ["cmake"]
    args.extend(config['build'])
    #args.extend([".."])
    args.extend(["../" + relic_target]) # because we've changed dir into build/
    if debug: print("config_configuration: ", args)
    if subprocess.call(args):
        raise ValueError("CMake configuration failed.")

def build_configuration(build_dir):
    args = ["make", "-j", str(multiprocessing.cpu_count()), "install"]
    if debug: print("build_configuration: ", args)
    if subprocess.call(args):
        raise ValueError("Building failed.")

def test_configuration(config):
    args = ["ctest", "--output-on-failure", "-j", str(multiprocessing.cpu_count())]
    args.extend(config['test'])
    if subprocess.call(args):
        print("Tests failed: %s" % config["build"])

def clean_configuration(build_dir):
    os.chdir("..")
    if subprocess.call(["rm", "-rf", build_dir]):
        raise ValueError("Cleaning build directory failed.")

def conf_build_test_clean(config, relic_target):
    build_dir = "build_" + config['label']
    try:
        prepare_configuration(build_dir)
        config_configuration(config, build_dir, relic_target)
        build_configuration(build_dir)
        test_configuration(config)
    except Exception as e:
        print("Build failed: ", str(config), e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
    clean_configuration(build_dir)



# Setup configurations
def extend_default_config(extension, test_num):
    default_conf = [
        '-DSEED=ZERO',
        '-DBENCH=0',
        '-DCHECK=off',
        '-DVERBS=off',
        '-DDEBUG=off',
        '-DMULTI=PTHREAD',
        '-DARITH=gmp',
        '-DTESTS=' + str(test_num)
    ]
    default_conf.extend(extension)
    return default_conf

# TODO: provide explanation here
BP_LABEL = 'bn'
SS_LABEL = 'ss'
#EC_LABEL = 'ec'
LABEL_OPTIONS = [BP_LABEL, SS_LABEL]
CURVE_SIZES = {BP_LABEL: ['254', '256'],
               SS_LABEL: ['1536']}
               #EC_LABEL: ['256', '384', '512']}

# get input
parser = argparse.ArgumentParser(description="RELIC config for multiple pairings curves")
parser.add_argument('--src', help="Rel path to RELIC source directory", required=True)
parser.add_argument('-p', '--prefix', help="Location to install static/shared libs", required=True)
parser.add_argument('-c', '--curves', help="Pick curve configs to build. options: ['bn', 'ss']", required=True)
parser.add_argument('-s', '--size', help="Curve sizes. For bn = ['254', '256', '512'], For ss = ['1536'], For NIST ec = ['256', '384', '512']", default=None)
parser.add_argument('-a', '--arch', help="32 or 64-bit architectures", default=64)
parser.add_argument('-t', '--test', help="Build tests and run them", default=False, action="store_true")
parser.add_argument('-v', '--verbose', help="Enable verbose mode", default=False, action="store_true")

# parse the provided arguments
args = parser.parse_args()
prefix_path = args.prefix
label = args.curves
relic_src = args.src
debug = args.verbose
test = args.test
if label not in LABEL_OPTIONS:
    parser.print_help()
    sys.exit("\n*** Invalid curve type. Options are %s ***" % str(LABEL_OPTIONS))
if relic_src is None:
    parser.print_help()
    sys.exit("\n*** Missing Argument. Did not provide RELIC source dir path ***")

if test:
    test_num = 1
else:
    test_num = 0

# test Relic standard configuration
#configurations.append({'build': extend_default_config([]), 'test': ['-E', 'test_bn|test_fpx']})

# test ECC configurations
# test BN-CURVE config
if label == BP_LABEL: # Type-III
    if args.size is not None and args.size in CURVE_SIZES.get(BP_LABEL):
        size = args.size
    else:
        size = '254' # default
        # note: by default, BN_PRECI=1024 (or base precision in bits)
    configurations.append({'build':
        extend_default_config(['-DFP_PRIME=' + size, "-DWITH='BN;DV;FP;FPX;EP;EPX;PP;PC;MD'", "-DEC_METHD='PRIME'",
                               "-DARCH='X64'", "-DEP_METHD='PROJC;LWNAF;COMBS;INTER'", "-DCMAKE_INSTALL_PREFIX:PATH={prefix}".format(prefix=prefix_path),
                               "-DFP_QNRES=off", "-DFP_METHD='BASIC;COMBA;COMBA;MONTY;LOWER;SLIDE'", "-DFPX_METHD='INTEG;INTEG;LAZYR'",
                               "-DPP_METHD='LAZYR;OATEP'", "-DRAND='CALL'", "-DLABEL='{label}'".format(label=BP_LABEL + size),
                               "-DCOMP='-O2 -funroll-loops -fomit-frame-pointer -Wno-unused-function -Wno-implicit-function-declaration "
                               "-Wno-incompatible-pointer-types-discards-qualifiers'"], test_num),
                           'test': ['-E', 'test_bn|test_fb|test_fpx|test_pc'], 'label': BP_LABEL + size})

elif label == SS_LABEL: # Type-I
    if args.size is not None and args.size in CURVE_SIZES.get(SS_LABEL):
        size = args.size
    else:
        size = '1536' # default
    configurations.append({'build':
        extend_default_config(['-DFP_PRIME=' + size, "-DBN_PRECI=" + size, "-DWITH='BN;DV;FP;FPX;EP;EPX;PP;PC;MD'", "-DEC_METHD='PRIME'",
                               "-DARCH='X64'", "-DEP_METHD='PROJC;LWNAF;COMBS;INTER'", "-DCMAKE_INSTALL_PREFIX:PATH={prefix}".format(prefix=prefix_path),
                               "-DFP_QNRES=off", "-DFP_METHD='BASIC;COMBA;COMBA;MONTY;LOWER;SLIDE'", "-DFPX_METHD='INTEG;INTEG;LAZYR'",
                               "-DPP_METHD='LAZYR;OATEP'", "-DRAND='CALL'", "-DLABEL='{label}'".format(label=SS_LABEL + size),
                               "-DCOMP='-O2 -funroll-loops -fomit-frame-pointer -Wno-unused-function -Wno-implicit-function-declaration "
                               "-Wno-incompatible-pointer-types-discards-qualifiers'"], test_num),
                           'test': ['-E', 'test_bn|test_fb|test_fpx|test_pc'], 'label': SS_LABEL + size})
else:
    pass # not reachable so don't care

for config in configurations:
    if debug: print("CONFIGURATION: ", config)
    conf_build_test_clean(config, relic_src)
