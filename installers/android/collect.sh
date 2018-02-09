#!/bin/bash
#the resulting out/python directory should be copied into the /res/raw directory in the eclipse workspace

export BD="$BD"

rm -r $BD/out

mkdir -p $BD/out
cp -r $BD/android-python27/python-build/output/python/ $BD/out/
    cp -r $BD/android-python27/python-build/output/extras/python/* $BD/out/python/lib/python2.7/

cp $BD/obj/lib/*    $BD/out/python/lib

cp $BD/charm/dist/Charm_Crypto-*-py2.7-linux-armv.egg $BD/out/python/lib/python2.7/site-packages/


cd $BD/out/python/lib/python2.7/site-packages
unzip Charm_Crypto-*-py2.7-linux-armv.egg
rm -r EGG-INFO
rm -r Charm_Crypto-*-py2.7-linux-armv.egg

cd $BD/out
zip -r python_27.zip python
