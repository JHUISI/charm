#!/bin/bash

export BD="$BD"
export NDK="$BD/android-ndk-r8e"

export HOST="arm-linux-androideabi"

export TC="$NDK/toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86"
export PATH="$TC/bin:$PATH"

export CFLAGS="--sysroot=$NDK/platforms/android-9/arch-arm"
export LDFLAGS="-L$NDK/platforms/android-9/arch-arm/usr/lib/"

# Work around toolchain ignoring platform location:
# http://stackoverflow.com/questions/6881164/crtbegin-so-o-missing-for-android-toolchain-custom-build
ln -s $NDK/platforms/android-9/arch-arm/usr/lib/crtbegin_so.o .
ln -s $NDK/platforms/android-9/arch-arm/usr/lib/crtend_so.o .

./configure --host=$HOST --target=$HOST --enable-shared --disable-assembly --prefix=$BD/obj && make && make install
