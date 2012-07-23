#!/bin/bash

set -x
export VERBOSE=0
path_to_relic=$1

# handles both EC & EC w/ billinear maps
cmake -DVERBS=on -DDEBUG=off -DTRACE=off -DSHLIB=off -DWITH="ALL" -DCHECK=on -DARITH=easy -DBENCH=0 -DTEST=0 -DSTBIN=off -DFP_METHD="BASIC;COMBA;COMBA;MONTY;LOWER;SLIDE" -DFP_QNRES=on -DEC_METHD="PRIME" -DPC_METHD="PRIME" -DPP_METHD="INTEG;INTEG;LAZYR;OATEP" -DFP_PRIME=254 -DEP_KBLTZ=on -DALLOC=DYNAMIC -DBN_PRECI=256 -DCOMP="-O2 -funroll-loops -fomit-frame-pointer" $path_to_relic/

make
set +x
