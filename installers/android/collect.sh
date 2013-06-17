#!/bin/bash
#the resulting out/python directory should be copied into the /res/raw directory in the eclipse workspace

BD="/home/charm/android-python27/android-python27/python-build-brandon-clean"

rm -r $BD/out

mkdir -p $BD/out/python/bin
cp $BD/android-python27/python-build/build/bin/python $BD/out/python/bin/python

cp -r $BD/android-python27/python-build/build/lib $BD/out/python/lib
cp $BD/obj/lib/*    $BD/out/python/lib

cp $BD/charm/dist/Charm_Crypto-*-py2.7-linux-armv.egg $BD/out/python/lib/python2.7/site-packages/


cd $BD/out/python/lib/python2.7/site-packages
unzip Charm_Crypto-*-py2.7-linux-armv.egg
rm -r EGG-INFO
rm -r Charm_Crypto-*-py2.7-linux-armv.egg

cd $BD/out
zip -r python_27.zip python
