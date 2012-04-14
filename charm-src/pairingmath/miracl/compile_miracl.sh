#!/bin/sh

# untar MIRACL source into this directory, then run this script 
# unzip -j -aa -L miracl.zip

rm -f *.exe
rm -f miracl.a
set -x
cp mirdef.hpp mirdef.h
g++ -c -m64 -O2 mrcore.c
g++ -c -m64 -O2 mrarth0.c
g++ -c -m64 -O2 mrarth1.c
g++ -c -m64 -O2 mrarth2.c
g++ -c -m64 -O2 mralloc.c
g++ -c -m64 -O2 mrsmall.c
g++ -c -m64 -O2 mrio1.c
g++ -c -m64 -O2 mrio2.c
g++ -c -m64 -O2 mrgcd.c
g++ -c -m64 -O2 mrjack.c
g++ -c -m64 -O2 mrxgcd.c
g++ -c -m64 -O2 mrarth3.c
g++ -c -m64 -O2 mrbits.c
g++ -c -m64 -O2 mrrand.c
g++ -c -m64 -O2 mrprime.c
g++ -c -m64 -O2 mrcrt.c
g++ -c -m64 -O2 mrscrt.c
g++ -c -m64 -O2 mrmonty.c
g++ -c -m64 -O2 mrpower.c
g++ -c -m64 -O2 mrsroot.c
g++ -c -m64 -O2 mrcurve.c
g++ -c -m64 -O2 mrfast.c
g++ -c -m64 -O2 mrshs.c
g++ -c -m64 -O2 mrshs256.c
g++ -c -m64 -O2 mrshs512.c
g++ -c -m64 -O2 mraes.c
g++ -c -m64 -O2 mrgcm.c
g++ -c -m64 -O2 mrlucas.c
g++ -c -m64 -O2 mrzzn2.c
g++ -c -m64 -O2 mrzzn2b.c
g++ -c -m64 -O2 mrzzn3.c
g++ -c -m64 -O2 mrecn2.c
g++ -c -m64 -O2 mrstrong.c
g++ -c -m64 -O2 mrbrick.c
g++ -c -m64 -O2 mrebrick.c
g++ -c -m64 -O2 mrec2m.c
g++ -c -m64 -O2 mrgf2m.c
g++ -c -m64 -O2 mrflash.c
g++ -c -m64 -O2 mrfrnd.c
g++ -c -m64 -O2 mrdouble.c
g++ -c -m64 -O2 mrround.c
g++ -c -m64 -O2 mrbuild.c
g++ -c -m64 -O2 mrflsh1.c
g++ -c -m64 -O2 mrpi.c
g++ -c -m64 -O2 mrflsh2.c
g++ -c -m64 -O2 mrflsh3.c
g++ -c -m64 -O2 mrflsh4.c
cp mrmuldv.g64 mrmuldv.c
g++ -c -m64 -O2 mrmuldv.c
g++ -c -m64 -O2 big.cpp
#g++ -c -m64 -O2 zzn2.cpp
#g++ -c -m64 -O2 zzn3.cpp
#g++ -c -m64 -O2 zzn6.cpp
#g++ -c -m64 -O2 zzn6a.cpp
g++ -c -m64 -O2 zzn.cpp
g++ -c -m64 -O2 ecn.cpp
#g++ -c -m64 -O2 ecn3.cpp
g++ -c -m64 -O2 ec2.cpp
g++ -c -m64 -O2 flash.cpp
g++ -c -m64 -O2 crt.cpp
# KSS curve
g++ -c -m64 -O2 kss_pair.cpp zzn18.cpp zzn6.cpp ecn3.cpp zzn3.cpp
# MNT curve
g++ -c -m64 -O2 mnt_pair.cpp zzn6a.cpp ecn3.cpp zzn3.cpp zzn2.cpp
# Cocks-Pinch curve
g++ -c -m64 -O2 cp_pair.cpp
# Barreto-Naehrig curve
g++ -c -m64 -O2 bn_pair.cpp
ar rc miracl.a mrcore.o mrarth0.o mrarth1.o mrarth2.o mralloc.o mrsmall.o mrzzn2.o mrzzn3.o
ar r miracl.a mrio1.o mrio2.o mrjack.o mrgcd.o mrxgcd.o mrarth3.o mrbits.o mrecn2.o
ar r miracl.a mrrand.o mrprime.o mrcrt.o mrscrt.o mrmonty.o mrcurve.o mrsroot.o mrzzn2b.o
ar r miracl.a mrpower.o mrfast.o mrshs.o mrshs256.o mraes.o mrlucas.o mrstrong.o mrgcm.o    
ar r miracl.a mrflash.o mrfrnd.o mrdouble.o mrround.o mrbuild.o
ar r miracl.a mrflsh1.o mrpi.o mrflsh2.o mrflsh3.o mrflsh4.o 
ar r miracl.a mrbrick.o mrebrick.o mrec2m.o mrgf2m.o mrmuldv.o mrshs512.o
#ar r miracl.a big.o zzn.o zzn2.o zzn3.o zzn6a.o ecn.o ecn3.o ec2.o flash.o crt.o mnt_pair.o 
#cp miracl.a miracl-mnt.a
cp miracl.a miracl-kss.a
ar r miracl.a big.o zzn.o zzn2.o zzn3.o zzn6a.o ecn.o ecn3.o ec2.o flash.o crt.o mnt_pair.o 
ar r miracl-kss.a big.o zzn.o zzn3.o zzn6.o zzn18.o ecn.o ecn3.o ec2.o flash.o crt.o kss_pair.o

rm mr*.o
#g++ -m64 -O2 bls_gen.cpp miracl.a -o bls_gen
#g++ -m64 -O2 bls_sign.cpp miracl.a -o bls_sign
#g++ -m64 -O2 bls_ver.cpp miracl.a -o bls_ver
#g++ -m64 -O2 bmark.c miracl.a -o bmark
#g++ -m64 -O2 fact.c miracl.a -o fact
#g++ -m64 -O2 mersenne.cpp miracl.a -o mersenne
#g++ -m64 -O2 brent.cpp miracl.a -o brent
#g++ -m64 -O2 sample.cpp miracl.a -o sample
#g++ -m64 -O2 ecsgen.cpp miracl.a -o ecsgen
#g++ -m64 -O2 ecsign.cpp miracl.a -o ecsign
#g++ -m64 -O2 ecsver.cpp miracl.a -o ecsver
#g++ -m64 -O2 pk-demo.cpp miracl.a -o pk-demo
#g++ -c -m64 -O2 polymod.cpp
#g++ -c -m64 -O2 poly.cpp
#g++ -m64 -O2 schoof.cpp polymod.o poly.o miracl.a -o schoof
set +x
