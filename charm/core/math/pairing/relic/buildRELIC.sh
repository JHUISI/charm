#!/bin/bash

set -x
#export VERBOSE=0
path_to_relic=$1
path_to_inc=/usr/local/include
path_to_lib=/usr/local/lib

relic_lib=lib
relic_inc=$path_to_relic/include


# handles both EC & EC w/ billinear maps
cmake -DVERBS=off -DDEBUG=off -DTRACE=off -DSHLIB=off -DWITH="ALL" -DCHECK=off -DARITH=easy -DBENCH=0 -DTESTS=0 -DSTBIN=off -DFP_METHD="BASIC;COMBA;COMBA;MONTY;LOWER;MONTY" -DFP_QNRES=off -DEC_METHD="PRIME" -DPC_METHD="PRIME" -DPP_METHD="INTEG;INTEG;LAZYR;OATEP" -DFP_PRIME=256 -DEP_KBLTZ=on -DALLOC=DYNAMIC -DBN_PRECI=256 -DCOMP="-O2 -funroll-loops -fomit-frame-pointer" $path_to_relic/

make
install -m 0644 $relic_lib/* $path_to_lib
install -m 0644 $relic_inc/*.h $path_to_inc
mkdir -p $path_to_inc/low
install -m 0644 $relic_inc/low/*.h $path_to_inc/low
set +x
