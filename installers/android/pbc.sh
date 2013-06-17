#!/bin/bash

#replace config.sub and config.guess from http://git.savannah.gnu.org/gitweb/?p=config.git;a=tree
#TODO, confirm the above is nessasary

export BD="/home/charm/android-python27/android-python27/python-build-brandon-clean"
export NDK="$BD/android-ndk-r8e"

export HOST="arm-linux-androideabi"

export PLATFORM="$NDK/platforms/android-9/arch-arm"
export SYSROOT=$PLATFORM
export TC="$NDK/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86"
export PATH="$TC/bin:$PATH"

#for some reason configure injects 'unknown' into the host prefix, so we manually select the compiler
export CC="$HOST-gcc " 
export CFLAGS="--sysroot=$SYSROOT -I$BD/obj/include" 
export CC="$CC $CFLAGS" #configure seems to ignore CFLAGS
 
export LDFLAGS="-L$PLATFORM/usr/lib/"

./configure --host=$HOST --enable-shared --prefix=$BD/obj LDFLAGS="$LDFLAGS -L$BD/obj/lib" && make && make install
