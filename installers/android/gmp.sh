#!/bin/bash

export BD="$BD"
export NDK="$BD/android-ndk-r8e"

export HOST="arm-linux-androideabi"

export PLATFORM="$NDK/platforms/android-9/arch-arm"
export SYSROOT=$PLATFORM
export TC="$NDK/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86"
export PATH="$TC/bin:$PATH"

#for some reason configure injects 'unknown' into the host prefix, so we manually select the compiler
export CC="$HOST-gcc" 

export CFLAGS="--sysroot=$SYSROOT"

./configure --host=$HOST --target=$HOST --enable-shared --disable-assembly --prefix=$BD/obj && make && make install
