#!/bin/bash

export BD="$BD"
export NDK="$BD/android-ndk-r8e"
export HOST="arm-linux-androideabi"
export CFLAGS="--sysroot=$NDK/platforms/android-9/arch-arm -I$BD/obj/include -L$BD/obj/lib -L$NDK/platforms/android-9/arch-arm/usr/lib" 
export LDFLAGS="-L$NDK/platforms/android-9/arch-arm/usr/lib -L$BD/obj/lib"

# configure seems to ignore CFLAGS
export CC="arm-linux-androideabi-gcc $CFLAGS"

./configure --host=$HOST --target=$HOST --enable-shared --prefix=$BD/obj LDFLAGS="$LDFLAGS" && make && make install
