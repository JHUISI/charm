#!/bin/sh

# Note: this script might require super-user privileges to install
# binaries

# untar MIRACL source into this directory, then run this script 
set -x
[ -e miracl.zip ] && unzip -j -aa -L miracl.zip

# patch mnt_pair.cpp, ssp_pair.cpp, etc here
curve=$1

if [ $curve = "mnt" ]; then
   curve=mnt
   echo "Building MNT curve in miracl."
   patch -N < mnt_pair.patch
   rm -f *.rej
fi

if [ $curve = "bn" ]; then
   curve=bn
   echo "Building BN curve in miracl."
   patch -N < bn_pair.patch
   rm -f *.rej
fi

if [ $curve = "ss" ]; then
   curve=ss
   echo "Building SS curve in miracl."
   patch -N < pairing1.patch
   patch -N < ssp_pair.patch
   rm -f *.rej
fi

if [ -e miracl-$curve.a ]; then
    echo "Already built miracl-$curve" 
    exit 0
fi

# if length of string is zero
if [ -z $curve ]; then
   curve=mnt
   echo "Building default curve in miracl: $curve"
   patch -N < mnt_pair.patch  
fi


rm -f miracl.a
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
g++ -c -m64 -O2 mrzzn4.c
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
# Cocks-Pinch curve
#g++ -c -m64 -O2 cp_pair.cpp

ar rc miracl.a mrcore.o mrarth0.o mrarth1.o mrarth2.o mralloc.o mrsmall.o mrzzn2.o mrzzn3.o mrzzn4.o
ar r miracl.a mrio1.o mrio2.o mrjack.o mrgcd.o mrxgcd.o mrarth3.o mrbits.o mrecn2.o
ar r miracl.a mrrand.o mrprime.o mrcrt.o mrscrt.o mrmonty.o mrcurve.o mrsroot.o mrzzn2b.o
ar r miracl.a mrpower.o mrfast.o mrshs.o mrshs256.o mraes.o mrlucas.o mrstrong.o mrgcm.o    
ar r miracl.a mrflash.o mrfrnd.o mrdouble.o mrround.o mrbuild.o
ar r miracl.a mrflsh1.o mrpi.o mrflsh2.o mrflsh3.o mrflsh4.o 
ar r miracl.a mrbrick.o mrebrick.o mrec2m.o mrgf2m.o mrmuldv.o mrshs512.o

if [ $curve = "mnt" ]; then
   # MNT curve
   g++ -c -m64 -O2 mnt_pair.cpp zzn6a.cpp ecn3.cpp zzn3.cpp zzn2.cpp
   cp miracl.a miracl-mnt.a
   ar r miracl-mnt.a big.o zzn.o zzn2.o zzn3.o zzn6a.o ecn.o ecn3.o ec2.o flash.o crt.o mnt_pair.o
fi

if [ $curve = "bn" ]; then
   # Barreto-Naehrig curve
   g++ -c -m64 -O2 bn_pair.cpp zzn12a.cpp zzn4.cpp ecn2.cpp ecn3.cpp zzn2.cpp
   cp miracl.a miracl-bn.a
   ar r miracl-bn.a big.o zzn.o zzn2.o zzn4.o zzn12a.o ecn.o ecn2.o ecn3.o ec2.o flash.o crt.o bn_pair.o
fi

if [ $curve = "kss" ]; then
   # KSS curve
   g++ -c -m64 -O2 kss_pair.cpp zzn18.cpp zzn6.cpp ecn3.cpp zzn3.cpp
   cp miracl.a miracl-kss.a
   ar r miracl-kss.a big.o zzn.o zzn3.o zzn6.o zzn18.o ecn.o ecn3.o ec2.o flash.o crt.o kss_pair.o
fi

if [ $curve = "ss" ]; then
	# SS curve
	g++ -c -m64 -O2 ssp_pair.cpp 
	cp miracl.a miracl-ss.a
	ar r miracl-ss.a big.o ecn.o zzn.o zzn2.o ssp_pair.o
fi
#ln -sf miracl-$curve.a miracl.a
install -d /usr/local/include/miracl
install -d /usr/local/lib
install -m 0644 miracl-$curve.a /usr/local/lib
install -m 0644 *.h /usr/local/include/miracl

rm -f mr*.o *.a
set +x
